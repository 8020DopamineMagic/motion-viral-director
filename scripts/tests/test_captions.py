import json
import subprocess
import sys
from pathlib import Path

import pytest

import validate_captions as vc

SCRIPT = Path(vc.__file__)


def srt(*cues):
    """cues: (start, end, text) with 'HH:MM:SS,mmm' stamps."""
    return "\n\n".join(f"{i}\n{s} --> {e}\n{t}" for i, (s, e, t) in enumerate(cues, 1)) + "\n"


def codes(result, severity=None):
    return {i["code"] for c in result["cues"] for i in c["issues"]
            if severity is None or i["severity"] == severity}


GOOD_VERTICAL = srt(("00:00:00,000", "00:00:01,200", "Your phone rang"),
                    ("00:00:01,200", "00:00:02,600", "at 2:14 PM"))


def test_clean_vertical_captions_pass():
    r = vc.validate(GOOD_VERTICAL, aspect="9:16")
    assert r["passed"] is True
    assert r["summary"]["errors"] == 0
    assert r["summary"]["cues"] == 2
    assert r["cues"][0]["wpm"] == pytest.approx(150.0, abs=0.1)


def test_source_document_example_metrics():
    # "3:14" opening line from the source: 8 words over 2.7 s = 177.8 WPM, 15.9 CPS.
    r = vc.validate(srt(("00:00:00,500", "00:00:03,200",
                         "At 3:14, every clock\nin the harbor stopped—")), aspect="16:9")
    cue = r["cues"][0]
    assert cue["words"] == 8
    assert cue["wpm"] == pytest.approx(177.8, abs=0.1)
    assert cue["sec_per_word"] == pytest.approx(0.34, abs=0.01)
    assert r["passed"] is True


def test_line_too_long_for_vertical_is_error():
    r = vc.validate(srt(("00:00:00,000", "00:00:04,000",
                         "This caption line is far too long for vertical")), aspect="9:16")
    assert "line_length" in codes(r, "error")
    assert r["passed"] is False


def test_same_line_is_fine_on_landscape_netflix_but_not_bbc():
    text = srt(("00:00:00,000", "00:00:04,000", "This caption line is forty-one chars long"))
    assert len("This caption line is forty-one chars long") == 41
    assert vc.validate(text, aspect="16:9")["passed"] is True
    assert "line_length" in codes(vc.validate(text, aspect="16:9", standard="bbc"), "error")


def test_reading_speed_errors():
    r = vc.validate(srt(("00:00:00,000", "00:00:01,200", "five quick words go here")), aspect="16:9")
    got = codes(r, "error")
    assert "wpm" in got and "sec_per_word" in got
    r = vc.validate(srt(("00:00:00,000", "00:00:01,500",
                         "Extraordinarily complicated\nterminology everywhere")), aspect="16:9")
    assert "cps" in codes(r, "error")


def test_children_audience_lowers_cps_ceiling():
    text = srt(("00:00:00,000", "00:00:02,000", "abcdefgh abcdefgh abcdefgh abcdefghi"))  # 36 chars = 18 CPS
    assert "cps" not in codes(vc.validate(text, aspect="16:9"))
    assert "cps" in codes(vc.validate(text, aspect="16:9", audience="children"), "error")


def test_duration_bounds():
    long_cue = srt(("00:00:00,000", "00:00:08,000", "This one sits on screen far too long"))
    assert "max_duration" in codes(vc.validate(long_cue, aspect="16:9"), "error")
    short_cue = srt(("00:00:00,000", "00:00:00,500", "Boom"))
    assert "min_duration" in codes(vc.validate(short_cue, aspect="16:9"), "error")
    # Word-by-word kinetic captions are normal on vertical: advisory only, still passes.
    r = vc.validate(short_cue, aspect="9:16")
    assert "min_duration" in codes(r, "warning")
    assert r["passed"] is True
    assert "min_duration" in codes(vc.validate(short_cue, aspect="9:16", style="subtitle"), "error")


def test_too_many_lines():
    text = srt(("00:00:00,000", "00:00:05,000", "one line\ntwo line\nthree line"))
    assert "line_count" in codes(vc.validate(text, aspect="16:9"), "error")
    assert "line_count" not in codes(vc.validate(text, aspect="9:16"))


def test_overlap_and_bad_timing():
    text = srt(("00:00:00,000", "00:00:02,000", "first cue here"),
               ("00:00:01,500", "00:00:03,500", "second cue here"))
    assert "overlap" in codes(vc.validate(text, aspect="16:9"), "error")
    text = srt(("00:00:02,000", "00:00:02,000", "zero length"))
    assert "bad_timing" in codes(vc.validate(text, aspect="16:9"), "error")


def test_markup_is_not_counted():
    text = srt(("00:00:00,000", "00:00:02,000", "<i>Hello</i> {\\an8}world"))
    cue = vc.validate(text, aspect="16:9")["cues"][0]
    assert cue["chars"] == len("Hello world")


def test_weak_line_break_is_warning():
    text = srt(("00:00:00,000", "00:00:03,000", "I walked to the\nstore today"))
    r = vc.validate(text, aspect="16:9")
    assert "weak_line_break" in codes(r, "warning")
    assert r["passed"] is True


def test_webvtt_and_dot_separators():
    vtt = "WEBVTT\n\nintro\n00:00.000 --> 00:01.500\nHello there friend\n\n00:01.500 --> 00:03.000\nSecond cue lands\n"
    r = vc.validate(vtt, aspect="16:9")
    assert r["summary"]["cues"] == 2
    assert r["cues"][0]["dur_s"] == pytest.approx(1.5)


def test_overrides_and_square_formats():
    text = srt(("00:00:00,000", "00:00:04,000", "This line is thirty characters."))
    assert "line_length" in codes(vc.validate(text, aspect="1:1"), "error")
    assert "line_length" not in codes(vc.validate(text, aspect="1:1", max_cpl=32))


def test_empty_input_fails_loudly():
    r = vc.validate("not a caption file", aspect="9:16")
    assert r["passed"] is False
    assert r["summary"]["cues"] == 0
    assert "no_cues" in r["summary"]["notes"][0]


def test_cli_exit_codes(tmp_path):
    good = tmp_path / "good.srt"
    good.write_text(GOOD_VERTICAL, encoding="utf-8")
    bad = tmp_path / "bad.srt"
    bad.write_text(srt(("00:00:00,000", "00:00:01,000",
                        "way too many words crammed into one second")), encoding="utf-8")
    ok = subprocess.run([sys.executable, str(SCRIPT), str(good), "--aspect", "9:16"],
                        capture_output=True, text=True)
    assert ok.returncode == 0 and json.loads(ok.stdout)["passed"] is True
    ko = subprocess.run([sys.executable, str(SCRIPT), str(bad), "--aspect", "9:16"],
                        capture_output=True, text=True)
    assert ko.returncode == 1 and json.loads(ko.stdout)["passed"] is False
    missing = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path / "nope.srt")],
                             capture_output=True, text=True)
    assert missing.returncode == 2
