#!/usr/bin/env python3
"""Validate a caption file (SRT or WebVTT) for reading speed, line length and timing.

Thresholds (see references/motion-grammar.md, "Caption legibility"):
  reading speed  <= 180 WPM and >= 0.30 s/word   (BBC subtitle guidelines)
  density        <= 20 characters/second adults, 17 children   (Netflix English)
  duration       0.83 s minimum (20 frames at 24 fps), 7.0 s maximum   (Netflix)
  line length    9:16, 4:5, 1:1 -> 25 chars, up to 3 lines
                 16:9 -> 42 chars (Netflix) or 37 (--standard bbc), 2 lines

Errors block delivery. Warnings are advisory: for example a 0.5 s one-word pop is
normal for word-by-word kinetic captions on vertical video, so the minimum-duration
rule is a warning there and an error for conventional subtitles.

Usage:
  python validate_captions.py captions.srt --aspect 9:16
  python validate_captions.py captions.vtt --aspect 16:9 --standard bbc --audience children

Exit codes: 0 no errors, 1 errors found, 2 file or usage problem. Output is JSON.
"""
import argparse
import json
import re
import sys
from pathlib import Path

MAX_WPM = 180.0
MIN_SEC_PER_WORD = 0.30
MAX_CPS = {"adult": 20.0, "children": 17.0}
MIN_DURATION = 20 / 24  # 0.83 s
MAX_DURATION = 7.0

PROFILES = {
    "9:16": {"max_cpl": 25, "max_lines": 3, "style": "kinetic"},
    "4:5": {"max_cpl": 25, "max_lines": 3, "style": "kinetic"},   # same 1080 px width as 9:16
    "1:1": {"max_cpl": 25, "max_lines": 3, "style": "kinetic"},
    "16:9": {"max_cpl": 42, "max_lines": 2, "style": "subtitle"},
}
BBC_LANDSCAPE_CPL = 37

# A line should not end on a word that belongs with the next line.
WEAK_ENDINGS = {"a", "an", "the", "of", "to", "and", "or", "but", "in", "on", "at", "for",
                "with", "my", "your", "his", "her", "our", "their", "its"}

_TIME = re.compile(r"^(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})$")
_ARROW = re.compile(r"(\S+)\s+-->\s+(\S+)")
_MARKUP = re.compile(r"<[^>]+>|\{\\[^}]*\}")
# Hyphens split words ("ten-four" is two spoken words): the stricter count for pace.
_WORD = re.compile(r"[^\W_]+(?:[’':.][^\W_]+)*", re.UNICODE)
# Leading markers that are read but not spoken: ">>", a dialogue dash, [RADIO], (whispers), "DRIVER 2:".
_SPEAKER = re.compile(r"^\s*(?:>>\s*|-\s+|\[[^\]]*\]\s*|\([^)]*\)\s*|[A-Z][A-Z0-9 .'’-]{1,24}:\s+)")
_SENTENCE_END = re.compile(r"[.?!…][\"'’”)\]]*\s*$")


def parse_time(stamp):
    m = _TIME.match(stamp.strip())
    if not m:
        raise ValueError(f"unreadable timestamp: {stamp!r}")
    h, mnt, sec, frac = m.groups()
    return int(h or 0) * 3600 + int(mnt) * 60 + int(sec) + int(frac.ljust(3, "0")) / 1000.0


def strip_speaker(line):
    prev = None
    while prev != line:
        prev, line = line, _SPEAKER.sub("", line, count=1)
    return line


def count_words(text):
    """Spoken words: speaker labels and leading sound tags are excluded, hyphenated words split."""
    return sum(len(_WORD.findall(strip_speaker(ln))) for ln in text.split("\n"))


def parse_cues(text):
    """Return [(label, start_s, end_s, [lines])] for every block that has a timing line."""
    cues = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n").replace("\r", "\n").strip()):
        lines = [ln.strip() for ln in block.split("\n")]
        at = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if at is None:
            continue
        m = _ARROW.search(lines[at])
        if not m:
            continue
        try:
            start, end = parse_time(m.group(1)), parse_time(m.group(2))
        except ValueError:
            continue
        body = [re.sub(r"\s+", " ", _MARKUP.sub("", ln)).strip() for ln in lines[at + 1:]]
        body = [ln for ln in body if ln]
        label = lines[at - 1] if at > 0 and lines[at - 1] else str(len(cues) + 1)
        cues.append((label, start, end, body))
    return cues


