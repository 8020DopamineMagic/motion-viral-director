"""Shared test setup: make the scripts importable and provide ffmpeg fixtures."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL_ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
needs_ffmpeg = pytest.mark.skipif(not HAVE_FFMPEG, reason="ffmpeg/ffprobe not on PATH")


def _ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


@pytest.fixture(scope="session")
def media(tmp_path_factory):
    """Tiny synthetic clips built once per session. Returns a dict of paths."""
    if not HAVE_FFMPEG:
        pytest.skip("ffmpeg/ffprobe not on PATH")
    d = tmp_path_factory.mktemp("media")
    out = {}

    # 4 s vertical clip with a full-scale sine: far louder than any delivery target.
    out["loud_vertical"] = d / "loud_vertical.mp4"
    _ffmpeg("-f", "lavfi", "-i", "testsrc2=size=270x480:rate=30:duration=4",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
            "-af", "volume=18dB", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", str(out["loud_vertical"]))

    # 4 s landscape clip with no audio stream at all.
    out["silent_landscape"] = d / "silent_landscape.mp4"
    _ffmpeg("-f", "lavfi", "-i", "testsrc2=size=480x270:rate=30:duration=4",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out["silent_landscape"]))

    # 3 s full-frame black/white strobe at 5 Hz (period 6 frames at 30 fps).
    out["strobe_5hz"] = d / "strobe_5hz.mp4"
    _ffmpeg("-f", "lavfi", "-i", "color=c=black:size=160x284:rate=30:duration=3",
            "-vf", "geq=lum='255*lt(mod(N,6),3)':cb=128:cr=128",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-qp", "0", str(out["strobe_5hz"]))

    # 3 s slow pulse at 1 Hz (period 30 frames): flashes, but under the limit.
    out["pulse_1hz"] = d / "pulse_1hz.mp4"
    _ffmpeg("-f", "lavfi", "-i", "color=c=black:size=160x284:rate=30:duration=3",
            "-vf", "geq=lum='255*lt(mod(N,30),15)':cb=128:cr=128",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-qp", "0", str(out["pulse_1hz"]))
    return out
