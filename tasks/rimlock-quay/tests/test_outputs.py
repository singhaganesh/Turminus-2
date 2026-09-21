"""Verifier for rimlock wait-graph mill."""

from __future__ import annotations

import subprocess
from pathlib import Path

BIN = Path("/app/bin/rimlock")
REF = Path("/tmp/rimlock.ref")
SHIFT = Path("/app/vatdock/shift.dmp")
DUSK = Path("/app/vatdock/dusk.dmp")
BAY = Path("/app/planbay")
SCR = Path("/app/scrollbay")
LIVE = BAY / "live.plan"
ALT = BAY / "alt.plan"
CHK = SCR / "desk.chk"
OK = BAY / "mill.ok"


def _link_ref() -> Path:
    r = subprocess.run(
        [
            "make",
            "-C",
            "/app/hullcue",
            "-f",
            "/app/hullcue/hull.mk",
            "hull",
            "HULLBIN=/tmp/rimlock.ref",
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    blob = REF.read_bytes()
    assert blob[:4] == b"\x7fELF"
    return REF


def _unjam_with(binpath: Path, src: Path, dst: Path) -> subprocess.CompletedProcess[str]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [str(binpath), "unjam", str(src), str(dst)],
        capture_output=True,
        text=True,
    )


def _book_text() -> str:
    return Path("/app/inkurn/book.tsv").read_text()


def _blk(tid: str, own: str, wait: str | None = None) -> str:
    body = "TH" + "READ " + tid + "\nOWN " + own + "\n"
    if wait:
        body += "WAIT " + wait + "\n"
    return body + ".\n"


def _shift_src() -> str:
    return "".join(
        [
            _blk("10", "0x100a"),
            "\n",
            _blk("11", "0x100b"),
            "\n",
            _blk("12", "0x100c", "0x100a"),
            "\n",
            _blk("13", "0x100d", "0x100b"),
            "\n",
            _blk("20", "0x200a", "0x200b"),
            "\n",
            _blk("21", "0x200b", "0x200a"),
        ]
    )


def _dusk_src() -> str:
    return "".join(
        [
            _blk("10", "0x400a"),
            "\n",
            _blk("11", "0x400b"),
            "\n",
            _blk("12", "0x400c", "0x400a"),
            "\n",
            _blk("13", "0x400d", "0x400b"),
            "\n",
            _blk("20", "0x500a", "0x500b"),
            "\n",
            _blk("21", "0x500b", "0x500a"),
        ]
    )


def _hold_src() -> str:
    return (
        _blk("9", "0x300b")
        + "\n"
        + _blk("8", "0x300c")
        + "\n"
        + _blk("7", "0x300a")
    )


def _assay(src: Path, dst: Path) -> subprocess.CompletedProcess[str]:
    BAY.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        ["/app/bin/rimlock", "unjam", str(src), str(dst)],
        capture_output=True,
        text=True,
    )


def _scroll(src: Path, dst: Path) -> subprocess.CompletedProcess[str]:
    SCR.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        ["/app/bin/rimlock", "scroll", str(src), str(dst)],
        capture_output=True,
        text=True,
    )


def _book() -> dict[str, int]:
    out: dict[str, int] = {}
    for ln in _book_text().splitlines():
        parts = ln.split()
        if len(parts) < 2 or parts[0] == "hex":
            continue
        out[parts[0]] = int(parts[1])
    return out


def _parse_dump_text(text: str) -> list[tuple[int, str, str | None]]:
    rows: list[tuple[int, str, str | None]] = []
    tid = 0
    own = ""
    wait: str | None = None
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("TH" + "READ "):
            tid = int(s.split()[1])
            own = ""
            wait = None
        elif s.startswith("OWN "):
            own = s.split()[1]
        elif s.startswith("WAIT "):
            wait = s.split()[1]
        elif s == "." and own:
            rows.append((tid, own, wait))
    return rows


def _expected_plan_text(text: str) -> list[str]:
    book = _book()
    rows = _parse_dump_text(text)
    tags = [book[own] for _, own, _ in rows]
    wait_of = {}
    for tid, own, wait in rows:
        t = book[own]
        if wait:
            wait_of[t] = book[wait]
    indeg = {t: 0 for t in tags}
    succ: dict[int, list[int]] = {t: [] for t in tags}
    for t, w in wait_of.items():
        succ[w].append(t)
        indeg[t] += 1
    plan: list[int] = []
    left = set(tags)
    while left:
        ready = [t for t in left if indeg[t] == 0]
        if not ready:
            ready = list(left)
        pick = min(ready)
        plan.append(pick)
        left.remove(pick)
        for j in succ[pick]:
            if j in left:
                indeg[j] -= 1
    return [str(x) for x in plan]


def _pin_shift() -> None:
    SHIFT.write_text(_shift_src())
    DUSK.write_text(_dusk_src())


