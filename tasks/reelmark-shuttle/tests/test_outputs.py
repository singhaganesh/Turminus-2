"""Nockreel pour/spin contract verifier."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

KNIT_OK = Path("/app/emitwell/knit/knit.ok")
CAPSET = Path("/app/emitwell/knit/capset.tbl")
LOADED_SET = Path("/app/reelcli/run/loaded.set")
ACCEPT = Path("/app/reelcli/run/accept.ok")
SPLICE = Path("/app/tapewell/spools/splice.reel")
OPEN = Path("/app/tapewell/spools/open.reel")
HELD = Path("/app/tapewell/spools/held.reel")
STALE = Path("/app/tapewell/fixtures/stale.tbl")


def _pour() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/app/bin/nockreel", "pour"],
        capture_output=True,
        text=True,
        check=False,
    )


def _spin(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/app/bin/nockreel", "spin", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _require_native_hull() -> None:
    """Grade the linked ELF hull, not a script replacement of nockreel."""
    blob = Path("/app/bin/nockreel").read_bytes()
    assert blob[:4] == b"\x7fELF"
    assert not blob.startswith(b"#!")
    listed = subprocess.run(
        ["nm", "--defined-only", "/app/bin/nockreel"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert listed.returncode == 0, listed.stderr
    names = listed.stdout
    assert "write_hdr" in names
    assert "xin_blob" in names
    assert "sel_bank" in names


def _payload(proc: subprocess.CompletedProcess[str]) -> dict:
    _require_native_hull()
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip())


def test_nck01_prefix_bind():
    """loaded must begin with table: plus knit.ok on a covered spool."""
    body = _payload(_spin(str(SPLICE)))
    assert body["loaded"].startswith("table:")
    assert body["loaded"] == "table:" + KNIT_OK.read_text().strip()


def test_nck02_row_play():
    """splice.reel must replay sys_loom_splice from the poured blob."""
    body = _payload(_spin(str(SPLICE)))
    assert body["status"] == "replayed"
    assert body["call"] == "sys_loom_splice"


def test_nck03_marker_one():
    """Successful table-backed spin writes accept.ok as 1."""
    _payload(_spin(str(SPLICE)))
    assert ACCEPT.read_text().strip() == "1"


def test_nck04_stale_exit():
    """stale blob spin must exit non-zero."""
    _require_native_hull()
    proc = _spin("--blob", str(STALE), str(OPEN))
    assert proc.returncode != 0


def test_nck05_set_matches():
    """loaded.set must copy the JSON loaded field and stay table-backed."""
    body = _payload(_spin(str(OPEN)))
    copied = LOADED_SET.read_text().strip()
    assert copied.startswith("table:")
    assert copied == body["loaded"]


def test_nck06_open_play():
    """open.reel must replay sys_openat2."""
    body = _payload(_spin(str(OPEN)))
    assert body["status"] == "replayed"
    assert body["call"] == "sys_openat2"


def test_nck07_json_shape():
    """spin JSON exposes loaded, status, and call as strings."""
    body = _payload(_spin(str(SPLICE)))
    assert set(body.keys()) == {"loaded", "status", "call"}
    assert isinstance(body["loaded"], str)
    assert isinstance(body["status"], str)
    assert isinstance(body["call"], str)
    assert body["loaded"].startswith("table:")


def test_nck08_holdout_pair():
    """Held-out sys_held_pair spool must replay after pour."""
    body = _payload(_spin(str(HELD)))
    assert body["status"] == "replayed"
    assert body["call"] == "sys_held_pair"


def test_nck09_ok_bind():
    """loaded suffix must equal trimmed knit.ok."""
    body = _payload(_spin(str(HELD)))
    assert body["loaded"] == "table:" + KNIT_OK.read_text().strip()


def test_nck10_no_stock():
    """loaded must not use a builtin: prefix on this image."""
    body = _payload(_spin(str(SPLICE)))
    assert body["loaded"].startswith("table:")
    assert not body["loaded"].startswith("builtin:")


def test_nck11_held_play():
    """held.reel must be covered by poured CALL rows."""
    body = _payload(_spin(str(HELD)))
    assert body["status"] == "replayed"


def test_nck12_stale_gap():
    """stale blob must clear accept.ok after a prior table-backed spin."""
    _payload(_spin(str(SPLICE)))
    assert ACCEPT.exists()
    _require_native_hull()
    proc = _spin("--blob", str(STALE), str(OPEN))
    assert proc.returncode != 0
    assert not ACCEPT.exists()


def test_nck13_cross_check():
    """STAMP line in capset.tbl must match knit.ok and the loaded suffix."""
    stamp = None
    slot = None
    for line in CAPSET.read_text().splitlines():
        if line.startswith("STAMP "):
            stamp = line.split()[1]
        elif line.startswith("SLOT "):
            slot = line.split()[1]
    assert stamp == KNIT_OK.read_text().strip()
    assert slot is not None and stamp is not None
    assert stamp.startswith(slot)
    assert "SLOT " + slot in CAPSET.read_text()
    body = _payload(_spin(str(OPEN)))
    assert body["loaded"] == f"table:{stamp}"


def test_nck_zz_blob_recovery():
    """pour must restore capset.tbl after a corrupt hand-written blob."""
    _require_native_hull()
    CAPSET.write_text("REEL\nMARK 2\nSTAMP deadbeef\n")
    ACCEPT.write_text("1\n")
    proc = _pour()
    assert proc.returncode == 0
    body = _payload(_spin(str(SPLICE)))
    assert body["status"] == "replayed"
    assert body["loaded"].startswith("table:")
    assert "STAMP " + KNIT_OK.read_text().strip() in CAPSET.read_text()
    stamp = KNIT_OK.read_text().strip()
    slot = None
    for line in CAPSET.read_text().splitlines():
        if line.startswith("SLOT "):
            slot = line.split()[1]
    assert slot is not None
    assert stamp.startswith(slot)


def test_nck14_lab_refuse():
    """lab-channel fixture must exit non-zero and leave accept.ok absent."""
    _payload(_spin(str(SPLICE)))
    assert ACCEPT.exists()
    _require_native_hull()
    lab = Path("/app/tapewell/fixtures/lab.tbl")
    proc = _spin("--blob", str(lab), str(OPEN))
    assert proc.returncode != 0
    assert not ACCEPT.exists()


def test_nck15_desc_spool():
    """A spool whose token is only on the description list must replay."""
    desc = Path("/app/tapewell/desc/calls.lst")
    shipped = {
        SPLICE.read_text().split()[0],
        OPEN.read_text().split()[0],
        HELD.read_text().split()[0],
    }
    hold = None
    for line in desc.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        name = line.split()[0]
        if name in shipped or name in {"sys_read", "sys_write"}:
            continue
        hold = name
        break
    assert hold is not None
    reel = Path("/tmp/nck_veil.reel")
    reel.write_text(hold + "\n")
    body = _payload(_spin(str(reel)))
    assert body["status"] == "replayed"
    assert body["call"] == hold
    assert body["loaded"].startswith("table:")
