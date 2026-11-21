#!/usr/bin/env python3
"""Audit a rendered video file: streams, aspect ratio, integrated loudness and true peak.

Needs ffmpeg and ffprobe on PATH. Measures; it never rewrites your file. When loudness is
off it prints the ffmpeg command that would fix it, for you to review and run.

Profiles (integrated loudness / true-peak ceiling):
  youtube        -14 LUFS +/-1.5   -1.0 dBTP    YouTube long-form and Shorts
  social_short   -16 LUFS +/-2.0   -1.0 dBTP    TikTok and Reels. Neither publishes a target, so
                                                this is a conservative convention, not a platform
                                                rule. On clips of 60 s or less it also checks that
                                                short-term loudness never jumps more than 5 LU
                                                above target.
  broadcast_eu   -23 LUFS +/-1.0   -1.0 dBTP    EBU R128
  broadcast_us   -24 LKFS +/-2.0   -2.0 dBTP    ATSC A/85

Usage:
  python audit_media.py final.mp4 --profile youtube --aspect 16:9
  python audit_media.py short.mp4 --profile social_short --aspect 9:16

Exit codes: 0 no failures, 1 at least one check failed, 2 file or tool problem. Output is JSON.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROFILES = {
    "youtube": {"target_lufs": -14.0, "tol_lu": 1.5, "max_tp": -1.0},
    "social_short": {"target_lufs": -16.0, "tol_lu": 2.0, "max_tp": -1.0, "short_term_headroom_lu": 5.0},
    "broadcast_eu": {"target_lufs": -23.0, "tol_lu": 1.0, "max_tp": -1.0},
    "broadcast_us": {"target_lufs": -24.0, "tol_lu": 2.0, "max_tp": -2.0},
}
ASPECTS = {"9:16": 9 / 16, "16:9": 16 / 9, "4:5": 4 / 5, "1:1": 1.0, "2.39:1": 2.39}
MIN_SHORT_SIDE = 1080
_LOUDNORM_JSON = re.compile(r"\{[^{}]*\"input_i\"[^{}]*\}", re.DOTALL)
_SHORT_TERM = re.compile(r"\bS:\s*(-?\d+(?:\.\d+)?)")


def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_loudnorm(stderr_text):
    """Pull the measurement block that ffmpeg's loudnorm filter prints to stderr."""
    blocks = _LOUDNORM_JSON.findall(stderr_text)
    if not blocks:
        raise ValueError("no loudnorm measurement found in ffmpeg output")
    data = json.loads(blocks[-1])
    return {"integrated_lufs": float(data["input_i"]), "true_peak_dbtp": float(data["input_tp"]),
            "lra_lu": float(data["input_lra"]), "threshold": _num(data.get("input_thresh"))}


def parse_short_term_max(log_text):
    """Loudest short-term (3 s) reading from ffmpeg's ebur128 frame log, or None."""
    values = [float(v) for v in _SHORT_TERM.findall(log_text)]
    values = [v for v in values if v > -70.0]  # -120.7 is the filter's 'not measured yet' value
    return max(values) if values else None


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format",
                          str(path)], capture_output=True, text=True)
    if out.returncode != 0:
        raise ValueError(f"ffprobe could not read {path}: {out.stderr.strip()[:200]}")
    data = json.loads(out.stdout)
    result = {"video": None, "audio": None, "duration_s": _num(data.get("format", {}).get("duration"))}
    for s in data.get("streams", []):
        if s.get("codec_type") == "video" and result["video"] is None:
            num, _, den = (s.get("avg_frame_rate") or s.get("r_frame_rate") or "0/1").partition("/")
            fps = float(num) / float(den) if _num(den) else 0.0
            result["video"] = {"width": s.get("width"), "height": s.get("height"), "fps": round(fps, 3),
                               "codec": s.get("codec_name"), "pix_fmt": s.get("pix_fmt")}
        elif s.get("codec_type") == "audio" and result["audio"] is None:
            result["audio"] = {"codec": s.get("codec_name"), "sample_rate": int(s.get("sample_rate") or 0),
                               "channels": s.get("channels")}
    return result


def measure(path, profile):
    """One ffmpeg pass: ebur128 for short-term peaks, then loudnorm for integrated/true peak."""
    p = PROFILES[profile]
    chain = f"ebur128=framelog=verbose,loudnorm=I={p['target_lufs']:g}:TP={p['max_tp']}:LRA=11:print_format=json"
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "verbose", "-i", str(path),
                          "-vn", "-af", chain, "-f", "null", "-"], capture_output=True, text=True)
    return parse_loudnorm(out.stderr), parse_short_term_max(out.stderr)