def _write_dump(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def test_rkq01_hdr():
    """Linked mill is ELF; agent mill matches hull from on-disk C; intern identities."""
    _pin_shift()
    blob = BIN.read_bytes()
    assert blob[:4] == b"\x7fELF"
    _link_ref()
    ref_out = Path("/tmp/rkq-ref.plan")
    assert _unjam_with(BIN, SHIFT, LIVE).returncode == 0
    assert _unjam_with(REF, SHIFT, ref_out).returncode == 0
    assert LIVE.read_bytes() == ref_out.read_bytes()
    assert LIVE.read_text().split() == _expected_plan_text(_shift_src())


def test_rkq02_twin():
    """Two process unjam runs of shift are byte-identical after identity emit."""
    _pin_shift()
    p1 = BAY / "t1.plan"
    p2 = BAY / "t2.plan"
    assert _assay(SHIFT, p1).returncode == 0
    assert _assay(SHIFT, p2).returncode == 0
    assert p1.read_bytes() == p2.read_bytes()
    assert all(x.isdigit() for x in p1.read_text().split())


def test_rkq03_peer():
    """Dusk remapped hex unjam matches shift plan identities."""
    _pin_shift()
    assert _assay(SHIFT, LIVE).returncode == 0
    assert _assay(DUSK, ALT).returncode == 0
    assert LIVE.read_text() == ALT.read_text()
    assert "0x" not in LIVE.read_text()


def test_rkq04_rows():
    """Scroll rows are tid tag in plan order."""
    _pin_shift()
    assert _assay(SHIFT, LIVE).returncode == 0
    assert _scroll(SHIFT, CHK).returncode == 0
    plan = [ln.strip() for ln in LIVE.read_text().splitlines() if ln.strip()]
    rows = [ln.split() for ln in CHK.read_text().splitlines() if ln.strip()]
    assert [r[1] for r in rows] == plan
    assert all(part.isdigit() for r in rows for part in r)


def test_rkq05_holdout():
    """Held-out three-source dump emits ascending identity, not dump order."""
    hd = BAY / "hold.dmp"
    _write_dump(hd, _hold_src())
    out = BAY / "hold.plan"
    r = _assay(hd, out)
    assert r.returncode == 0
    assert out.read_text().split() == _expected_plan_text(_hold_src())


def test_rkq06_tail():
    """Missing closer must make `unjam` exit non-zero and omits mill.ok."""
    bad = BAY / "bad.dmp"
    _write_dump(bad, _blk("8", "0x300a")[:-2])
    if OK.exists():
        OK.unlink()
    r = _assay(bad, BAY / "bad.plan")
    assert r.returncode != 0
    assert not OK.exists()


def test_rkq07_mint():
    """Corrupt live.plan then re-run unjam recovers identity lines."""
    _pin_shift()
    assert _assay(SHIFT, LIVE).returncode == 0
    LIVE.write_text("junk\n")
    r = _assay(SHIFT, LIVE)
    assert r.returncode == 0
    assert LIVE.read_text().split() == _expected_plan_text(_shift_src())
    assert OK.exists()


def test_rkq08_hush():
    """Dusk scroll matches shift scroll (second run of the same graph)."""
    _pin_shift()
    a = SCR / "a.chk"
    b = SCR / "b.chk"
    assert _scroll(SHIFT, a).returncode == 0
    assert _scroll(DUSK, b).returncode == 0
    assert a.read_text() == b.read_text()


def test_rkq09_hits():
    """Simultaneously releasable monitors appear in ascending identity."""
    _pin_shift()
    assert _assay(SHIFT, LIVE).returncode == 0
    got = LIVE.read_text().split()
    exp = _expected_plan_text(_shift_src())
    assert got == exp


def test_rkq10_child():
    """One unjam subprocess writes decimal identities, not dump hex."""
    _pin_shift()
    out = BAY / "one.plan"
    r = _assay(SHIFT, out)
    assert r.returncode == 0
    text = out.read_text()
    assert "0x" not in text
    assert all(p.isdigit() for p in text.split())


def test_rkq11_stay():
    """Plan is a valid topo order of recorded wait edges under intern identity."""
    _pin_shift()
    assert _assay(SHIFT, LIVE).returncode == 0
    assert LIVE.read_text().split() == _expected_plan_text(_shift_src())


def test_rkq12_peer():
    """Two process dusk scroll files match expected identities."""
    _pin_shift()
    s1 = SCR / "d1.chk"
    s2 = SCR / "d2.chk"
    assert _scroll(DUSK, s1).returncode == 0
    assert _scroll(DUSK, s2).returncode == 0
    assert s1.read_bytes() == s2.read_bytes()
    rows = [ln.split() for ln in s1.read_text().splitlines() if ln.strip()]
    assert [r[1] for r in rows] == _expected_plan_text(_dusk_src())
