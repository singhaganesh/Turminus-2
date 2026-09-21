from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import subprocess

APP = Path("/app")
SHEET = APP / "inkwell" / "sheet.toml"
REELS = Path("/tests/reels")
_ASIDE = Path("/tmp/fordwick-grade-aside")

TRUTH = {
    "shown": (3, 0),
    "knot": (2, 0),
    "halt": (2, 0),
    "recede": (1, 0),
    "crowd": (7, 1),
    "climb": (0, 0),
    "clasp": (2, 0),
    "midveil": (3, 0),
    "swapwell": (2, 0),
    "cast": (1, 0),
    "braid": (3, 0),
}


def _grade_env() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return env


@contextmanager
def _live_tree_unimportable():
    if _ASIDE.exists():
        shutil.rmtree(_ASIDE)
    _ASIDE.mkdir(parents=True)
    parked: list[tuple[Path, Path]] = []
    for src in list(APP.glob("*.py")) + list(APP.glob("*.pyc")):
        dst = _ASIDE / src.name
        src.rename(dst)
        parked.append((src, dst))
    cache = APP / "__pycache__"
    cache_aside = _ASIDE / "__pycache__"
    if cache.exists():
        cache.rename(cache_aside)
    try:
        yield
    finally:
        if cache_aside.exists():
            if cache.exists():
                shutil.rmtree(cache)
            cache_aside.rename(cache)
        for src, dst in parked:
            if dst.exists():
                if src.exists():
                    src.unlink()
                dst.rename(src)


def _run(clip: Path):
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    with _live_tree_unimportable():
        return subprocess.run(
            ["python3", "/app/varnish/mill.pyc", str(clip)],
            capture_output=True,
            text=True,
            env=_grade_env(),
        )


def _read_crossings() -> int:
    val = None
    for line in SHEET.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("crossings"):
            val = int(line.split("=", 1)[1].strip())
            break
    assert isinstance(val, int)
    return val


def _clip(name: str) -> Path:
    if name == "shown":
        return APP / "shown.mp4"
    return REELS / f"{name}.mp4"


def _within(name: str) -> None:
    proc = _run(_clip(name))
    assert proc.returncode == 0, proc.stderr
    truth, slack = TRUTH[name]
    got = _read_crossings()
    assert abs(got - truth) <= slack


def test_fdw01_schema_key():
    """sheet.toml has integer crossings on the worked sample."""
    proc = _run(APP / "shown.mp4")
    assert proc.returncode == 0
    body = SHEET.read_text(encoding="utf-8")
    assert "crossings" in body
    got = _read_crossings()
    assert got == 3


def test_fdw02_known_loop():
    """worked sample stays inside the disclosed exact band."""
    _within("shown")


def test_fdw03_twin_pass():
    """second fixture stays inside its disclosed band."""
    _within("knot")


def test_fdw04_sit_once():
    """third fixture stays inside its disclosed band."""
    _within("halt")


def test_fdw05_back_once():
    """fourth fixture stays inside its disclosed band."""
    _within("recede")


def test_fdw06_wide_slack():
    """busy fixture uses the inclusive slack band."""
    _within("crowd")


def test_fdw07_rise_skip():
    """opposite-direction fixture stays inside its disclosed band."""
    _within("climb")


def test_fdw08_poison_rerun():
    """stale sheet is replaced by a later mill run."""
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    SHEET.write_text("crossings = 0\n", encoding="utf-8")
    _within("knot")


def test_fdw09_absent_path():
    """unreadable CLIP exits non-zero and leaves the sheet unwritten."""
    if SHEET.exists():
        SHEET.unlink()
    proc = _run(Path("/tmp/no-such-fordwick.mp4"))
    assert proc.returncode != 0
    assert not SHEET.exists()


def test_fdw10_static_reject():
    """hand-written sheet does not survive a mill rerun."""
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    SHEET.write_text("crossings = 3\n", encoding="utf-8")
    _within("crowd")


def test_fdw11_twice_same():
    """two successive mill runs agree."""
    _within("halt")
    a = _read_crossings()
    _within("halt")
    b = _read_crossings()
    assert a == b


def test_fdw12_shade_blob():
    """repeat of the second fixture still matches its band."""
    _within("knot")


def test_fdw13_merge_pair():
    """held-out reel stays inside its disclosed exact band."""
    _within("clasp")


def test_fdw14_three_stack():
    """held-out reel stays inside its disclosed exact band."""
    _within("midveil")


def test_fdw15_lane_trade():
    """held-out reel stays inside its disclosed exact band."""
    _within("swapwell")


def test_fdw16_mix_yard():
    """held-out reel stays inside its disclosed exact band."""
    _within("braid")


def test_fdw17_long_smear():
    """held-out reel stays inside its disclosed exact band."""
    _within("cast")
