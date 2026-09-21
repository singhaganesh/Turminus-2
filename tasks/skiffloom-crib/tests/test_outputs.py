"""Verifier for skiffloom cull slates."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

BIN = Path("/app/bin/skiffloom")
EVE = Path("/app/deltabay/eve.chg")
MORN = Path("/app/deltabay/morn.chg")
VOID = Path("/app/deltabay/void.chg")
WELL = Path("/app/slatewell")
OK = WELL / "cull.ok"
MESH = Path("/app/meshcards")
TICKS = Path("/app/durcards/ticks.txt")


def _cull(exe: Path, src: Path, dest: Path) -> subprocess.CompletedProcess[str]:
    dest.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [str(exe), "cull", str(src), str(dest)],
        capture_output=True,
        text=True,
    )


def _read_json(dest: Path) -> dict:
    return json.loads((dest / "slate.json").read_text())


def _ticks() -> dict[str, int]:
    out: dict[str, int] = {}
    for line in TICKS.read_text().splitlines():
        if not line.strip():
            continue
        name, dur = line.split()
        out[name] = int(dur)
    return out


def _parse_chg(path: Path) -> tuple[int, str, list[tuple[str, set[int]]]]:
    budget = 0
    origin = ""
    files: list[tuple[str, set[int]]] = []
    cur: str | None = None
    hits: set[int] = set()
    for line in path.read_text().splitlines():
        if line.startswith("BUDGET "):
            budget = int(line.split()[1])
        elif line.startswith("ORIGIN "):
            origin = line.split()[1]
        elif line.startswith("FILE "):
            if cur is not None:
                files.append((cur, set(hits)))
            cur = line[5:]
            hits = set()
        elif line.startswith("LINES "):
            hits = {int(x) for x in line.split()[1:]}
        elif line == "END":
            if cur is not None:
                files.append((cur, set(hits)))
            break
    return budget, origin, files


def _parse_mesh(path: Path) -> tuple[str, dict[str, set[int]]]:
    ident = ""
    files: dict[str, set[int]] = {}
    cur = ""
    for line in path.read_text().splitlines():
        if line.startswith("ID "):
            ident = line[3:]
        elif line.startswith("FILE "):
            cur = line[5:]
            files[cur] = set()
        elif line.startswith("HITS "):
            files[cur] = {int(x) for x in line.split()[1:]}
    return ident, files


def _expected(path: Path) -> tuple[list[str], list[str], int]:
    budget, _origin, chg_files = _parse_chg(path)
    weights: dict[str, int] = {}
    for mesh in MESH.glob("*.mesh"):
        ident, hits = _parse_mesh(mesh)
        w = 0
        for fpath, lines in chg_files:
            for ln in lines:
                if ln in hits.get(fpath, set()):
                    w += 1
        if w > 0:
            weights[ident] = w
    pool = sorted(weights, key=lambda k: (-weights[k], k))
    durs = _ticks()
    names: list[str] = []
    spent = 0
    for ident in pool:
        nxt = spent + durs[ident]
        if nxt > budget:
            break
        names.append(ident)
        spent = nxt
    return pool, names, spent


def _link_ref() -> Path:
    dest = Path("/tmp/skiffloom.ref")
    r = subprocess.run(
        ["make", "-C", "/app/cribcli", "-f", "driver.mk", "OUT=/tmp/skiffloom.ref"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    assert dest.is_file()
    return dest


def test_sk01_hdr():
    """Linked mill is ELF and two eve culls match."""
    blob = BIN.read_bytes()
    assert blob[:4] == b"\x7fELF"
    a = Path("/tmp/sk_a")
    b = Path("/tmp/sk_b")
    shutil.rmtree(a, ignore_errors=True)
    shutil.rmtree(b, ignore_errors=True)
    ra = _cull(BIN, EVE, a)
    rb = _cull(BIN, EVE, b)
    assert ra.returncode == 0
    assert rb.returncode == 0
    assert (a / "slate.json").read_bytes() == (b / "slate.json").read_bytes()
    assert (a / "slate.bin").read_bytes() == (b / "slate.bin").read_bytes()
    pool, names, spent = _expected(EVE)
    doc = _read_json(a)
    assert doc["pool"] == pool
    assert doc["names"] == names
    assert doc["spent_ms"] == spent


def test_sk02_peer():
    """Second eve dest keeps the same ranked pool as forms.txt."""
    dest = Path("/tmp/sk_peer")
    shutil.rmtree(dest, ignore_errors=True)
    r = _cull(BIN, EVE, dest)
    assert r.returncode == 0
    pool, _names, _spent = _expected(EVE)
    assert _read_json(dest)["pool"] == pool


def test_sk03_bag():
    """morn pool keeps the rib-only sheet that also covers the change."""
    dest = WELL / "mornbox"
    r = _cull(BIN, MORN, dest)
    assert r.returncode == 0
    doc = _read_json(dest)
    assert set(doc["pool"]) == set(_expected(MORN)[0])


def test_sk04_cut():
    """eve names fill the duration budget and stop before the next tick."""
    dest = WELL
    r = _cull(BIN, EVE, dest)
    assert r.returncode == 0
    _pool, names, spent = _expected(EVE)
    doc = _read_json(dest)
    assert len(doc["names"]) == len(names)
    assert doc["spent_ms"] == spent


def test_sk05_dusk():
    """morn pool keeps the keel-overlapping sheet."""
    dest = WELL / "mornbox"
    r = _cull(BIN, MORN, dest)
    assert r.returncode == 0
    assert set(_read_json(dest)["pool"]) == set(_expected(MORN)[0])


def test_sk06_tail():
    """Held-out unique-weight card clips by duration not by a count cap."""
    card = Path("/tmp/sk_tail.chg")
    card.write_text(
        "BUDGET 90\nORIGIN live\nFILE rib.c\nLINES 1 2 3 4 5 6 7 8 9\nEND\n"
    )
    dest = Path("/tmp/sk_tail")
    shutil.rmtree(dest, ignore_errors=True)
    r = _cull(BIN, card, dest)
    assert r.returncode == 0
    _pool, names, spent = _expected(card)
    doc = _read_json(dest)
    assert len(doc["names"]) == len(names)
    assert doc["spent_ms"] == spent


def test_sk07_seal():
    """Corrupt slates then cull eve regenerates spent_ms."""
    dest = WELL
    (dest / "slate.json").write_text("{}")
    (dest / "slate.bin").write_bytes(b"xxxx")
    r = _cull(BIN, EVE, dest)
    assert r.returncode == 0
    _pool, _names, spent = _expected(EVE)
    assert _read_json(dest)["spent_ms"] == spent
    magic = (dest / "slate.bin").read_bytes()[:4]
    assert magic == b"SLT1"


def test_sk08_rest():
    """Passing eve cull writes cull.ok and a matching binary spent trailer."""
    dest = WELL
    r = _cull(BIN, EVE, dest)
    assert r.returncode == 0
    assert OK.is_file()
    blob = (dest / "slate.bin").read_bytes()
    spent = (blob[-4] << 24) | (blob[-3] << 16) | (blob[-2] << 8) | blob[-1]
    assert spent == _read_json(dest)["spent_ms"]
    assert spent == _expected(EVE)[2]


def test_sk09_hold():
    """Held-out two-file card keeps both covering sheets in pool."""
    card = Path("/tmp/sk_hold.chg")
    card.write_text(
        "BUDGET 80\nORIGIN live\nFILE rib.c\nLINES 12\nFILE keel.c\nLINES 10 11\nEND\n"
    )
    dest = Path("/tmp/sk_hold")
    shutil.rmtree(dest, ignore_errors=True)
    r = _cull(BIN, card, dest)
    assert r.returncode == 0
    doc = _read_json(dest)
    assert set(doc["pool"]) == set(_expected(card)[0])


def test_sk10_note():
    """Two eve culls into sibling dests stay byte-identical."""
    a = Path("/tmp/sk_n1")
    b = Path("/tmp/sk_n2")
    shutil.rmtree(a, ignore_errors=True)
    shutil.rmtree(b, ignore_errors=True)
    assert _cull(BIN, EVE, a).returncode == 0
    assert _cull(BIN, EVE, b).returncode == 0
    assert (a / "slate.bin").read_bytes() == (b / "slate.bin").read_bytes()


def test_sk11_ref():
    """Throwaway mill from HULL.txt matches the shipped CLI on eve."""
    ref = _link_ref()
    a = Path("/tmp/sk_ship")
    b = Path("/tmp/sk_throw")
    shutil.rmtree(a, ignore_errors=True)
    shutil.rmtree(b, ignore_errors=True)
    assert _cull(BIN, EVE, a).returncode == 0
    assert _cull(ref, EVE, b).returncode == 0
    assert (a / "slate.json").read_bytes() == (b / "slate.json").read_bytes()
    assert (a / "slate.bin").read_bytes() == (b / "slate.bin").read_bytes()


def test_sk12_lab():
    """voided origin exits non-zero and leaves cull.ok missing."""
    if OK.exists():
        OK.unlink()
    r = _cull(BIN, VOID, WELL)
    assert r.returncode != 0
    assert not OK.is_file()
