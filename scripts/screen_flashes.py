#!/usr/bin/env python3
"""Screen a video for flashing that could breach WCAG 2.3.1 (three flashes per second).

A FLAG-ONLY screen. It can tell you a video has a problem. It cannot tell you a video is
safe: it samples a 16 x 16 grid, so small or fine-detailed flicker can slip through, and it
does not replace a PEAT / Harding (ITU-R BT.1702) analysis for broadcast or paid media.

Method, following the WCAG definitions:
  general flash  a pair of opposing changes in relative luminance of 10% or more of full
                 scale, where the darker state is below 0.80
  red flash      a pair of opposing transitions involving a saturated red
                 (R/(R+G+B) >= 0.8) where (R-G-B) x 320 changes by more than 20
  limit          more than three flashes inside any one-second window
  area           flagged only when at least about 3% of the frame flashes together
                 (the WCAG small-area allowance is roughly 25% of a 10-degree field)

Needs ffmpeg and ffprobe on PATH.

Usage:
  python screen_flashes.py final.mp4

Exit codes: 0 nothing flagged (not a clearance), 1 flagged, 2 file or tool problem. Output is JSON.
"""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

GRID = 16
MAX_FLASHES = 3
MIN_AREA_FRACTION = 0.0278
NOTE = ("Flag-only screen on a 16x16 grid: a clean result is not a clearance. "
        "Run PEAT or a Harding test before broadcast or paid placement of strobing content.")

_LIN = [(c / 255.0) / 12.92 if c / 255.0 <= 0.04045 else ((c / 255.0 + 0.055) / 1.055) ** 2.4 for c in range(256)]


def transitions(series, min_delta=0.10, dark_ceiling=0.80):
    """Frame indexes where the series completes a qualifying swing, alternating up/down."""
    if not series:
        return []
    events, ref, direction = [], series[0], 0
    for i in range(1, len(series)):
        v = series[i]
        if direction == 0:
            dark_ok = dark_ceiling is None or min(v, ref) < dark_ceiling
            if abs(v - ref) >= min_delta and dark_ok:
                direction = 1 if v > ref else -1
                events.append(i)
                ref = v
        elif direction == 1:
            if v > ref:
                ref = v
            elif ref - v >= min_delta and (dark_ceiling is None or v < dark_ceiling):
                direction, ref = -1, v
                events.append(i)
        else:
            if v < ref:
                ref = v
            elif v - ref >= min_delta and (dark_ceiling is None or ref < dark_ceiling):
                direction, ref = 1, v
                events.append(i)
    return events


def _flashes_per_window(events, n_frames, fps):
    """For each window start frame, flashes (pairs of opposing transitions) in the next second."""
    window = max(1, int(round(fps)))
    counts, lo, hi = [0] * n_frames, 0, 0
    for start in range(n_frames):
        while lo < len(events) and events[lo] < start:
            lo += 1
        while hi < len(events) and events[hi] < start + window:
            hi += 1
        counts[start] = (hi - lo) // 2
    return counts


def max_flashes_per_second(series, fps, min_delta=0.10, dark_ceiling=0.80):
    counts = _flashes_per_window(transitions(series, min_delta, dark_ceiling), len(series), fps)
    return max(counts, default=0)


def screen_cells(cell_series, fps, min_delta=0.10, dark_ceiling=0.80, min_area_fraction=MIN_AREA_FRACTION):
    """cell_series: one luminance series per grid cell. Flag when enough cells flash together."""
    n_cells = len(cell_series)
    n_frames = len(cell_series[0]) if n_cells else 0
    need = max(1, math.ceil(min_area_fraction * n_cells))
    over = [0] * n_frames
    worst = 0
    for series in cell_series:
        counts = _flashes_per_window(transitions(series, min_delta, dark_ceiling), n_frames, fps)
        for i, c in enumerate(counts):
            if c > MAX_FLASHES:
                over[i] += 1
        worst = max(worst, max(counts, default=0))
    windows, start = [], None
    for i, n in enumerate(over + [0]):
        if n >= need and start is None:
            start = i
        elif n < need and start is not None:
            windows.append({"start_s": round(start / fps, 2), "end_s": round((i - 1) / fps + 1.0, 2),
                            "cells_flashing": max(over[start:i])})
            start = None
    return {"flagged": bool(windows), "max_flashes_per_second": worst, "cells_needed": need,
            "flagged_windows": windows[:10]}


def _fps(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=avg_frame_rate", "-of", "csv=p=0", video], capture_output=True, text=True)
    num, _, den = out.stdout.strip().partition("/")
    try:
        return float(num) / float(den or 1)
    except (ValueError, ZeroDivisionError):
        return 30.0


def read_cells(video):
    """Decode to a GRID x GRID RGB thumbnail per frame; return (luminance series, red series) per cell."""
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", video, "-an",
                           "-vf", f"scale={GRID}:{GRID}:flags=area,format=rgb24", "-f", "rawvideo", "-"],
                          capture_output=True)
    if proc.returncode != 0:
        raise ValueError(f"ffmpeg failed: {proc.stderr.decode(errors='replace').strip()[:300]}")
    raw, cells, frame_bytes = proc.stdout, GRID * GRID, GRID * GRID * 3
    n_frames = len(raw) // frame_bytes
    lum = [[0.0] * n_frames for _ in range(cells)]
    red = [[0.0] * n_frames for _ in range(cells)]
    for f in range(n_frames):
        base = f * frame_bytes
        for c in range(cells):
            o = base + c * 3
            r, g, b = _LIN[raw[o]], _LIN[raw[o + 1]], _LIN[raw[o + 2]]
            lum[c][f] = 0.2126 * r + 0.7152 * g + 0.0722 * b
            total = r + g + b
            if total > 0 and r / total >= 0.8:
                red[c][f] = max(0.0, r - g - b) * 320.0
    return lum, red, n_frames


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video")
    args = ap.parse_args(argv)
    if not Path(args.video).is_file():
        print(json.dumps({"error": f"file not found: {args.video}"}))
        return 2
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print(json.dumps({"error": "ffmpeg and ffprobe must be on PATH; this check is pending until they are"}))
        return 2
    try:
        fps = _fps(args.video)
        lum, red, n_frames = read_cells(args.video)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    general = screen_cells(lum, fps)
    saturated_red = screen_cells(red, fps, min_delta=20.0, dark_ceiling=None)
    flagged = general["flagged"] or saturated_red["flagged"]
    print(json.dumps({"flagged": flagged, "limit_flashes_per_second": MAX_FLASHES, "fps": round(fps, 3),
                      "frames": n_frames, "grid": f"{GRID}x{GRID}", "general": general,
                      "saturated_red": saturated_red, "note": NOTE}, indent=2))
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
