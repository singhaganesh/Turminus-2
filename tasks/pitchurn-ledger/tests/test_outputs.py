"""Verifier for pitchurn silo tally artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

TALLY = Path("/app/urnbay/tally.json")
STABLE = Path("/app/filmwelle/stable.bin")
PLAIN = Path("/app/filmwelle/plain.bin")
BRINE = Path("/app/filmwelle/brine.bin")
PROBE = Path("/app/filmwelle/probe.bin")
SEED = Path("/app/seed/urnbay")
URN = Path("/app/urnbay")


def _anneal() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/app/bin/pitchurn", "anneal"],
        capture_output=True,
        text=True,
    )


def _restore() -> None:
    if URN.exists():
        shutil.rmtree(URN)
    shutil.copytree(SEED, URN)


def _prepare() -> None:
    _restore()
    _anneal()


def _stow(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/app/bin/pitchurn", "stow", path.as_posix()],
        capture_output=True,
        text=True,
    )


def _draw(dest: Path, src: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/app/bin/pitchurn", "draw", dest.as_posix(), src.as_posix()],
        capture_output=True,
        text=True,
    )


def _census() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/app/bin/pitchurn", "census"],
        capture_output=True,
        text=True,
    )


def _tally() -> dict:
    return json.loads(TALLY.read_text())


def test_pu01_twice_blob():
    """Second stow of stable.bin keeps reuse_frac at or above 0.80."""
    _prepare()
    r = _stow(STABLE)
    assert float(json.loads(TALLY.read_text())["reuse_frac"]) >= 0.80
    assert r.returncode < 1


def test_pu02_held_frac():
    """Second stow of plain.bin keeps reuse_frac at or above 0.80."""
    _prepare()
    _stow(PLAIN)
    t = _tally()
    assert float(t["reuse_frac"]) >= 0.80


def test_pu03_fresh_span():
    """Never-seen probe.bin has mean_piece at or below 2048."""
    _prepare()
    _stow(PROBE)
    t = _tally()
    assert float(t["mean_piece"]) <= 2048.0
    assert t["reel"] == PROBE.name


def test_pu03b_holdout_span():
    """Never-seen holdout reel has mean_piece at or below 2048."""
    _prepare()
    p = Path("/app/urnbay/held.bin")
    data = bytearray()
    for i in range(24000):
        if i % 11 == 0:
            data.append(0x80 + (i % 90))
        else:
            data.append(ord("m") + (i % 9))
    p.write_bytes(bytes(data))
    _stow(p)
    t = _tally()
    assert float(t["mean_piece"]) <= 2048.0
    assert t["reel"] == p.name


def test_pu04_sink_match():
    """draw of plain.bin matches source bytes after a reuse stow."""
    _prepare()
    _stow(PLAIN)
    assert float(_tally()["reuse_frac"]) >= 0.80
    dest = Path("/app/urnbay/plain.out")
    d = _draw(dest, PLAIN)
    assert dest.read_bytes() == PLAIN.read_bytes()
    assert d.returncode < 1


def test_pu05_dirty_exit():
    """Full new copy of already-siloed stable.bin must not exit 0."""
    _prepare()
    r = _stow(STABLE)
    t = json.loads(TALLY.read_text())
    assert float(t["reuse_frac"]) >= 0.80
    stored = int(t["bytes_stored"])
    incoming = int(t["bytes_in"])
    assert stored < incoming
    assert r.returncode != 0 or stored != incoming


def test_pu06_card_keys():
    """tally.json exposes the six named keys as strings after brine stow."""
    _prepare()
    _stow(BRINE)
    t = _tally()
    for k in ("reel", "bytes_in", "bytes_stored", "reuse_frac", "mean_piece", "piece_count"):
        assert k in t
        assert isinstance(t[k], str)
    assert float(t["reuse_frac"]) >= 0.80


def test_pu07_hi_bit():
    """Second stow of brine.bin keeps reuse_frac at or above 0.80."""
    _prepare()
    _stow(BRINE)
    t = _tally()
    assert float(t["reuse_frac"]) >= 0.80


def test_pu08_cold_keep():
    """stable.bin restow stores far fewer bytes than bytes_in."""
    _prepare()
    _stow(STABLE)
    t = _tally()
    assert int(t["bytes_stored"]) < int(t["bytes_in"])


def test_pu09_once_pass():
    """One stow process of plain.bin is enough for reuse_frac."""
    _prepare()
    _stow(PLAIN)
    assert float(_tally()["reuse_frac"]) >= 0.80


def test_pu10_zz_corrupt():
    """Corrupt tally then stow stable.bin still recovers reuse."""
    _prepare()
    TALLY.write_text("{}\n")
    _stow(STABLE)
    t = _tally()
    assert "reuse_frac" in t
    assert float(t["reuse_frac"]) >= 0.80


def test_pu11_card_obj():
    """census rewrites tally.json after a reuse stow of plain.bin."""
    _prepare()
    _stow(PLAIN)
    assert float(_tally()["reuse_frac"]) >= 0.80
    TALLY.write_text("{}\n")
    c = _census()
    assert c.returncode < 1
    t = _tally()
    assert float(t["reuse_frac"]) >= 0.80
    assert t["reel"] == PLAIN.name


def test_pu12_floor_ignored():
    """MIN.txt floor 0.00 is not enough; brine reuse_frac still needs 0.80."""
    _prepare()
    _stow(BRINE)
    assert float(_tally()["reuse_frac"]) >= 0.80
