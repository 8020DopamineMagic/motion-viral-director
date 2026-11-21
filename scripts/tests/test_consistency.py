"""The documentation quotes numbers that the scripts own. These tests fail when the two drift apart."""
import re

import pytest

import audit_media as am
import check_cadence as cc
import check_contrast as ct
import check_safe_zones as sz
import validate_captions as vc
from conftest import SKILL_ROOT

SKILL = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
REFS = {p.name: p.read_text(encoding="utf-8") for p in (SKILL_ROOT / "references").glob("*.md")}
EXAMPLES = REFS["worked-examples.md"]


def frontmatter():
    block = SKILL.split("---", 2)[1]
    return dict(re.findall(r"^(\w+):\s*(.+)$", block, re.MULTILINE))


def test_frontmatter_and_size():
    fm = frontmatter()
    assert fm["name"] == SKILL_ROOT.name == "motion-viral-director"
    assert 100 < len(fm["description"]) <= 1024
    assert "<" not in fm["description"] and ">" not in fm["description"]
    assert len(SKILL.splitlines()) < 500


def test_every_file_the_docs_point_to_exists():
    docs = SKILL + "".join(REFS.values())
    for name in set(re.findall(r"\b([a-z_]+\.py)\b", docs)):
        found = (SKILL_ROOT / "scripts" / name).is_file() or (SKILL_ROOT / "scripts" / "tests" / name).is_file()
        assert found, f"docs mention scripts/{name}"
    for name in set(re.findall(r"\b([a-z0-9-]+\.md)\b", docs)) - {"SKILL.md"}:
        assert (SKILL_ROOT / "references" / name).is_file() or (SKILL_ROOT / "assets" / name).is_file(), name
    for name in set(re.findall(r"assets/([\w.-]+)", docs)):
        assert (SKILL_ROOT / "assets" / name).is_file(), f"docs mention assets/{name}"


def test_every_script_is_listed_in_skill_md():
    for script in (SKILL_ROOT / "scripts").glob("*.py"):
        assert f"`{script.name}`" in SKILL, f"{script.name} is not in the SKILL.md validator table"


@pytest.mark.parametrize("label,platform", [
    ("Universal: TikTok + Reels + Shorts", "universal_3feed"), ("Universal + Instagram Stories", "universal_4feed"),
    ("TikTok only", "tiktok"), ("Instagram Reels only", "instagram_reels"),
    ("YouTube Shorts only", "youtube_shorts"), ("Instagram Stories only", "instagram_stories")])
def test_safe_zone_table_in_skill_md(label, platform):
    x1, y1, x2, y2 = sz.safe_bounds(platform)
    row = next(line for line in SKILL.splitlines() if line.startswith(f"| {label}"))
    assert f"x {x1}-{x2}, y {y1}-{y2}" in row
    if "Universal" in label:
        assert f"({x2 - x1} x {y2 - y1})" in row


def test_safe_zone_table_in_reference():
    text = REFS["production-compliance.md"]
    for platform in sz.platforms():
        x1, y1, x2, y2 = sz.safe_bounds(platform)
        assert f"x {x1}..{x2}, y {y1}..{y2}" in text, platform


def test_caption_and_cadence_limits_in_skill_md():
    assert f"{vc.MAX_WPM:.0f} WPM, and at least {vc.MIN_SEC_PER_WORD:.2f} s per word" in SKILL
    assert f"{vc.MAX_CPS['adult']:.0f} chars/s adults, {vc.MAX_CPS['children']:.0f} children" in SKILL
    assert f"{vc.MIN_DURATION:.2f} s to {vc.MAX_DURATION:.1f} s" in SKILL
    assert f"{vc.PROFILES['9:16']['max_cpl']} chars, up to {vc.PROFILES['9:16']['max_lines']} lines" in SKILL
    assert f"{vc.PROFILES['16:9']['max_cpl']} chars, {vc.PROFILES['16:9']['max_lines']} lines (BBC: {vc.BBC_LANDSCAPE_CPL})" in SKILL
    assert (vc.MAX_WPM, vc.MIN_SEC_PER_WORD, vc.MAX_CPS["adult"]) == (cc.MAX_WPM, cc.MIN_SEC_PER_WORD, cc.MAX_CPS)
    assert f"{cc.BASELINE_WPM[0]:.0f}-{cc.BASELINE_WPM[1]:.0f} WPM" in SKILL
    f = cc.fit(words=1, runtime_s=45, wpm=140)
    assert f"at most {f['max_words']} words, and about {f['comfortable_words']}" in SKILL


