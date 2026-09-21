"""Verifier for twinefuse mill sew."""

from __future__ import annotations

import json
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

BIN = "/app/bin/twinefuse"
EVE = "/app/cordbay/eve.yarn"
MORN = "/app/cordbay/morn.yarn"
DOCK = Path("/app/dockurn")
CUE = Path("/app/aliascue")
ROWS = DOCK / "rows.ndjson"
IDX = DOCK / "hitch.idx"
OK = DOCK / "berth.ok"
MBOX = DOCK / "mornbox"


def _scan(path: str) -> list[tuple[str, str]]:
    recs: list[tuple[str, str]] = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        eid, tok = line.split(" ", 1)
        recs.append((eid, tok))
    return recs


def _pairs() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for p in sorted(CUE.glob("*.cue")):
        left = right = origin = ""
        for line in p.read_text().splitlines():
            line = line.strip()
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if k == "left":
                left = v
            elif k == "right":
                right = v
            elif k == "origin":
                origin = v
        if origin == "scrapped":
            continue
        if left and right:
            out.append((left, right))
    return out


def _parent(par: dict[str, str], k: str) -> str:
    par.setdefault(k, k)
    while par[k] != k:
        par[k] = par[par[k]]
        k = par[k]
    return k


def _join(par: dict[str, str], a: str, b: str) -> None:
    ra, rb = _parent(par, a), _parent(par, b)
    if ra != rb:
        par[rb] = ra


def _expected(path: str) -> tuple[list[dict], str]:
    recs = _scan(path)
    par: dict[str, str] = {}
    for _, tok in recs:
        _parent(par, tok)
    for a, b in _pairs():
        _join(par, a, b)
    groups: dict[str, set[str]] = defaultdict(set)
    for k in list(par):
        groups[_parent(par, k)].add(k)
    mark = {}
    for members in groups.values():
        least = min(members)
        for m in members:
            mark[m] = least
    rows = []
    by_h: dict[str, list[str]] = defaultdict(list)
    for eid, tok in recs:
        h = mark[tok]
        rows.append({"id": eid, "hitch": h, "tok": tok})
        by_h[h].append(eid)
    idx_lines = []
    for h in sorted(by_h):
        ids = ",".join(sorted(by_h[h]))
        idx_lines.append(f"{h} {ids}")
    return rows, "\n".join(idx_lines) + "\n"


def _load_rows(path: Path) -> list[dict]:
    out = []
    for line in path.read_text().splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def _sew(dump: str, dest: str, binpath: str = BIN) -> subprocess.CompletedProcess:
    return subprocess.run(
        [binpath, "sew", dump, dest],
        capture_output=True,
        text=True,
        check=False,
    )


