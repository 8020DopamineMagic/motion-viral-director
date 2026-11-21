import json
import subprocess
import sys
from pathlib import Path

import pytest

import check_safe_zones as sz

SCRIPT = Path(sz.__file__)

# Pixel table from the source document, 1080 x 1920 canvas: (x1, y1, x2, y2).
PUBLISHED = {
    "tiktok": (65, 154, 940, 1498),
    "instagram_reels": (65, 230, 961, 1306),
    "instagram_stories": (65, 250, 1015, 1536),
    "youtube_shorts": (65, 173, 950, 1536),
    "universal_3feed": (65, 230, 940, 1306),
    "universal_4feed": (65, 250, 940, 1306),
}


@pytest.mark.parametrize("platform,box", PUBLISHED.items())
def test_safe_bounds_match_published_table(platform, box):
    assert tuple(sz.safe_bounds(platform)) == box


def test_universal_zones_are_true_intersections():
    def intersect(names):
        boxes = [sz.safe_bounds(n) for n in names]
        return (max(b[0] for b in boxes), max(b[1] for b in boxes),
                min(b[2] for b in boxes), min(b[3] for b in boxes))
    three = ["tiktok", "instagram_reels", "youtube_shorts"]
    assert tuple(sz.safe_bounds("universal_3feed")) == intersect(three)
    assert tuple(sz.safe_bounds("universal_4feed")) == intersect(three + ["instagram_stories"])


def test_box_inside_passes():
    r = sz.check_box(100, 300, 700, 400, "universal_3feed")
    assert r["passed"] is True and r["violations"] == []


def test_box_over_bottom_ui_fails_with_fix():
    r = sz.check_box(100, 1400, 700, 160, "universal_3feed")
    assert r["passed"] is False
    v = r["violations"][0]
    assert v["edge"] == "bottom" and v["overshoot_px"] == 1560 - 1306
    assert r["fix"]["y"] == 1306 - 160  # same size, moved up


def test_box_too_big_gets_resize_fix():
    r = sz.check_box(0, 0, 1080, 1920, "tiktok")
    assert {v["edge"] for v in r["violations"]} == {"left", "right", "top", "bottom"}
    assert (r["fix"]["w"], r["fix"]["h"]) == (875, 1344)


def test_scales_to_other_frame_sizes():
    b = sz.safe_bounds("universal_3feed", frame_w=2160, frame_h=3840)
    assert tuple(b) == (130, 461, 1879, 2611)


def test_custom_margins_and_unknown_platform():
    assert tuple(sz.safe_bounds(margins={"top": 0.1, "bottom": 0.1, "left": 0.05, "right": 0.05})) == (54, 192, 1026, 1728)
    with pytest.raises(KeyError):
        sz.safe_bounds("myspace")


def test_cli_single_box_and_multi_platform(tmp_path):
    p = subprocess.run([sys.executable, str(SCRIPT), "--x", "100", "--y", "1400", "--w", "700", "--h", "160",
                        "--platform", "tiktok", "--platform", "instagram_reels"], capture_output=True, text=True)
    out = json.loads(p.stdout)
    assert p.returncode == 1
    by_platform = {r["platform"]: r["passed"] for r in out["results"]}
    assert by_platform == {"tiktok": False, "instagram_reels": False}
    boxes = tmp_path / "boxes.json"
    boxes.write_text(json.dumps([{"name": "headline", "x": 100, "y": 300, "w": 700, "h": 200},
                                 {"name": "cta", "x": 100, "y": 1350, "w": 700, "h": 100}]))
    p = subprocess.run([sys.executable, str(SCRIPT), "--boxes", str(boxes)], capture_output=True, text=True)
    out = json.loads(p.stdout)
    assert p.returncode == 1
    assert [(r["name"], r["passed"]) for r in out["results"]] == [("headline", True), ("cta", False)]
    p = subprocess.run([sys.executable, str(SCRIPT), "--list"], capture_output=True, text=True)
    assert p.returncode == 0 and json.loads(p.stdout)["universal_3feed"]["safe_size"] == [875, 1076]
