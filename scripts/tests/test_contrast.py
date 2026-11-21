import json
import subprocess
import sys
from pathlib import Path

import pytest

import check_contrast as ct

SCRIPT = Path(ct.__file__)


def test_extremes():
    assert ct.contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert ct.contrast_ratio("#3a3a3a", "#3A3A3A") == pytest.approx(1.0)
    assert ct.contrast_ratio("#fff", "#000") == pytest.approx(21.0)  # shorthand hex


# The palette the source document reports as "verified": these are regression fixtures.
@pytest.mark.parametrize("fg,bg,published", [
    ("#EDE6D6", "#0E131B", 14.98),
    ("#F29F3D", "#0E131B", 8.69),
    ("#F29F3D", "#253040", 6.22),
    ("#F7F4EC", "#0A0E14", 17.60),
])
def test_source_palette_ratios(fg, bg, published):
    assert ct.contrast_ratio(fg, bg) == pytest.approx(published, abs=0.01)


def test_wcag_thresholds():
    grey = ct.evaluate("#777777", "#FFFFFF")       # 4.48:1, the classic near miss
    assert grey["ratio"] == pytest.approx(4.48, abs=0.01)
    assert grey["aa_normal"] is False and grey["aa_large"] is True
    assert grey["passed"] is False
    assert ct.evaluate("#777777", "#FFFFFF", large=True)["passed"] is True
    assert ct.evaluate("#767676", "#FFFFFF")["passed"] is True  # 4.54:1


def test_failing_pair_gets_a_passing_suggestion():
    r = ct.evaluate("#8A8A8A", "#FFFFFF")
    assert r["passed"] is False
    assert ct.contrast_ratio(r["suggestion"], "#FFFFFF") >= 4.5


def test_scrim_worst_case_over_moving_footage():
    # White captions on a 60% black scrim: worst case is bright footage behind it.
    ok = ct.evaluate_scrim("#FFFFFF", "#000000", 0.6)
    assert ok["worst_case_bg"].upper() == "#666666"
    assert ok["ratio"] == pytest.approx(5.74, abs=0.01)
    assert ok["passed"] is True
    thin = ct.evaluate_scrim("#FFFFFF", "#000000", 0.3)
    assert thin["passed"] is False
    assert 0.3 < thin["min_alpha_for_aa"] <= 0.6


def test_invalid_hex():
    with pytest.raises(ValueError):
        ct.contrast_ratio("#GGGGGG", "#000000")
    with pytest.raises(ValueError):
        ct.contrast_ratio("12345", "#000000")


def test_cli(tmp_path):
    p = subprocess.run([sys.executable, str(SCRIPT), "--fg", "#EDE6D6", "--bg", "#0E131B"],
                       capture_output=True, text=True)
    assert p.returncode == 0 and json.loads(p.stdout)["results"][0]["ratio"] == pytest.approx(14.98, abs=0.01)
    p = subprocess.run([sys.executable, str(SCRIPT), "--pair", "#777777:#FFFFFF:body",
                        "--pair", "#000:#fff:headline"], capture_output=True, text=True)
    out = json.loads(p.stdout)
    assert p.returncode == 1 and [r["passed"] for r in out["results"]] == [False, True]
    p = subprocess.run([sys.executable, str(SCRIPT), "--fg", "#FFFFFF", "--scrim", "#000000@0.6"],
                       capture_output=True, text=True)
    assert p.returncode == 0
