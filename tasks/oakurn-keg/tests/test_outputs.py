"""Verifier for oakurn pour, steep, and board artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

BIN = Path("/app/bin/oakurn")
URN = Path("/app/caskbay")
LIVE = Path("/app/snapvat/live")
PANE = Path("/app/inkpit/counts.json")
CORE = URN / "core.urn"
QUIET = URN / "quiet.urn"


@pytest.fixture(autouse=True)
def _restore():
    if LIVE.exists():
        shutil.rmtree(LIVE)
    LIVE.mkdir(parents=True)
    shutil.copy(QUIET, LIVE / "quiet.urn")
    PANE.write_text('{"days":{"2024-03-12":2},"covers":"quiet"}\n')
    Path("/app/snapvat/last.id").write_text("quiet\n")
    Path("/app/snapvat/busy.latch").write_text("1\n")
    Path("/app/snapvat/emit.prev").write_text("")
    Path("/app/snapvat/tick").write_text("0\n")
    Path("/app/snapvat/poured.txt").write_text("")
    yield


def _load():
    return json.loads(PANE.read_text())


def test_aa_magic_stock():
    """Linked mill is ELF and a pour plus steep records mill work."""
    blob = BIN.read_bytes()
    assert blob[:4] == b"\x7fELF"
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/core.urn"], capture_output=True, text=True).returncode == 0
    prev = Path("/app/inkpit/emit.inc").read_text() if Path("/app/inkpit/emit.inc").exists() else ""
    r = subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True)
    assert r.returncode == 0
    emit = Path("/app/inkpit/emit.inc").read_text()
    assert emit != prev


def test_bb_id_mark():
    """After pour, steep sets covers to that urn identifier."""
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/core.urn"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True).returncode == 0
    data = _load()
    assert "covers" in PANE.read_text()
    assert data["covers"] == "core"


def test_cc_held_row():
    """A grade-time urn identifier lands in covers after one steep."""
    extra = URN / "z9.urn"
    extra.write_text("URN1\nid z9\nday 1999-01-01\nn 5\n")
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/z9.urn"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True).returncode == 0
    assert _load()["covers"] == "z9"


def test_dd_idle_nonzero():
    """A second steep with no new mill work exits non-zero."""
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/core.urn"], capture_output=True, text=True).returncode == 0
    first = subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True)
    assert first.returncode == 0
    second = subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True)
    assert second.returncode != 0


def test_ee_corrupt_regen():
    """Corrupt pane JSON then one steep restores an object with days."""
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/core.urn"], capture_output=True, text=True).returncode == 0
    PANE.write_text("{}\n")
    r = subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True)
    assert r.returncode == 0
    data = _load()
    assert "days" in data
    assert isinstance(data["days"], dict)


def test_ff_clock_key():
    """Events land on the urn day field, not the mill wall stamp."""
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/core.urn"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True).returncode == 0
    days = _load()["days"]
    assert days.get("2024-03-11") == 3
    assert days.get("2024-03-12") != 5


def test_gg_twin_key():
    """Quiet and core urns keep separate calendar keys."""
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/core.urn"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True).returncode == 0
    days = _load()["days"]
    assert days.get("2024-03-10") == 2
    assert days.get("2024-03-11") == 3


def test_hh_busy_still():
    """Steep still folds while snapvat busy.latch is present."""
    Path("/app/snapvat/busy.latch").write_text("1\n")
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/core.urn"], capture_output=True, text=True).returncode == 0
    r = subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True)
    assert r.returncode == 0
    assert Path("/app/inkpit/emit.inc").exists()
    assert (LIVE / "core.urn").is_file()


def test_ii_one_proc():
    """A single steep subprocess writes emit.inc after pour."""
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/core.urn"], capture_output=True, text=True).returncode == 0
    r = subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True)
    assert r.returncode == 0
    assert Path("/app/inkpit/emit.inc").stat().st_size > 0


def test_jj_panel_read():
    """board prints the regenerated object including covers."""
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/core.urn"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True).returncode == 0
    r = subprocess.run(["/app/bin/oakurn", "board"], capture_output=True, text=True)
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["covers"] == "core"


def test_kk_extra_row():
    """Held-out urn day total appears after pour and steep."""
    extra = URN / "z9.urn"
    extra.write_text("URN1\nid z9\nday 1999-01-01\nn 5\n")
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/z9.urn"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True).returncode == 0
    days = _load()["days"]
    assert days.get("1999-01-01") == 5
    assert _load()["covers"] == "z9"


def test_ll_key_order():
    """Serialized object lists days before covers."""
    assert subprocess.run(["/app/bin/oakurn", "pour", "/app/caskbay/core.urn"], capture_output=True, text=True).returncode == 0
    assert subprocess.run(["/app/bin/oakurn", "steep"], capture_output=True, text=True).returncode == 0
    text = PANE.read_text()
    assert text.index("days") < text.index("covers")
    days = json.loads(text)["days"]
    assert "2024-03-11" in days
