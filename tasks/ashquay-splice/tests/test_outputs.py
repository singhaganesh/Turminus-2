"""Grade ashquay splice artifacts."""

import json
import shutil
import subprocess
from pathlib import Path

BIN = Path("/app/bin/ashquay")
CORE = Path("/app/dumpit/shift.core")
RUNA = Path("/app/outkeg/runA")
RUNB = Path("/app/outkeg/runB")
RUNH = Path("/app/outkeg/runH")


def _splice(core: Path, out: Path) -> subprocess.CompletedProcess:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    return subprocess.run(
        ["/app/bin/ashquay", "splice", str(core), str(out)],
        capture_output=True,
        text=True,
        check=False,
    )


def _bt(out: Path) -> str:
    return (out / "backtrace.txt").read_text()


def _prov(out: Path) -> dict:
    return json.loads((out / "provenance.json").read_text())


def _lined(text: str) -> int:
    n = 0
    for line in text.splitlines():
        if ":" in line.split()[-1] and "/" in line:
            n += 1
    return n


def test_aq01_magic_stock():
    """Linked mill is ELF and shift dump prints source rows after splice."""
    blob = BIN.read_bytes()
    assert blob[:4] == b"\x7fELF"
    rc = _splice(CORE, RUNA)
    assert rc.returncode == 0
    text = _bt(RUNA)
    assert "src/mod.c:10" in text
    assert "src/mod.c:20" in text
    assert "src/z.c:3" in text
    assert _lined(text) == 3


def test_aq02_twin_trees():
    """Two splice trees of the same dump are byte-identical."""
    a = _splice(CORE, RUNA)
    b = _splice(CORE, RUNB)
    assert a.returncode == 0 and b.returncode == 0
    assert (RUNA / "backtrace.txt").read_bytes() == (RUNB / "backtrace.txt").read_bytes()
    assert (RUNA / "provenance.json").read_bytes() == (RUNB / "provenance.json").read_bytes()


def test_aq03_row_host():
    """aabbccdd object names the well that supplied its line table."""
    assert _splice(CORE, RUNA).returncode == 0
    rows = {r["build_id"]: r["host"] for r in _prov(RUNA)["objects"]}
    assert rows["aabbccdd"] == "midquay"


def test_aq04_void_exit():
    """A dump whose build id no well holds exits non-zero."""
    core = Path("/tmp/void.core")
    core.write_text("ASHCORE1\nmod deadbeef 0x4000\npc 0x00004000\n")
    out = Path("/tmp/voidout")
    rc = _splice(core, out)
    assert rc.returncode != 0


def test_aq05_ok_flag():
    """A clean splice writes ok.mark after a line-bearing backtrace."""
    assert _splice(CORE, RUNA).returncode == 0
    assert (RUNA / "ok.mark").read_text() == "ok\n"
    assert "src/mod.c:10" in _bt(RUNA)


def test_aq09_key_shape():
    """Provenance objects use build_id and host keys with the used wells."""
    assert _splice(CORE, RUNA).returncode == 0
    objs = _prov(RUNA)["objects"]
    assert objs
    rows = {r["build_id"]: r["host"] for r in objs}
    for row in objs:
        assert set(row.keys()) == {"build_id", "host"}
        assert row["build_id"]
        assert row["host"]
    assert rows["aabbccdd"] == "midquay"
    assert rows["eeff0011"] == "deepwell"


def test_aq11_name_shape():
    """Frames use NAME at 0xADDR form, with source suffix when present."""
    assert _splice(CORE, RUNA).returncode == 0
    lines = _bt(RUNA).splitlines()
    assert lines
    assert lines[0].startswith("foo at 0x")
    assert "src/mod.c:10" in lines[0]
    assert " at 0x" in lines[1]


def test_aq06_held_row():
    """A held-out dump still prints its source row from the matching well."""
    core = Path("/tmp/hold.core")
    core.write_text("ASHCORE1\nmod 99887766 0x3000\npc 0x00003000\n")
    rc = _splice(core, RUNH)
    assert rc.returncode == 0
    text = _bt(RUNH)
    assert "src/q.c:9" in text
    hosts = [r["host"] for r in _prov(RUNH)["objects"]]
    assert "midquay" in hosts


def test_aq07_corrupt_again():
    """Corrupt outkeg files then one splice restores them."""
    assert _splice(CORE, RUNA).returncode == 0
    (RUNA / "backtrace.txt").write_text("junk\n")
    (RUNA / "provenance.json").write_text("{}\n")
    rc = subprocess.run(
        ["/app/bin/ashquay", "splice", "/app/dumpit/shift.core", "/app/outkeg/runA"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert rc.returncode == 0
    assert "src/mod.c:10" in _bt(RUNA)
    rows = {r["build_id"]: r["host"] for r in _prov(RUNA)["objects"]}
    assert rows["aabbccdd"] == "midquay"


def test_aq08_second_id():
    """eeff0011 object names the well that supplied its line table."""
    assert _splice(CORE, RUNA).returncode == 0
    rows = {r["build_id"]: r["host"] for r in _prov(RUNA)["objects"]}
    assert rows["eeff0011"] == "deepwell"


def test_aq10_void_nomark():
    """A rejected dump does not leave ok.mark."""
    core = Path("/tmp/void2.core")
    core.write_text("ASHCORE1\nmod deadbeef 0x4000\npc 0x00004000\n")
    out = Path("/tmp/voidout2")
    if out.exists():
        shutil.rmtree(out)
    rc = _splice(core, out)
    assert rc.returncode != 0
    leftover = list(out.glob("ok.mark"))
    assert leftover == []


def test_aq12_one_proc():
    """One splice argv fills both products in a single process."""
    if RUNA.exists():
        shutil.rmtree(RUNA)
    RUNA.mkdir(parents=True)
    rc = subprocess.run(
        ["/app/bin/ashquay", "splice", "/app/dumpit/shift.core", "/app/outkeg/runA"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert rc.returncode == 0
    assert (RUNA / "backtrace.txt").is_file()
    assert (RUNA / "provenance.json").is_file()
    assert "src/z.c:3" in _bt(RUNA)
