#!/usr/bin/env python3
"""Check that text, logos and CTAs sit clear of platform UI on vertical (9:16) video.

The margins below are WORKING DEFAULTS for organic posts, taken from the source playbook
(June 2026). Platforms do not publish one stable pixel box, third-party guides disagree,
and paid placements reserve more space. So: design to the universal zone, then confirm
with an in-app draft preview before anything high-stakes. Use --margins to test a
different set (for example an ad spec).

On a 1080 x 1920 canvas the universal 3-feed zone (TikTok + Reels + Shorts) is
x 65..940, y 230..1306 (875 x 1076 px).

Usage:
  python check_safe_zones.py --x 100 --y 300 --w 700 --h 200
  python check_safe_zones.py --box headline:100,300,700,200 --box cta:100,1350,700,100 --platform all
  python check_safe_zones.py --boxes overlays.json --frame 2160x3840
  python check_safe_zones.py --list

Coordinates are pixels from the top-left corner; a box is x, y, width, height.
Exit codes: 0 every box is inside, 1 something is covered, 2 usage problem. Output is JSON.
"""
import argparse
import json
import sys
from pathlib import Path

# Fraction of the frame covered by platform UI on each edge.
PLATFORM_MARGINS = {
    "tiktok": {"top": 0.08, "bottom": 0.22, "left": 0.06, "right": 0.13},
    "instagram_reels": {"top": 0.12, "bottom": 0.32, "left": 0.06, "right": 0.11},
    "instagram_stories": {"top": 0.13, "bottom": 0.20, "left": 0.06, "right": 0.06},
    "youtube_shorts": {"top": 0.09, "bottom": 0.20, "left": 0.06, "right": 0.12},
}
# Universal zones are derived, never typed in, so they cannot drift from their members.
UNIVERSAL = {
    "universal_3feed": ["tiktok", "instagram_reels", "youtube_shorts"],
    "universal_4feed": ["tiktok", "instagram_reels", "youtube_shorts", "instagram_stories"],
}
EDGES = ("top", "bottom", "left", "right")
NOTE = ("Working defaults (source playbook, June 2026), not official platform specs. "
        "Confirm with an in-app draft preview before a high-stakes upload.")


def margins_for(platform):
    if platform in UNIVERSAL:
        members = [PLATFORM_MARGINS[m] for m in UNIVERSAL[platform]]
        return {e: max(m[e] for m in members) for e in EDGES}
    return dict(PLATFORM_MARGINS[platform])  # KeyError for an unknown platform is intended


def platforms():
    return list(PLATFORM_MARGINS) + list(UNIVERSAL)


def safe_bounds(platform="universal_3feed", frame_w=1080, frame_h=1920, margins=None):
    """Return [x1, y1, x2, y2]: content must stay inside this rectangle."""
    m = margins or margins_for(platform)
    return [round(frame_w * m["left"]), round(frame_h * m["top"]),
            frame_w - round(frame_w * m["right"]), frame_h - round(frame_h * m["bottom"])]


def check_box(x, y, w, h, platform="universal_3feed", frame_w=1080, frame_h=1920, margins=None):
    x1, y1, x2, y2 = safe_bounds(platform, frame_w, frame_h, margins)
    violations = []

    def add(edge, overshoot, what):
        violations.append({"edge": edge, "overshoot_px": overshoot, "message": what})

    if x < x1:
        add("left", x1 - x, f"left edge at {x}px is {x1 - x}px inside the left UI margin (min {x1}px)")
    if x + w > x2:
        add("right", x + w - x2, f"right edge at {x + w}px is {x + w - x2}px into the right-hand buttons (max {x2}px)")
    if y < y1:
        add("top", y1 - y, f"top edge at {y}px is {y1 - y}px under the top UI (min {y1}px)")
    if y + h > y2:
        add("bottom", y + h - y2, f"bottom edge at {y + h}px is {y + h - y2}px into the caption/CTA area (max {y2}px)")
    fix = None
    if violations:
        fw, fh = min(w, x2 - x1), min(h, y2 - y1)
        fix = {"x": min(max(x, x1), x2 - fw), "y": min(max(y, y1), y2 - fh), "w": fw, "h": fh}
    return {"platform": "custom" if margins else platform, "passed": not violations,
            "box": [x, y, w, h], "safe_bounds": [x1, y1, x2, y2], "violations": violations, "fix": fix}


def describe(frame_w=1080, frame_h=1920):
    table = {}
    for p in platforms():
        b = safe_bounds(p, frame_w, frame_h)
        table[p] = {"margins_pct": {e: round(v * 100) for e, v in margins_for(p).items()},
                    "safe_bounds": b, "safe_size": [b[2] - b[0], b[3] - b[1]]}
    return table


def _parse_box(spec):
    name, _, nums = spec.rpartition(":")
    try:
        x, y, w, h = (int(v) for v in nums.split(","))
    except ValueError:
        raise ValueError(f"box must be [name:]x,y,w,h, got {spec!r}") from None
    return {"name": name or "box", "x": x, "y": y, "w": w, "h": h}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for flag in ("--x", "--y", "--w", "--h"):
        ap.add_argument(flag, type=int)
    ap.add_argument("--box", action="append", default=[], metavar="[NAME:]X,Y,W,H")
    ap.add_argument("--boxes", type=Path, help='JSON list of {"name","x","y","w","h"}')
    ap.add_argument("--platform", action="append", default=[], choices=platforms() + ["all"])
    ap.add_argument("--frame", default="1080x1920", metavar="WxH")
    ap.add_argument("--margins", metavar="TOP,BOTTOM,LEFT,RIGHT", help="custom margins as percentages, e.g. 12,35,6,13")
    ap.add_argument("--list", action="store_true", help="print the safe box for every platform")
    args = ap.parse_args(argv)
    try:
        fw, fh = (int(v) for v in args.frame.lower().split("x"))
        if args.list:
            print(json.dumps(describe(fw, fh), indent=2))
            return 0
        boxes = [_parse_box(b) for b in args.box]
        if args.boxes:
            boxes += json.loads(args.boxes.read_text(encoding="utf-8"))
        if args.x is not None:
            if None in (args.y, args.w, args.h):
                ap.error("--x needs --y, --w and --h")
            boxes.append({"name": "box", "x": args.x, "y": args.y, "w": args.w, "h": args.h})
        if not boxes:
            ap.error("give a box with --x/--y/--w/--h, --box or --boxes (or use --list)")
        custom = None
        if args.margins:
            t, b, l, r = (float(v) / 100.0 for v in args.margins.split(","))
            custom = {"top": t, "bottom": b, "left": l, "right": r}
        targets = args.platform or ["universal_3feed"]
        if "all" in targets:
            targets = platforms()
        if custom:
            targets = ["custom"]
        results = []
        for box in boxes:
            for p in targets:
                r = check_box(box["x"], box["y"], box["w"], box["h"], p if not custom else "universal_3feed",
                              fw, fh, custom)
                results.append({"name": box.get("name", "box"), **r})
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    passed = all(r["passed"] for r in results)
    print(json.dumps({"passed": passed, "frame": [fw, fh], "results": results, "note": NOTE}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
