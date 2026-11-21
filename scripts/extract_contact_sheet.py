#!/usr/bin/env python3
"""Export contact sheets from a video so the hierarchy audits can be done by eye.

Writes four PNGs (needs ffmpeg and ffprobe on PATH):
  <prefix>_color.png      evenly spaced frames across the WHOLE video
  <prefix>_grayscale.png  same frames with colour removed: does hierarchy survive without hue?
  <prefix>_squint.png     same frames blurred: does the intended focal element still dominate?
  <prefix>_hook.png       frames at 0.0, 0.5, 1.5 and 3.0 s: is frame 0 a hard cut to something
                          readable on mute, and is the promise clear by 3 s?

The script only produces the images. Look at them (open them with your image viewer or
Read tool) and record what you see; an unopened contact sheet is not a completed check.

Usage:
  python extract_contact_sheet.py final.mp4 --prefix out/audit
  python extract_contact_sheet.py final.mp4 --cols 5 --rows 4 --tile-width 320

Exit codes: 0 written, 2 file or tool problem. Output is JSON listing the files.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HOOK_TIMES = (0.0, 0.5, 1.5, 3.0)


def plan_grid(duration_s, cols=4, rows=3):
    """Pick a sampling rate so cols x rows tiles span the full duration."""
    tiles = cols * rows
    return {"tiles": tiles, "fps": tiles / max(duration_s, 1e-3)}


def _duration(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        raise ValueError(f"could not read the duration of {video}: {out.stderr.strip()[:200]}") from None


def _run(args):
    done = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args],
                          capture_output=True, text=True)
    if done.returncode != 0:
        raise ValueError(f"ffmpeg failed: {done.stderr.strip()[:300]}")


def export_sheets(video, prefix, cols=4, rows=3, tile_width=360):
    duration = _duration(video)
    plan = plan_grid(duration, cols, rows)
    Path(prefix).parent.mkdir(parents=True, exist_ok=True)
    base = f"fps={plan['fps']:.6f},scale={tile_width}:-2"
    variants = {"color": base, "grayscale": base + ",format=gray", "squint": base + ",gblur=sigma=8"}
    files = {}
    for label, chain in variants.items():
        files[label] = f"{prefix}_{label}.png"
        _run(["-i", video, "-vf", f"{chain},tile={cols}x{rows}", "-frames:v", "1", files[label]])

    times = [t for t in HOOK_TIMES if t < duration - 0.05] or [0.0]
    files["hook"] = f"{prefix}_hook.png"
    inputs = []
    for t in times:
        inputs += ["-ss", f"{t}", "-i", video]
    if len(times) == 1:
        _run([*inputs, "-vf", f"scale={tile_width}:-2", "-frames:v", "1", files["hook"]])
    else:
        scaled = "".join(f"[{i}:v]scale={tile_width}:-2[s{i}];" for i in range(len(times)))
        stack = "".join(f"[s{i}]" for i in range(len(times))) + f"hstack=inputs={len(times)}"
        _run([*inputs, "-filter_complex", scaled + stack, "-frames:v", "1", files["hook"]])
    files["hook_times_s"] = times
    files["duration_s"] = round(duration, 3)
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video")
    ap.add_argument("--prefix", default="audit_sheet")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--tile-width", type=int, default=360)
    args = ap.parse_args(argv)
    if not Path(args.video).is_file():
        print(json.dumps({"error": f"file not found: {args.video}"}))
        return 2
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print(json.dumps({"error": "ffmpeg and ffprobe must be on PATH; this check is pending until they are"}))
        return 2
    try:
        files = export_sheets(args.video, args.prefix, args.cols, args.rows, args.tile_width)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    files["next_step"] = ("Open each PNG and judge it. squint: intended focal element still dominates. "
                          "grayscale: hierarchy holds without hue. hook: frame 0 readable on mute, no fade-in.")
    print(json.dumps(files, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