def evaluate(probe_data, measured, profile="youtube", aspect=None, short_term_max=None,
             allow_silent=False, source=None):
    p = PROFILES[profile]
    checks = []

    def add(check_id, status, value, expected, message=""):
        checks.append({"id": check_id, "status": status, "value": value, "expected": expected, "message": message})

    video, audio = probe_data.get("video"), probe_data.get("audio")
    if video is None:
        add("video_stream", "fail", None, "a video stream", "no video stream found")
    else:
        w, h = video["width"], video["height"]
        if aspect:
            want, got = ASPECTS[aspect], w / h
            ok = abs(got - want) / want <= 0.01
            add("aspect_ratio", "pass" if ok else "fail", f"{w}x{h}", aspect,
                "" if ok else f"{w}x{h} is {got:.3f}:1, not {aspect}")
        short = min(w, h)
        add("resolution", "pass" if short >= MIN_SHORT_SIDE else "warn", f"{w}x{h}", f"short side >= {MIN_SHORT_SIDE}px",
            "" if short >= MIN_SHORT_SIDE else "below 1080p: fine for a proxy, not for delivery")

    if audio is None:
        add("audio_stream", "na" if allow_silent else "fail", None, "an audio stream",
            "no audio stream" + ("" if allow_silent else "; pass --allow-silent if that is intended"))
    else:
        add("audio_stream", "pass", f"{audio['codec']} {audio['sample_rate']} Hz", "an audio stream")

    fix = None
    if audio is not None and measured is not None:
        lufs, tp = measured["integrated_lufs"], measured["true_peak_dbtp"]
        lo, hi = p["target_lufs"] - p["tol_lu"], p["target_lufs"] + p["tol_lu"]
        l_ok = lo <= lufs <= hi
        add("integrated_lufs", "pass" if l_ok else "fail", lufs, f"{p['target_lufs']:g} LUFS +/-{p['tol_lu']:g}",
            "" if l_ok else ("too loud: the platform will turn it down and it will sound crushed" if lufs > hi
                             else "too quiet: it will sound weak next to other videos"))
        t_ok = tp <= p["max_tp"]
        add("true_peak", "pass" if t_ok else "fail", tp, f"<= {p['max_tp']} dBTP",
            "" if t_ok else "peaks can clip after the platform re-encodes to lossy audio")
        s_ok = True
        duration = probe_data.get("duration_s") or 0
        headroom = p.get("short_term_headroom_lu")
        if headroom is not None and short_term_max is not None and duration <= 60:
            limit = p["target_lufs"] + headroom
            s_ok = short_term_max <= limit
            add("short_term_jump", "pass" if s_ok else "fail", short_term_max, f"<= {limit:g} LUFS short-term",
                "" if s_ok else "a loud passage jumps more than 5 LU above target")
        if not (l_ok and t_ok and s_ok):
            src = source or "input.mp4"
            stem = Path(src)
            dst = str(stem.with_name(stem.stem + "_normalized" + (stem.suffix or ".mp4")))
            parts = [f"I={p['target_lufs']:g}", f"TP={p['max_tp']}", "LRA=11", f"measured_I={lufs}",
                     f"measured_TP={tp}", f"measured_LRA={measured['lra_lu']}"]
            if measured.get("threshold") is not None:
                parts.append(f"measured_thresh={measured['threshold']}")
            parts.append("linear=true")
            fix = f'ffmpeg -i "{src}" -af loudnorm={":".join(parts)} -c:v copy -ar 48000 "{dst}"'
    elif audio is not None:
        add("integrated_lufs", "na", None, f"{p['target_lufs']:g} LUFS +/-{p['tol_lu']:g}", "not measured")

    result = {"passed": not any(c["status"] == "fail" for c in checks), "profile": profile,
              "checks": checks, "probe": probe_data, "measured": measured, "short_term_max_lufs": short_term_max}
    if fix:
        result["fix_command"] = fix
        result["fix_note"] = "Review, run, then audit the new file again. This script changes nothing itself."
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("media_file", type=Path)
    ap.add_argument("--profile", choices=sorted(PROFILES), default="youtube")
    ap.add_argument("--aspect", choices=sorted(ASPECTS), help="expected aspect ratio")
    ap.add_argument("--allow-silent", action="store_true", help="do not fail a file with no audio stream")
    args = ap.parse_args(argv)
    if not args.media_file.is_file():
        print(json.dumps({"error": f"file not found: {args.media_file}"}))
        return 2
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print(json.dumps({"error": "ffmpeg and ffprobe must be on PATH; this check is pending until they are"}))
        return 2
    try:
        info = probe(args.media_file)
        measured, st_max = (None, None)
        if info["audio"] is not None:
            measured, st_max = measure(args.media_file, args.profile)
        result = evaluate(info, measured, args.profile, args.aspect, st_max, args.allow_silent,
                          source=str(args.media_file))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
