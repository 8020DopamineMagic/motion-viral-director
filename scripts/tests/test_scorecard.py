import json
import subprocess
import sys
from pathlib import Path

import pytest

import qa_scorecard as qa
from conftest import SKILL_ROOT

SCRIPT = Path(qa.__file__)


def test_init_starts_everything_pending():
    card = qa.new_scorecard("demo", "9:16_short", platforms=["tiktok"])
    assert card["format"] == "9:16_short"
    applicable = [c for c in card["checks"].values() if c["status"] != "na"]
    assert applicable and all(c["status"] == "pending" for c in applicable)
    assert card["checks"]["safe_zones.inside"]["status"] == "pending"


def test_format_decides_what_is_not_applicable():
    long_form = qa.new_scorecard("essay", "16:9_long")
    assert long_form["checks"]["safe_zones.inside"]["status"] == "na"
    assert long_form["checks"]["hook.loop_seam"]["status"] == "na"
    assert long_form["checks"]["hook.promise_match"]["status"] == "pending"
    short = qa.new_scorecard("short", "9:16_short")
    assert short["checks"]["hook.promise_match"]["status"] == "na"


def test_verdicts():
    card = qa.new_scorecard("demo", "9:16_short")
    assert qa.report(card)["verdict"] == "NOT READY: CHECKS PENDING"
    for c in card["checks"].values():
        if c["status"] == "pending":
            c.update(status="pass", method="inspected", evidence="looked at it")
    assert qa.report(card)["verdict"] == "READY"
    card["checks"]["wcag.contrast"].update(status="fail", value=3.1)
    r = qa.report(card)
    assert r["verdict"] == "BLOCKED" and "wcag.contrast" in [f["id"] for f in r["failed"]]


def test_numeric_value_overrules_an_optimistic_status():
    card = qa.new_scorecard("demo", "9:16_short")
    card["checks"]["captions.max_wpm"].update(status="pass", value=212, method="computed", evidence="script")
    r = qa.report(card)
    assert "captions.max_wpm" in [f["id"] for f in r["failed"]]
    assert any("212" in p for p in r["problems"])


def test_pass_needs_evidence_and_a_method():
    card = qa.new_scorecard("demo", "9:16_short")
    card["checks"]["hierarchy.grayscale"]["status"] = "pass"
    r = qa.report(card)
    assert any("hierarchy.grayscale" in p and "evidence" in p for p in r["problems"])
    assert r["verdict"] != "READY"


def test_audio_target_follows_format():
    short = qa.new_scorecard("s", "9:16_short")
    short["checks"]["audio.integrated_lufs"].update(status="pass", value=-16.2, method="measured", evidence="audit_media")
    assert "audio.integrated_lufs" not in [f["id"] for f in qa.report(short)["failed"]]
    short["checks"]["audio.integrated_lufs"]["value"] = -9.0
    assert "audio.integrated_lufs" in [f["id"] for f in qa.report(short)["failed"]]


def test_markdown_separates_executed_from_pending():
    card = qa.new_scorecard("demo", "16:9_long")
    card["checks"]["wcag.contrast"].update(status="pass", value=14.98, method="computed", evidence="check_contrast.py")
    md = qa.to_markdown(qa.report(card), card)
    assert "## Checks executed" in md and "## Checks pending" in md
    assert md.index("wcag.contrast") < md.index("## Checks pending")
    assert "14.98" in md


def test_malformed_scorecard_is_rejected():
    with pytest.raises(ValueError):
        qa.report({"project_id": "x", "format": "9:16_short", "checks": {"made.up": {"status": "pass"}}})
    with pytest.raises(ValueError):
        qa.report({"project_id": "x", "format": "vertical", "checks": {}})
    card = qa.new_scorecard("demo", "9:16_short")
    card["checks"]["wcag.contrast"]["status"] = "maybe"
    with pytest.raises(ValueError):
        qa.report(card)


def test_schema_file_accepts_fresh_scorecards():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((SKILL_ROOT / "assets" / "qa-scorecard.schema.json").read_text())
    for fmt in qa.FORMATS:
        jsonschema.validate(qa.new_scorecard("demo", fmt), schema)
    bad = qa.new_scorecard("demo", "9:16_short")
    bad["checks"]["wcag.contrast"]["status"] = "maybe"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_cli_roundtrip(tmp_path):
    card = tmp_path / "card.json"
    p = subprocess.run([sys.executable, str(SCRIPT), "init", "--project", "demo", "--format", "9:16_short",
                        "--out", str(card)], capture_output=True, text=True)
    assert p.returncode == 0 and card.exists()
    p = subprocess.run([sys.executable, str(SCRIPT), "set", str(card), "wcag.contrast", "pass",
                        "--value", "7.2", "--method", "computed", "--evidence", "check_contrast.py"],
                       capture_output=True, text=True)
    assert p.returncode == 0
    p = subprocess.run([sys.executable, str(SCRIPT), "report", str(card)], capture_output=True, text=True)
    assert p.returncode == 3 and json.loads(p.stdout)["verdict"] == "NOT READY: CHECKS PENDING"
    p = subprocess.run([sys.executable, str(SCRIPT), "set", str(card), "wcag.flashes", "fail", "--value", "5",
                        "--method", "measured", "--evidence", "screen_flashes.py"], capture_output=True, text=True)
    p = subprocess.run([sys.executable, str(SCRIPT), "report", str(card), "--md"], capture_output=True, text=True)
    assert p.returncode == 1 and "BLOCKED" in p.stdout
