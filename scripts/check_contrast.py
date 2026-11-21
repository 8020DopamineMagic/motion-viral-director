#!/usr/bin/env python3
"""WCAG 2.2 contrast check for text, captions and accents.

SC 1.4.3 (AA): 4.5:1 for normal text and captions, 3.0:1 for large text
(roughly 24 px regular or 18.7 px bold and up, relative to a 1080 px wide frame scaled to viewing size).
AAA is 7.0:1 / 4.5:1. Ratios are compared unrounded, so 4.48:1 fails.

Captions over moving footage have no fixed background, so test the scrim instead:
--scrim composites a translucent box over the brightest and darkest possible footage and
reports the worst case, plus the lowest opacity that would pass.

Usage:
  python check_contrast.py --fg "#EDE6D6" --bg "#0E131B"
  python check_contrast.py --pair "#F29F3D:#253040:accent on card" --pair "#777:#fff:fine print:large"
  python check_contrast.py --fg "#FFFFFF" --scrim "#000000@0.6"
  python check_contrast.py --pairs palette.json      # [{"fg": "...", "bg": "...", "label": "...", "large": false}]

Exit codes: 0 all pass AA, 1 at least one fails, 2 usage problem. Output is JSON.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

AA_NORMAL, AA_LARGE, AAA_NORMAL, AAA_LARGE = 4.5, 3.0, 7.0, 4.5
_HEX = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def parse_hex(color):
    m = _HEX.match(color.strip())
    if not m:
        raise ValueError(f"not a hex colour: {color!r}")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in rgb)


def _linear(channel):
    c = channel / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb):
    r, g, b = (_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _ratio_rgb(a, b):
    la, lb = relative_luminance(a), relative_luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def contrast_ratio(fg, bg):
    return _ratio_rgb(parse_hex(fg), parse_hex(bg))


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def suggest(fg, bg, target):
    """Nearest colour to fg, pushed toward black or white, that reaches the target ratio."""
    f, b = parse_hex(fg), parse_hex(bg)
    toward = (0, 0, 0) if relative_luminance(b) > 0.179 else (255, 255, 255)
    if _ratio_rgb(toward, b) < target:
        return None
    lo, hi = 0.0, 1.0
    for _ in range(24):
        mid = (lo + hi) / 2
        if _ratio_rgb(tuple(round(c) for c in _mix(f, toward, mid)), b) >= target:
            hi = mid
        else:
            lo = mid
    return to_hex(_mix(f, toward, hi))


def evaluate(fg, bg, large=False, label=None):
    ratio = contrast_ratio(fg, bg)
    target = AA_LARGE if large else AA_NORMAL
    out = {"label": label, "fg": fg, "bg": bg, "large": large, "ratio": round(ratio, 2),
           "required": target, "aa_normal": ratio >= AA_NORMAL, "aa_large": ratio >= AA_LARGE,
           "aaa_normal": ratio >= AAA_NORMAL, "aaa_large": ratio >= AAA_LARGE, "passed": ratio >= target}
    if not out["passed"]:
        out["suggestion"] = suggest(fg, bg, target)
    return out


def _worst_over_footage(fg_rgb, scrim_rgb, alpha):
    worst = None
    for footage in ((255, 255, 255), (0, 0, 0)):
        composite = tuple(round(c) for c in _mix(footage, scrim_rgb, alpha))
        ratio = _ratio_rgb(fg_rgb, composite)
        if worst is None or ratio < worst[0]:
            worst = (ratio, composite)
    return worst


def evaluate_scrim(fg, scrim, alpha, large=False, label=None):
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("scrim opacity must be between 0 and 1")
    f, s = parse_hex(fg), parse_hex(scrim)
    target = AA_LARGE if large else AA_NORMAL
    ratio, composite = _worst_over_footage(f, s, alpha)
    min_alpha = None
    if _worst_over_footage(f, s, 1.0)[0] >= target:
        lo, hi = 0.0, 1.0
        for _ in range(24):
            mid = (lo + hi) / 2
            if _worst_over_footage(f, s, mid)[0] >= target:
                hi = mid
            else:
                lo = mid
        min_alpha = math.ceil(hi * 100 - 1e-9) / 100
    return {"label": label, "fg": fg, "scrim": scrim, "alpha": alpha, "large": large,
            "worst_case_bg": to_hex(composite), "ratio": round(ratio, 2), "required": target,
            "passed": ratio >= target, "min_alpha_for_aa": min_alpha}


def _parse_pair(spec):
    parts = spec.split(":")
    if len(parts) < 2:
        raise ValueError(f"pair must be FG:BG[:label[:large]], got {spec!r}")
    large = len(parts) > 3 and parts[3].strip().lower() == "large"
    return {"fg": parts[0], "bg": parts[1], "label": parts[2] if len(parts) > 2 else None, "large": large}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fg")
    ap.add_argument("--bg")
    ap.add_argument("--large", action="store_true", help="large text: 3.0:1 is enough")
    ap.add_argument("--pair", action="append", default=[], metavar="FG:BG[:LABEL[:large]]")
    ap.add_argument("--pairs", type=Path, help="JSON list of pairs")
    ap.add_argument("--scrim", metavar="HEX@OPACITY", help="translucent caption box over moving footage")
    args = ap.parse_args(argv)
    try:
        results = []
        pairs = [_parse_pair(p) for p in args.pair]
        if args.pairs:
            pairs += json.loads(args.pairs.read_text(encoding="utf-8"))
        if args.fg and args.bg:
            pairs.append({"fg": args.fg, "bg": args.bg, "large": args.large})
        for p in pairs:
            results.append(evaluate(p["fg"], p["bg"], bool(p.get("large")), p.get("label")))
        if args.scrim:
            if not args.fg:
                ap.error("--scrim needs --fg")
            colour, _, alpha = args.scrim.partition("@")
            results.append(evaluate_scrim(args.fg, colour, float(alpha or 1), args.large))
        if not results:
            ap.error("give --fg and --bg, --pair, --pairs, or --fg with --scrim")
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    passed = all(r["passed"] for r in results)
    print(json.dumps({"passed": passed, "standard": "WCAG 2.2 SC 1.4.3 (AA)", "results": results}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
