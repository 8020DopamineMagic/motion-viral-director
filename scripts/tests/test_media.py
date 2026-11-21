import json
import subprocess
import sys
from pathlib import Path

import pytest

import audit_media as am
import extract_contact_sheet as ecs
import screen_flashes as sf
from conftest import needs_ffmpeg

LOUDNORM_OK = """
[Parsed_loudnorm_0 @ 0x55d]
{
	"input_i" : "-14.20",
	"input_tp" : "-1.30",
	"input_lra" : "6.10",
	"input_thresh" : "-24.50",
	"output_i" : "-14.01",
	"output_tp" : "-1.00",
	"output_lra" : "5.90",
	"output_thresh" : "-24.30",
	"normalization_type" : "dynamic",
	"target_offset" : "0.01"
}
"""


def test_parse_loudnorm():
    m = am.parse_loudnorm(LOUDNORM_OK)
    assert (m["integrated_lufs"], m["true_peak_dbtp"], m["lra_lu"]) == (-14.2, -1.3, 6.1)
    with pytest.raises(ValueError):
        am.parse_loudnorm("ffmpeg said nothing useful")


def test_parse_loudnorm_silence():
    m = am.parse_loudnorm(LOUDNORM_OK.replace('"-14.20"', '"-inf"').replace('"-1.30"', '"-inf"'))
    assert m["integrated_lufs"] == float("-inf")


def test_parse_ebur128_short_term_max():
    log = ("[Parsed_ebur128_0 @ 0x1] t: 0.5 TARGET:-23 LUFS M: -20.1 S:-120.7 I: -20.1 LUFS LRA: 0.0 LU\n"
           "[Parsed_ebur128_0 @ 0x1] t: 3.0 TARGET:-23 LUFS M: -9.8 S: -10.4 I: -14.9 LUFS LRA: 3.0 LU\n"
           "[Parsed_ebur128_0 @ 0x1] t: 3.1 TARGET:-23 LUFS M: -12.0 S: -11.2 I: -14.8 LUFS LRA: 3.0 LU\n")
    assert am.parse_short_term_max(log) == -10.4
    assert am.parse_short_term_max("no frames") is None


PROBE_VERTICAL = {"video": {"width": 1080, "height": 1920, "fps": 30.0, "codec": "h264", "pix_fmt": "yuv420p"},
                  "audio": {"codec": "aac", "sample_rate": 48000, "channels": 2}, "duration_s": 42.0}


def status(result, check_id):
    return next(c["status"] for c in result["checks"] if c["id"] == check_id)


def test_evaluate_passing_social_master():
    r = am.evaluate(PROBE_VERTICAL, {"integrated_lufs": -15.6, "true_peak_dbtp": -1.4, "lra_lu": 5.0},
                    profile="social_short", aspect="9:16", short_term_max=-12.5)
    assert r["passed"] is True
    assert {c["status"] for c in r["checks"]} == {"pass"}


def test_evaluate_flags_hot_master_and_gives_fix_command():
    r = am.evaluate(PROBE_VERTICAL, {"integrated_lufs": -8.1, "true_peak_dbtp": 0.3, "lra_lu": 2.0},
                    profile="social_short", aspect="9:16", short_term_max=-6.0, source="in.mp4")
    assert r["passed"] is False
    assert status(r, "integrated_lufs") == "fail"
    assert status(r, "true_peak") == "fail"
    assert status(r, "short_term_jump") == "fail"
    assert "loudnorm=I=-16" in r["fix_command"] and "TP=-1.0" in r["fix_command"]


def test_youtube_only_penalises_too_loud_or_far_too_quiet():
    quiet_ok = am.evaluate(PROBE_VERTICAL, {"integrated_lufs": -15.2, "true_peak_dbtp": -2.0, "lra_lu": 7.0},
                           profile="youtube", aspect="9:16")
    assert status(quiet_ok, "integrated_lufs") == "pass"


