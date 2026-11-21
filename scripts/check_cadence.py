#!/usr/bin/env python3
"""Check spoken-copy pacing before anything is recorded or rendered.

Works on a script, not a media file, so it runs during pre-production.

Limits (per beat, blocking):  <= 180 WPM, <= 20 chars/s, >= 0.30 s/word
Advice (whole piece):         130-150 WPM conversational baseline,
                              15-25% of runtime left free of speech for visuals, SFX and silence

Three modes:
  1) One line:      python check_cadence.py --text "At 3:14, every clock stopped" --seconds 2.7
  2) Timed beats:   python check_cadence.py --beats beats.txt
                    beats.txt has one beat per line, "START-END | spoken copy". Leave the copy
                    blank for a beat with no speech. Lines starting with # are ignored.
                        00:00.0-00:00.5 |
                        00:00.5-00:03.2 | At 3:14, every clock in the harbor stopped.
  3) Will it fit?   python check_cadence.py --file script.txt --runtime 45 [--wpm 140]

Exit codes: 0 pass, 1 a limit is broken (or the script does not fit), 2 usage problem. Output is JSON.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

MAX_WPM = 180.0
MAX_CPS = 20.0
MIN_SEC_PER_WORD = 0.30
BASELINE_WPM = (130.0, 150.0)
MIN_BREATHING_PCT = 15.0
MAX_SPEECH_FRACTION = 0.85      # leaves 15% breathing room
COMFORT_SPEECH_FRACTION = 0.75  # leaves 25%

# Hyphens split words ("forty-seven" is two spoken words): the stricter count for pace.
_WORD = re.compile(r"[^\W_]+(?:[’':.][^\W_]+)*", re.UNICODE)
_NUMERAL_OR_ACRONYM = re.compile(r"\d|\b[A-Z]{2,}\b")
_RANGE = re.compile(r"\s*(?:-->|[-–—]+|\bto\b)\s*")


def count_words(text):
    return len(_WORD.findall(text))


def parse_time(stamp):
    """Accept 12.7, 1:02.5, 00:01:02,500 and return seconds."""
    parts = stamp.strip().replace(",", ".").split(":")
    if not 1 <= len(parts) <= 3:
        raise ValueError(f"unreadable timecode: {stamp!r}")
    try:
        total = 0.0
        for p in parts:
            total = total * 60 + float(p)
    except ValueError:
        raise ValueError(f"unreadable timecode: {stamp!r}") from None
    return total


def parse_beats(text):
    beats = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" not in line:
            raise ValueError(f"line {n}: expected 'START-END | spoken copy', got {raw!r}")
        span, copy = line.split("|", 1)
        ends = _RANGE.split(span.strip())
        if len(ends) != 2:
            raise ValueError(f"line {n}: expected 'START-END' before the bar, got {span.strip()!r}")
        start, end = parse_time(ends[0]), parse_time(ends[1])
        if end <= start:
            raise ValueError(f"line {n}: end must be after start ({span.strip()})")
        beats.append({"start": start, "end": end, "text": copy.strip()})
    if not beats:
        raise ValueError("no beats found")
    return beats


def measure(text, seconds):
    text = re.sub(r"\s+", " ", text).strip()
    words, chars = count_words(text), len(text)
    issues = []
    if seconds <= 0:
        raise ValueError("seconds must be positive")
    wpm, cps = words / seconds * 60.0, chars / seconds
    spw = seconds / words if words else None
    if wpm > MAX_WPM:
        issues.append({"code": "wpm", "message": f"{wpm:.1f} WPM is over the {MAX_WPM:.0f} WPM ceiling"})
    if cps > MAX_CPS:
        issues.append({"code": "cps", "message": f"{cps:.1f} chars/s is over the {MAX_CPS:.0f} CPS ceiling"})
    if spw is not None and spw < MIN_SEC_PER_WORD:
        issues.append({"code": "sec_per_word",
                       "message": f"{spw:.2f} s/word is under the {MIN_SEC_PER_WORD:.2f} s/word floor"})
    if issues and words:
        need = max(words / MAX_WPM * 60.0, chars / MAX_CPS, words * MIN_SEC_PER_WORD)
        keep = min(int(seconds * MAX_WPM / 60.0), int(seconds / MIN_SEC_PER_WORD))
        issues.append({"code": "fix", "message": f"give this line {need:.1f} s, or cut it to {keep} words"})
    notes = []
    found = sorted(set(re.findall(r"[$€£]?\d[\d:.,]*%?|\b[A-Z]{2,}\b", text)))
    if found:
        notes.append({"code": "spoken_count", "message": (
            f"numerals or acronyms ({', '.join(found)}) are counted as one word each; spoken aloud they "
            "are usually more ('$400' = four hundred dollars, 'HVAC' = four letters). Write them as spoken "
            "and re-check before trusting the pace")})
    return {"words": words, "chars": chars, "seconds": round(seconds, 3), "wpm": round(wpm, 1),
            "cps": round(cps, 1), "sec_per_word": round(spw, 2) if spw else None,
            "issues": issues, "notes": notes, "passed": not issues}


def analyze_beats(beats):
    rows, words, speech = [], 0, 0.0
    for b in beats:
        dur = b["end"] - b["start"]
        m = measure(b["text"], dur)
        rows.append({"start": b["start"], "end": b["end"], "text": b["text"], **m})
        if m["words"]:
            words += m["words"]
            speech += dur
    runtime = max(b["end"] for b in beats) - min(b["start"] for b in beats)
    overall = words / speech * 60.0 if speech else 0.0
    breathing = (runtime - speech) / runtime * 100.0 if runtime else 0.0
    warnings = []
    if speech and overall > BASELINE_WPM[1]:
        warnings.append({"code": "above_conversational_baseline",
                         "message": f"overall {overall:.1f} WPM is above the {BASELINE_WPM[0]:.0f}-"
                                    f"{BASELINE_WPM[1]:.0f} WPM conversational range; fine for a hook, tiring for a whole piece"})
    if speech and overall < BASELINE_WPM[0]:
        warnings.append({"code": "below_conversational_baseline",
                         "message": f"overall {overall:.1f} WPM is below the conversational range; check it is deliberate"})
    if speech and breathing < MIN_BREATHING_PCT:
        warnings.append({"code": "low_breathing_room",
                         "message": f"only {breathing:.1f}% of runtime is free of speech; aim for 15-25%"})
    return {"passed": all(r["passed"] for r in rows), "beats": rows,
            "totals": {"words": words, "speech_s": round(speech, 3), "runtime_s": round(runtime, 3),
                       "silence_s": round(runtime - speech, 3), "overall_wpm": round(overall, 1),
                       "breathing_room_pct": round(breathing, 1)},
            "warnings": warnings}


def fit(words, runtime_s, wpm=140.0):
    speech = words / wpm * 60.0
    return {"words": words, "wpm": wpm, "runtime_s": runtime_s, "speech_s": round(speech, 1),
            "speech_pct": round(speech / runtime_s * 100.0, 1),
            "max_words": math.floor(runtime_s * MAX_SPEECH_FRACTION * wpm / 60.0),
            "comfortable_words": math.floor(runtime_s * COMFORT_SPEECH_FRACTION * wpm / 60.0),
            "fits": speech <= runtime_s * MAX_SPEECH_FRACTION + 1e-9}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--beats", type=Path, help="file of 'START-END | spoken copy' lines")
    ap.add_argument("--text", help="spoken copy as a string")
    ap.add_argument("--file", type=Path, help="spoken copy in a text file")
    ap.add_argument("--seconds", type=float, help="time available for --text (mode 1)")
    ap.add_argument("--runtime", type=float, help="total runtime to fit the copy into (mode 3)")
    ap.add_argument("--wpm", type=float, default=140.0, help="delivery pace for --runtime (default 140)")
    args = ap.parse_args(argv)
    try:
        if args.beats:
            result = analyze_beats(parse_beats(args.beats.read_text(encoding="utf-8-sig")))
            ok = result["passed"]
        else:
            text = args.text if args.text is not None else (
                args.file.read_text(encoding="utf-8-sig") if args.file else None)
            if text is None:
                ap.error("give --beats, --text or --file")
            if args.seconds is not None:
                result = measure(text, args.seconds)
                ok = result["passed"]
            elif args.runtime is not None:
                result = fit(count_words(text), args.runtime, args.wpm)
                ok = result["fits"]
            else:
                ap.error("--text/--file needs --seconds or --runtime")
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