def validate(text, aspect="9:16", standard="netflix", style=None, audience="adult",
             max_cpl=None, max_lines=None):
    if aspect not in PROFILES:
        raise ValueError(f"unknown aspect {aspect!r}; choose from {sorted(PROFILES)}")
    profile = dict(PROFILES[aspect])
    if aspect == "16:9" and standard == "bbc":
        profile["max_cpl"] = BBC_LANDSCAPE_CPL
    if max_cpl:
        profile["max_cpl"] = max_cpl
    if max_lines:
        profile["max_lines"] = max_lines
    if style:
        profile["style"] = style
    profile.update(max_wpm=MAX_WPM, max_cps=MAX_CPS[audience], min_sec_per_word=MIN_SEC_PER_WORD,
                   min_duration_s=round(MIN_DURATION, 2), max_duration_s=MAX_DURATION,
                   aspect=aspect, standard=standard, audience=audience)

    out, prev_end, total_words, total_time = [], None, 0, 0.0
    for label, start, end, body in parse_cues(text):
        issues = []

        def add(code, severity, message):
            issues.append({"code": code, "severity": severity, "message": message})

        dur = end - start
        plain = " ".join(body)
        words, chars = count_words("\n".join(body)), len(plain)
        cue = {"cue": label, "start_s": round(start, 3), "end_s": round(end, 3), "dur_s": round(dur, 3),
               "lines": len(body), "words": words, "chars": chars}
        if dur <= 0:
            add("bad_timing", "error", f"end {end:.3f}s is not after start {start:.3f}s")
            cue.update(wpm=None, cps=None, sec_per_word=None)
        else:
            wpm, cps = words / dur * 60.0, chars / dur
            spw = dur / words if words else None
            cue.update(wpm=round(wpm, 1), cps=round(cps, 1), sec_per_word=round(spw, 2) if spw else None)
            if wpm > MAX_WPM:
                add("wpm", "error", f"{wpm:.1f} WPM is over the {MAX_WPM:.0f} WPM ceiling")
            if cps > profile["max_cps"]:
                add("cps", "error", f"{cps:.1f} chars/s is over the {profile['max_cps']:.0f} CPS ceiling")
            if spw is not None and spw < MIN_SEC_PER_WORD:
                add("sec_per_word", "error", f"{spw:.2f} s/word is under the {MIN_SEC_PER_WORD:.2f} s/word floor")
            if dur > MAX_DURATION:
                add("max_duration", "error", f"{dur:.2f} s on screen is over the {MAX_DURATION:.1f} s maximum")
            if dur < MIN_DURATION - 1e-3:
                severity = "error" if profile["style"] == "subtitle" else "warning"
                add("min_duration", severity, f"{dur:.2f} s on screen is under the {MIN_DURATION:.2f} s minimum")
        if prev_end is not None and start < prev_end - 1e-6:
            add("overlap", "error", f"starts {prev_end - start:.3f} s before the previous cue ends")
        if len(body) > profile["max_lines"]:
            add("line_count", "error", f"{len(body)} lines; maximum is {profile['max_lines']}")
        for n, line in enumerate(body, 1):
            if len(line) > profile["max_cpl"]:
                add("line_length", "error", f"line {n} is {len(line)} chars; maximum is {profile['max_cpl']}")
            last = _WORD.findall(line.lower())
            if n < len(body) and last and last[-1] in WEAK_ENDINGS and not _SENTENCE_END.search(line):
                add("weak_line_break", "warning",
                    f"line {n} ends on '{last[-1]}'; break at a phrase boundary instead")
        cue["issues"] = issues
        out.append(cue)
        prev_end = max(prev_end, end) if prev_end is not None else end
        if dur > 0:
            total_words += words
            total_time += dur

    errors = sum(1 for c in out for i in c["issues"] if i["severity"] == "error")
    warnings = sum(1 for c in out for i in c["issues"] if i["severity"] == "warning")
    timed = [c for c in out if c["wpm"] is not None]
    summary = {
        "cues": len(out), "errors": errors, "warnings": warnings,
        "overall_wpm": round(total_words / total_time * 60.0, 1) if total_time else None,
        "worst_wpm": max((c["wpm"] for c in timed), default=None),
        "worst_cps": max((c["cps"] for c in timed), default=None),
        "longest_line": max((len(ln) for _, _, _, body in parse_cues(text) for ln in body), default=0),
        "notes": [],
    }
    if not out:
        summary["notes"].append("no_cues: no caption cues found; is this an SRT or WebVTT file?")
    return {"passed": bool(out) and errors == 0, "profile": profile, "summary": summary, "cues": out}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("caption_file", type=Path)
    ap.add_argument("--aspect", choices=sorted(PROFILES), default="9:16")
    ap.add_argument("--standard", choices=["netflix", "bbc"], default="netflix",
                    help="16:9 line length: netflix = 42 chars, bbc = 37")
    ap.add_argument("--style", choices=["subtitle", "kinetic"],
                    help="subtitle: 0.83 s minimum is an error; kinetic: it is a warning")
    ap.add_argument("--audience", choices=sorted(MAX_CPS), default="adult")
    ap.add_argument("--max-cpl", type=int, help="override characters per line")
    ap.add_argument("--max-lines", type=int, help="override lines per cue")
    ap.add_argument("--issues-only", action="store_true", help="print only cues that have issues")
    args = ap.parse_args(argv)
    try:
        text = args.caption_file.read_text(encoding="utf-8-sig")
    except OSError as exc:
        print(json.dumps({"error": f"cannot read {args.caption_file}: {exc}"}))
        return 2
    result = validate(text, args.aspect, args.standard, args.style, args.audience, args.max_cpl, args.max_lines)
    if args.issues_only:
        result["cues"] = [c for c in result["cues"] if c["issues"]]
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