def test_word_budget_table_in_story_reference():
    text = REFS["story-script.md"]
    for label, seconds in [("15 s", 15), ("30 s", 30), ("45 s", 45), ("60 s", 60), ("90 s", 90), ("2 min", 120)]:
        f = cc.fit(words=1, runtime_s=seconds, wpm=140)
        assert f"| {label} | {f['max_words']} | {f['comfortable_words']} |" in text


def test_loudness_table_in_skill_md():
    p = am.PROFILES
    assert f"| YouTube long-form and Shorts | {p['youtube']['target_lufs']:g} LUFS | {p['youtube']['max_tp']} dBTP |" in SKILL
    assert f"| {p['social_short']['target_lufs']:g} LUFS | {p['social_short']['max_tp']} dBTP |" in SKILL
    assert f"| {p['broadcast_eu']['target_lufs']:g} LUFS | {p['broadcast_eu']['max_tp']} dBTP |" in SKILL
    assert f"| {p['broadcast_us']['target_lufs']:g} LKFS | {p['broadcast_us']['max_tp']} dBTP |" in SKILL


def test_contrast_claims():
    assert f"{ct.AA_NORMAL}:1" in SKILL and f"{ct.AA_LARGE}:1" in SKILL
    pct = round(ct.evaluate_scrim("#FFFFFF", "#000000", 0.5)["min_alpha_for_aa"] * 100)
    assert f"at least {pct}% opacity" in SKILL
    for fg, bg in [("#EDE6D6", "#0E131B"), ("#F29F3D", "#0E131B"), ("#F29F3D", "#253040"), ("#F7F4EC", "#0A0E14")]:
        assert f"{ct.contrast_ratio(fg, bg):.2f}:1" in EXAMPLES, (fg, bg)


def test_worked_example_pacing_is_what_the_script_computes():
    rows = re.findall(r"^\| (\d\d:\d\d\.\d)-(\d\d:\d\d\.\d) \|.*?\*\*VO \((\d+) words, ([\d.]+) WPM, ([\d.]+) CPS\):\*\* \"([^\"]+)\"",
                      EXAMPLES, re.MULTILINE)
    assert len(rows) == 4
    words = speech = 0
    for start, end, n, wpm, cps, text in rows:
        dur = cc.parse_time(end) - cc.parse_time(start)
        m = cc.measure(text, dur)
        assert (m["words"], m["wpm"], m["cps"]) == (int(n), float(wpm), float(cps)), text
        assert m["passed"]
        words += m["words"]
        speech += dur
    assert f"{words} words over {speech:.1f} s of speech" in EXAMPLES
    assert f"{words / speech * 60:.1f} WPM overall" in EXAMPLES
    assert f"({(15.0 - speech) / 15.0 * 100:.1f}%)" in EXAMPLES


def test_example_beats_file_parses():
    r = cc.analyze_beats(cc.parse_beats((SKILL_ROOT / "assets" / "beats-example.txt").read_text(encoding="utf-8")))
    assert r["passed"] and r["totals"]["words"] == 33


def test_kit_fetch_pins_the_current_version():
    """A card install fetches the kit by tag; the tag must match this file's version."""
    version = re.search(r'^\s+version:\s*"([\d.]+)"', SKILL, re.MULTILINE).group(1)
    fetch = re.search(
        r"git clone --depth 1 --branch v([\d.]+) "
        r"https://github\.com/8020DopamineMagic/motion-viral-director motion-viral-director",
        SKILL,
    )
    assert fetch, "SKILL.md section 0 must give the pinned kit fetch command"
    assert fetch.group(1) == version