def test_evaluate_aspect_and_missing_audio():
    r = am.evaluate(PROBE_VERTICAL, None, profile="youtube", aspect="16:9")
    assert status(r, "aspect_ratio") == "fail"
    silent = dict(PROBE_VERTICAL, audio=None)
    r = am.evaluate(silent, None, profile="youtube", aspect="9:16")
    assert status(r, "audio_stream") == "fail" and r["passed"] is False
    r = am.evaluate(silent, None, profile="youtube", aspect="9:16", allow_silent=True)
    assert status(r, "audio_stream") == "na" and r["passed"] is True


@needs_ffmpeg
def test_audit_real_loud_clip(media):
    p = subprocess.run([sys.executable, am.__file__, str(media["loud_vertical"]),
                        "--profile", "social_short", "--aspect", "9:16"], capture_output=True, text=True)
    out = json.loads(p.stdout)
    assert p.returncode == 1
    assert out["probe"]["video"]["width"] == 270 and out["probe"]["video"]["height"] == 480
    assert status(out, "aspect_ratio") == "pass"
    assert status(out, "integrated_lufs") == "fail"
    assert out["measured"]["integrated_lufs"] > -10


@needs_ffmpeg
def test_audit_real_silent_clip(media):
    p = subprocess.run([sys.executable, am.__file__, str(media["silent_landscape"]),
                        "--profile", "youtube", "--aspect", "16:9"], capture_output=True, text=True)
    out = json.loads(p.stdout)
    assert p.returncode == 1 and status(out, "audio_stream") == "fail"


def test_audit_missing_file_is_usage_error(tmp_path):
    p = subprocess.run([sys.executable, am.__file__, str(tmp_path / "nope.mp4")], capture_output=True, text=True)
    assert p.returncode == 2


# ---- contact sheets -------------------------------------------------------

def test_grid_plan_spans_whole_video():
    plan = ecs.plan_grid(duration_s=45.0, cols=4, rows=3)
    assert plan["tiles"] == 12
    assert plan["fps"] == pytest.approx(12 / 45.0)
    short = ecs.plan_grid(duration_s=0.2, cols=4, rows=3)
    assert short["fps"] > 0


@needs_ffmpeg
def test_contact_sheets_are_written(media, tmp_path):
    prefix = tmp_path / "audit"
    files = ecs.export_sheets(str(media["loud_vertical"]), str(prefix))
    for key in ("color", "grayscale", "squint", "hook"):
        assert Path(files[key]).exists() and Path(files[key]).stat().st_size > 500


# ---- flash screening ------------------------------------------------------

def strobe(period_frames, seconds=3, fps=30, lo=0.0, hi=1.0):
    half = period_frames // 2
    return [hi if (n % period_frames) < half else lo for n in range(seconds * fps)]


def test_flash_counting_pure():
    assert sf.max_flashes_per_second(strobe(6), fps=30) >= 4        # 5 Hz
    assert sf.max_flashes_per_second(strobe(30), fps=30) <= 2       # 1 Hz
    assert sf.max_flashes_per_second([0.5] * 90, fps=30) == 0       # steady
    assert sf.max_flashes_per_second(strobe(6, lo=0.50, hi=0.55), fps=30) == 0   # under 10% swing
    assert sf.max_flashes_per_second(strobe(6, lo=0.85, hi=1.0), fps=30) == 0    # darker state not below 0.80


def test_flash_verdict_requires_enough_area():
    fast, steady = strobe(6), [0.2] * 90
    small = sf.screen_cells([fast] + [steady] * 255, fps=30)         # 1 of 256 cells
    assert small["flagged"] is False
    big = sf.screen_cells([fast] * 64 + [steady] * 192, fps=30)      # 25% of frame
    assert big["flagged"] is True and big["max_flashes_per_second"] >= 4


@needs_ffmpeg
def test_flash_screen_on_real_clips(media):
    p = subprocess.run([sys.executable, sf.__file__, str(media["strobe_5hz"])], capture_output=True, text=True)
    out = json.loads(p.stdout)
    assert p.returncode == 1 and out["flagged"] is True
    assert "not a clearance" in out["note"]
    p = subprocess.run([sys.executable, sf.__file__, str(media["pulse_1hz"])], capture_output=True, text=True)
    assert p.returncode == 0 and json.loads(p.stdout)["flagged"] is False
