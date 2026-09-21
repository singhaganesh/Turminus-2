"""Verifier for clatter tallow/pour keg artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

BIN = Path("/app/bin/clatter")
WELL = Path("/app/dropwell")
SEED = Path("/app/seed/dropwell")
KEG = Path("/app/kegbay")
JSON_PATH = KEG / "upload.json"
TSV_PATH = KEG / "batch.tsv"
MARK = KEG / "MARK"
ARC = Path("/app/tidearc/lastgood.rec")
DELTA = 11644473600
TICKS = 10000000


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _restore() -> None:
    WELL.mkdir(parents=True, exist_ok=True)
    for p in WELL.glob("*.clat"):
        p.unlink()
    for p in SEED.glob("*.clat"):
        shutil.copy(p, WELL / p.name)
    if KEG.exists():
        for p in KEG.iterdir():
            if p.is_file():
                p.unlink()


def _mint() -> subprocess.CompletedProcess[str]:
    _assert_native()
    a = subprocess.run(["/app/bin/clatter", "tallow"], capture_output=True, text=True)
    if a.returncode != 0:
        return a
    return subprocess.run(["/app/bin/clatter", "pour"], capture_output=True, text=True)


def _u16(b: bytes, i: int) -> int:
    return int.from_bytes(b[i : i + 2], "little")


def _u32(b: bytes, i: int) -> int:
    return int.from_bytes(b[i : i + 4], "little")


def _load_clat(path: Path) -> tuple[int, tuple[int, int] | None, bytes, int]:
    b = path.read_bytes()
    write_stamp = _u32(b, 6)
    n = _u16(b, 10)
    crash = None
    guid = b"\x00" * 16
    companion = 0
    off = 12
    for _ in range(n):
        st = _u32(b, off)
        rva = _u32(b, off + 4)
        sz = _u32(b, off + 8)
        off += 12
        sl = b[rva : rva + sz]
        if st == 3 and len(sl) >= 8:
            lo = _u32(sl, 0)
            hi = _u32(sl, 4)
            crash = (lo, hi)
        if st == 15 and len(sl) > 16:
            guid = sl[:16]
            companion = sl[16]
    return write_stamp, crash, guid, companion


def _unix_key(path: Path) -> int:
    write_stamp, crash, _g, _c = _load_clat(path)
    if crash is None:
        return write_stamp
    lo, hi = crash
    ft = (hi << 32) | lo
    return ft // TICKS - DELTA


def _want_names() -> list[str]:
    files = list(WELL.glob("*.clat"))
    metas = []
    for p in files:
        _w, _c, guid, companion = _load_clat(p)
        metas.append((p, guid, companion, _unix_key(p)))
    by: dict[bytes, list] = {}
    for p, guid, companion, key in metas:
        by.setdefault(guid, []).append((companion, key, p.name))
    groups = []
    for guid, rows in by.items():
        prim = [r[1] for r in rows if r[0] == 0]
        pk = min(prim) if prim else min(r[1] for r in rows)
        rows.sort(key=lambda r: (r[0], r[2]))
        groups.append((pk, [r[2] for r in rows]))
    groups.sort(key=lambda g: g[0])
    out: list[str] = []
    for _k, names in groups:
        out.extend(names)
    return out


def _load_json() -> dict:
    return json.loads(JSON_PATH.read_text())


def test_bw01_repeat_pair() -> None:
    """two fresh mints write identical keg bytes."""
    _restore()
    assert _mint().returncode == 0
    j1 = JSON_PATH.read_bytes()
    t1 = TSV_PATH.read_bytes()
    assert _mint().returncode == 0
    assert JSON_PATH.read_bytes() == j1
    assert TSV_PATH.read_bytes() == t1


def test_bw02_arc_order() -> None:
    """seq names follow decoded dump chronology."""
    _restore()
    assert _mint().returncode == 0
    body = _load_json()
    got = [row["name"] for row in sorted(body["entries"], key=lambda r: r["seq"])]
    assert got == _want_names()
    by_name = {row["name"]: row["seq"] for row in body["entries"]}
    for line in ARC.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[1] in by_name:
            assert by_name[parts[1]] == int(parts[0])


def test_bw03_pair_adj() -> None:
    """same-guid extras sit beside their primary."""
    _restore()
    assert _mint().returncode == 0
    names = [row["name"] for row in sorted(_load_json()["entries"], key=lambda r: r["seq"])]
    assert names.index("a.clat") + 1 == names.index("a2.clat")
    assert names.index("e.clat") + 1 == names.index("e2.clat")


def test_bw04_hold_extra() -> None:
    """a dump added at grade time lands in chronology."""
    _restore()
    extra = WELL / "mid.clat"
    raw = bytearray((WELL / "b.clat").read_bytes())
    unix = 1550000000
    ft = (unix + DELTA) * TICKS
    lo_d = ft & 0xFFFFFFFF
    hi_d = (ft >> 32) & 0xFFFFFFFF
    n = _u16(bytes(raw), 10)
    off = 12
    for _ in range(n):
        st = _u32(bytes(raw), off)
        rva = _u32(bytes(raw), off + 4)
        off += 12
        if st == 3:
            raw[rva : rva + 4] = int(lo_d).to_bytes(4, "little")
            raw[rva + 4 : rva + 8] = int(hi_d).to_bytes(4, "little")
        if st == 15:
            raw[rva : rva + 16] = bytes([0x55]) * 16
            raw[rva + 16] = 0
    extra.write_bytes(bytes(raw))
    assert _mint().returncode == 0
    names = [row["name"] for row in sorted(_load_json()["entries"], key=lambda r: r["seq"])]
    assert names == _want_names()
    assert "mid.clat" in names
    assert names.index("b.clat") < names.index("mid.clat") < names.index("d.clat")


def test_bw05_empty_exit() -> None:
    """empty well makes tallow fail."""
    _restore()
    for p in WELL.glob("*.clat"):
        p.unlink()
    proc = subprocess.run(["/app/bin/clatter", "tallow"], capture_output=True, text=True)
    _assert_native()
    assert proc.returncode != 0


def test_bw06_outside_exit() -> None:
    """pour of a path outside the well exits nonzero."""
    _restore()
    assert _mint().returncode == 0
    proc = subprocess.run(
        ["/app/bin/clatter", "pour", "/app/scratch"],
        capture_output=True,
        text=True,
    )
    _assert_native()
    assert proc.returncode != 0


def test_bw07_schema_rows() -> None:
    """json lists every well file once with required fields."""
    _restore()
    assert _mint().returncode == 0
    body = _load_json()
    names = [row["name"] for row in body["entries"]]
    well = {p.name for p in WELL.glob("*.clat")}
    assert set(names) == well
    assert len(names) == len(well)
    for row in body["entries"]:
        assert set(row) >= {"seq", "name", "digest", "guid"}
        assert isinstance(row["seq"], int)
        assert row["seq"] >= 1


def test_bw08_tsv_rows() -> None:
    """tsv rows match json seq/name/digest/guid."""
    _restore()
    assert _mint().returncode == 0
    body = _load_json()
    lines = TSV_PATH.read_text().splitlines()
    assert lines[0] == "seq\tname\tdigest\tguid"
    rows = [ln.split("\t") for ln in lines[1:] if ln]
    js = sorted(body["entries"], key=lambda r: r["seq"])
    assert len(rows) == len(js)
    for rec, j in zip(rows, js):
        assert rec[0] == str(j["seq"])
        assert rec[1] == j["name"]
        assert rec[2] == j["digest"]
        assert rec[3] == j["guid"]
    names = [rec[1] for rec in rows]
    assert names == _want_names()


def test_bw09_hex_body() -> None:
    """digest matches dump bytes and seq-1 is the earliest crash."""
    _restore()
    assert _mint().returncode == 0
    body = _load_json()
    want = _want_names()
    names = [row["name"] for row in sorted(body["entries"], key=lambda r: r["seq"])]
    assert names == want
    for row in body["entries"]:
        proc = subprocess.run(
            ["sha256sum", str(WELL / row["name"])],
            capture_output=True,
            text=True,
        )
        assert row["digest"] == proc.stdout.split()[0]
        assert row["digest"] == row["digest"].lower()


def test_bw10_k_split() -> None:
    """batch_count is ceil of entry count over three and first batch is earliest names."""
    _restore()
    assert _mint().returncode == 0
    body = _load_json()
    want = _want_names()
    names = [row["name"] for row in sorted(body["entries"], key=lambda r: r["seq"])]
    assert names == want
    n = len(want)
    assert body["batch_count"] == (n + 2) // 3
    assert names[:3] == want[:3]


def test_bw11_zz_regen() -> None:
    """tallow then pour restores keg files after they are clobbered."""
    _restore()
    assert _mint().returncode == 0
    JSON_PATH.write_text("{}")
    TSV_PATH.write_text("junk")
    proc = subprocess.run(["/app/bin/clatter", "tallow"], capture_output=True, text=True)
    assert proc.returncode == 0
    proc = subprocess.run(["/app/bin/clatter", "pour"], capture_output=True, text=True)
    _assert_native()
    assert proc.returncode == 0
    names = [row["name"] for row in sorted(_load_json()["entries"], key=lambda r: r["seq"])]
    assert names == _want_names()


def test_bw12_one_shot() -> None:
    """one tallow subprocess then one pour subprocess fills the keg."""
    _restore()
    _assert_native()
    a = subprocess.run(["/app/bin/clatter", "tallow"], capture_output=True, text=True)
    assert a.returncode == 0
    b = subprocess.run(["/app/bin/clatter", "pour"], capture_output=True, text=True)
    assert b.returncode == 0
    names = [row["name"] for row in sorted(_load_json()["entries"], key=lambda r: r["seq"])]
    assert names == _want_names()


def test_bw13_flag_gone() -> None:
    """failed empty mint leaves MARK absent."""
    _restore()
    MARK.write_text("ok")
    for p in WELL.glob("*.clat"):
        p.unlink()
    subprocess.run(["/app/bin/clatter", "tallow"], capture_output=True, text=True)
    _assert_native()
    assert not MARK.exists()


def test_bw14_seed_hide() -> None:
    """chronology holds even if last-good is moved aside."""
    _restore()
    hidden = KEG / "hide.rec"
    if ARC.exists():
        shutil.move(str(ARC), str(hidden))
    try:
        assert _mint().returncode == 0
        names = [row["name"] for row in sorted(_load_json()["entries"], key=lambda r: r["seq"])]
        assert names == _want_names()
    finally:
        if hidden.exists():
            shutil.move(str(hidden), str(ARC))
