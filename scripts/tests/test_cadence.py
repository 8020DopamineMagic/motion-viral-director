import json
import subprocess
import sys
from pathlib import Path

import pytest

import check_cadence as cc

SCRIPT = Path(cc.__file__)

# The annotated 15-second opening from the source document. Its published figures
# (33 words, 12.7 s speech, 155.9 WPM, peak 177.8 WPM / 17.1 CPS) are the fixture.
OPENING = """\
# timecode | spoken copy (blank = no speech)
00:00.0-00:00.5 |
00:00.5-00:03.2 | At 3:14, every clock in the harbor stopped—
00:03.2-00:06.6 | except the brass chronometer nobody wound for forty years.
00:06.6-00:08.4 |
00:08.4-00:11.8 | My grandfather built it to outlive a winter gale.
00:11.8–00:15.0 | Tonight, its second hand started running backward.
"""


def test_single_line_measure():
    m = cc.measure("At 3:14, every clock in the harbor stopped—", 2.7)
    assert m["words"] == 8
    assert m["wpm"] == pytest.approx(177.8, abs=0.1)
    assert m["cps"] == pytest.approx(15.9, abs=0.1)
    assert m["passed"] is True


def test_source_opening_reproduces_published_numbers():
    r = cc.analyze_beats(cc.parse_beats(OPENING))
    t = r["totals"]
    assert t["words"] == 33
    assert t["speech_s"] == pytest.approx(12.7, abs=0.01)
    assert t["runtime_s"] == pytest.approx(15.0, abs=0.01)
    assert t["overall_wpm"] == pytest.approx(155.9, abs=0.1)
    assert t["breathing_room_pct"] == pytest.approx(15.3, abs=0.1)
    assert max(b["wpm"] for b in r["beats"] if b["words"]) == pytest.approx(177.8, abs=0.1)
    assert max(b["cps"] for b in r["beats"] if b["words"]) == pytest.approx(17.1, abs=0.1)
    assert r["passed"] is True


def test_overall_pace_above_baseline_is_advisory_not_blocking():
    r = cc.analyze_beats(cc.parse_beats(OPENING))
    assert any(w["code"] == "above_conversational_baseline" for w in r["warnings"])


def test_rushed_beat_fails():
    r = cc.analyze_beats(cc.parse_beats(
        "0-3 | one two three four five six seven eight nine ten eleven twelve"))
    assert r["passed"] is False
    assert {i["code"] for i in r["beats"][0]["issues"]} >= {"wpm", "sec_per_word"}


def test_no_breathing_room_is_flagged():
    r = cc.analyze_beats(cc.parse_beats("0-6 | this is a calm line of twelve words that fills every second"))
    assert any(w["code"] == "low_breathing_room" for w in r["warnings"])


@pytest.mark.parametrize("stamp,seconds", [
    ("12.7", 12.7), ("1:02.5", 62.5), ("00:01:02,500", 62.5), ("0:00", 0.0), ("01:00:00.000", 3600.0)])
def test_timecode_parsing(stamp, seconds):
    assert cc.parse_time(stamp) == pytest.approx(seconds)


def test_bad_beat_lines_raise_with_line_number():
    with pytest.raises(ValueError, match="line 2"):
        cc.parse_beats("0-1 | fine\nthis is not a beat\n")
    with pytest.raises(ValueError, match="end"):
        cc.parse_beats("5-3 | backwards")


def test_fit_estimate():
    f = cc.fit(words=105, runtime_s=45, wpm=140)
    assert f["speech_s"] == pytest.approx(45.0)
    assert f["fits"] is False  # no breathing room left
    assert f["max_words"] == 89  # 45 s * 85% * 140 wpm / 60, floored
    assert cc.fit(words=85, runtime_s=45, wpm=140)["fits"] is True


def test_cli_modes(tmp_path):
    beats = tmp_path / "beats.txt"
    beats.write_text(OPENING, encoding="utf-8")
    p = subprocess.run([sys.executable, str(SCRIPT), "--beats", str(beats)], capture_output=True, text=True)
    assert p.returncode == 0 and json.loads(p.stdout)["totals"]["words"] == 33
    p = subprocess.run([sys.executable, str(SCRIPT), "--text", "one two three four five six", "--seconds", "1"],
                       capture_output=True, text=True)
    assert p.returncode == 1
    p = subprocess.run([sys.executable, str(SCRIPT), "--text", "word " * 105, "--runtime", "45"],
                       capture_output=True, text=True)
    assert p.returncode == 1 and json.loads(p.stdout)["fits"] is False


# Iteration 2: one counting rule, the stricter one.

def test_hyphenated_words_count_as_spoken_words():
    assert cc.count_words("forty-seven years, one-nine") == 5


def test_numerals_and_acronyms_get_a_spoken_count_note():
    m = cc.measure("Call HVAC at 3:14 for $400", 2.0)
    assert any(n["code"] == "spoken_count" for n in m.get("notes", []))
    assert m["passed"] is True  # a note, not a failure


def test_plain_words_get_no_note():
    assert cc.measure("Your phone rang twice", 2.0).get("notes", []) == []