def _link_ref() -> Path:
    proc = subprocess.run(
        ["go", "build", "-o", "/tmp/twinefuse.ref", "berth.local/twinefuse/berthcli"],
        cwd="/app",
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    blob = Path("/tmp/twinefuse.ref").read_bytes()
    assert blob[:4] == b"\x7fELF"
    return Path("/tmp/twinefuse.ref")


def _same_sew(dump: str, left: str, right: str) -> None:
    a = Path("/tmp/tf-ag") / left
    b = Path("/tmp/tf-rf") / right
    shutil.rmtree(a, ignore_errors=True)
    shutil.rmtree(b, ignore_errors=True)
    ref = str(_link_ref())
    assert _sew(dump, str(a), BIN).returncode == 0
    assert _sew(dump, str(b), ref).returncode == 0
    assert (a / "rows.ndjson").read_bytes() == (b / "rows.ndjson").read_bytes()
    assert (a / "hitch.idx").read_bytes() == (b / "hitch.idx").read_bytes()


def test_tf00_magic():
    """Mill is ELF, matches on-disk Go mill, and two sews of eve agree on rows.ndjson."""
    blob = Path(BIN).read_bytes()
    assert blob[:4] == b"\x7fELF"
    _same_sew(EVE, "eve-a", "eve-b")
    held = Path("/tmp/tf-held.yarn")
    held.write_text("x01 t_z\nx02 t_b\nx03 t_q\n")
    _same_sew(str(held), "held-a", "held-b")
    a = Path("/tmp/tf-a")
    b = Path("/tmp/tf-b")
    shutil.rmtree(a, ignore_errors=True)
    shutil.rmtree(b, ignore_errors=True)
    assert _sew(EVE, str(a)).returncode == 0
    assert _sew(EVE, str(b)).returncode == 0
    assert (a / "rows.ndjson").read_bytes() == (b / "rows.ndjson").read_bytes()


def test_tf01_twin():
    """Two separate sew invocations of eve agree on hitch.idx."""
    a = Path("/tmp/tf-ia")
    b = Path("/tmp/tf-ib")
    shutil.rmtree(a, ignore_errors=True)
    shutil.rmtree(b, ignore_errors=True)
    assert _sew(EVE, str(a)).returncode == 0
    assert _sew(EVE, str(b)).returncode == 0
    assert (a / "hitch.idx").read_bytes() == (b / "hitch.idx").read_bytes()


def test_tf02_book():
    """hitch.idx lines are sorted and match the independent recompute."""
    assert _sew(EVE, str(DOCK)).returncode == 0
    _, want = _expected(EVE)
    got = IDX.read_text()
    assert got == want
    assert got == want  # independent recompute


def test_tf03_seq():
    """rows.ndjson follows eve dump line sequence."""
    assert _sew(EVE, str(DOCK)).returncode == 0
    want_rows, _ = _expected(EVE)
    got = _load_rows(ROWS)
    assert [r["id"] for r in got] == [r["id"] for r in want_rows]
    assert [r["tok"] for r in got] == [r["tok"] for r in want_rows]


def test_tf04_clump():
    """Each group's hitch is the least token in that group."""
    assert _sew(EVE, str(DOCK)).returncode == 0
    want_rows, _ = _expected(EVE)
    got = {r["id"]: r["hitch"] for r in _load_rows(ROWS)}
    for row in want_rows:
        assert got[row["id"]] == row["hitch"]


def test_tf05_span():
    """Alias-joined tokens share one hitch."""
    assert _sew(EVE, str(DOCK)).returncode == 0
    want_rows, _ = _expected(EVE)
    got = {r["id"]: r["hitch"] for r in _load_rows(ROWS)}
    joined = {a for a, b in _pairs()} | {b for a, b in _pairs()}
    pair_ids = [eid for eid, tok in _scan(EVE) if tok in joined]
    assert got[pair_ids[0]] == got[pair_ids[1]]
    want_h = next(r["hitch"] for r in want_rows if r["id"] == pair_ids[0])
    assert got[pair_ids[0]] == want_h


def test_tf06_peer():
    """mornbox hitch per id matches eve and both match the independent mark."""
    assert _sew(EVE, str(DOCK)).returncode == 0
    shutil.rmtree(MBOX, ignore_errors=True)
    assert _sew(MORN, str(MBOX)).returncode == 0
    eve_h = {r["id"]: r["hitch"] for r in _load_rows(ROWS)}
    morn_h = {r["id"]: r["hitch"] for r in _load_rows(MBOX / "rows.ndjson")}
    assert eve_h == morn_h
    want_eve, _ = _expected(EVE)
    want_morn, _ = _expected(MORN)
    for row in want_eve:
        assert eve_h[row["id"]] == row["hitch"]
    for row in want_morn:
        assert morn_h[row["id"]] == row["hitch"]


def test_tf07_held():
    """Hold-out yarn not in cordbay follows the same hitch-to-id rule."""
    held = Path("/tmp/tf-held.yarn")
    dest = Path("/tmp/tf-held-out")
    held.write_text("x01 u_aa\nx02 u_cc\nx03 u_bb\n")
    c1 = CUE / "hold.cue"
    c2 = CUE / "hold2.cue"
    c1.write_text("left=u_aa\nright=u_cc\norigin=desk\n")
    c2.write_text("left=u_cc\nright=u_bb\norigin=desk\n")
    shutil.rmtree(dest, ignore_errors=True)
    try:
        assert _sew(str(held), str(dest)).returncode == 0
        want_rows, want_idx = _expected(str(held))
        got = _load_rows(dest / "rows.ndjson")
        assert got == want_rows
        assert (dest / "hitch.idx").read_text() == want_idx
    finally:
        c1.unlink(missing_ok=True)
        c2.unlink(missing_ok=True)


def test_tf08_hush():
    """scrapped origin makes sew fail and leaves berth.ok absent."""
    scrap = CUE / "tmp.cue"
    scrap.write_text("left=t_a\nright=t_m\norigin=scrapped\n")
    if OK.exists():
        OK.unlink()
    try:
        proc = _sew(EVE, str(DOCK))
        assert proc.returncode != 0
        assert not OK.exists()
    finally:
        scrap.unlink(missing_ok=True)


def test_tf09_guard():
    """Successful sew writes berth.ok and idx digest matches recompute."""
    if OK.exists():
        OK.unlink()
    assert _sew(EVE, str(DOCK)).returncode == 0
    assert OK.read_text() == "ok\n"
    _, want = _expected(EVE)
    assert IDX.read_text() == want


def test_tf10_hits():
    """A hitch copied from a row selects the same id set in hitch.idx."""
    assert _sew(EVE, str(DOCK)).returncode == 0
    rows = _load_rows(ROWS)
    table = {}
    for line in IDX.read_text().splitlines():
        h, ids = line.split(" ", 1)
        table[h] = ids.split(",")
    by_h: dict[str, set[str]] = defaultdict(set)
    for r in rows:
        by_h[r["hitch"]].add(r["id"])
    for r in rows:
        assert set(table[r["hitch"]]) == by_h[r["hitch"]]
    want_rows, _ = _expected(EVE)
    joined = {a for a, b in _pairs()} | {b for a, b in _pairs()}
    pair_ids = [eid for eid, tok in _scan(EVE) if tok in joined]
    want_h = next(r["hitch"] for r in want_rows if r["id"] == pair_ids[0])
    want_ids = {r["id"] for r in want_rows if r["hitch"] == want_h}
    assert set(table[want_h]) == want_ids


def test_tf11_redo():
    """Corrupt dockurn then sew recovers independently computed rows."""
    DOCK.mkdir(parents=True, exist_ok=True)
    ROWS.write_text("{}\n")
    IDX.write_text("junk\n")
    assert _sew(EVE, str(DOCK)).returncode == 0
    want_rows, want_idx = _expected(EVE)
    assert _load_rows(ROWS) == want_rows
    assert IDX.read_text() == want_idx
    assert OK.read_text() == "ok\n"
