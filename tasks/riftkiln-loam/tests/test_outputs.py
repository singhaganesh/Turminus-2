"""Verifier for riftkiln sift mill artifacts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

BIN = Path("/app/bin/riftkiln")
YG = Path("/app/cardhearth/card.yg")
OK = Path("/app/markcue/brew.ok")
Q = Path("/app/tblwell/quarrel.lst")


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _sift(src: Path, dest: Path) -> subprocess.CompletedProcess[str]:
    _assert_native()
    dest.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        ["/app/bin/riftkiln", "sift", str(src), str(dest)],
        capture_output=True,
        text=True,
    )


def _write_qn(text: str) -> Path:
    p = Path("/app/treypit/held.qn")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def _load(dest: Path) -> dict:
    return json.loads(dest.read_text())


def _nested_a() -> str:
    return """yard north {
  peg a = 1;
  pen outer {
    pen inner {
      peg b = 2;
    } clip wet
  }
}
"""


def _nested_b() -> str:
    return """yard west {
  peg z = 9;
  pen outer {
    pen left {
      peg p = 1;
    } clip damp
    pen right {
      peg q = 2;
    }
  }
}
"""


def _nested_c() -> str:
    return """yard east {
  pen outer {
    pen mid {
      pen inner {
        peg b = 2;
      } clip fog
    }
  }
}
"""


def _pen(body: dict, stem: str) -> dict | None:
    members = body.get("members") or []
    for m in members:
        if isinstance(m, dict) and m.get("stem") == stem:
            return m
        if isinstance(m, dict):
            hit = _pen(m, stem)
            if hit is not None:
                return hit
    return None


def _sibling_after_pen(enclosing: dict, inner_stem: str) -> dict:
    kids = enclosing.get("members") or []
    idx = next(i for i, k in enumerate(kids) if k.get("stem") == inner_stem)
    inn = kids[idx]
    assert "clip" not in inn
    assert idx + 1 < len(kids)
    nxt = kids[idx + 1]
    assert "stem" in nxt
    assert "members" not in nxt
    assert "tag" not in nxt
    return nxt


def _held_a(dest: Path) -> None:
    src = _write_qn(_nested_a())
    proc = _sift(src, dest)
    assert proc.returncode == 0, proc.stderr
    body = _load(dest)
    outer = _pen(body, "outer")
    assert outer is not None
    nxt = _sibling_after_pen(outer, "inner")
    assert nxt.get("stem") == "wet"
    inner = _pen(outer, "inner")
    assert inner is not None
    kids = inner.get("members") or []
    assert kids
    assert "tag" in kids[0]


def _held_b(dest: Path) -> None:
    src = _write_qn(_nested_b())
    proc = _sift(src, dest)
    assert proc.returncode == 0, proc.stderr
    body = _load(dest)
    outer = _pen(body, "outer")
    assert outer is not None
    nxt = _sibling_after_pen(outer, "left")
    assert nxt.get("stem") == "damp"


def _held_c(dest: Path) -> None:
    src = _write_qn(_nested_c())
    proc = _sift(src, dest)
    assert proc.returncode == 0, proc.stderr
    body = _load(dest)
    mid = _pen(body, "mid")
    assert mid is not None
    nxt = _sibling_after_pen(mid, "inner")
    assert nxt.get("stem") == "fog"


def test_k01_alpha() -> None:
    """held nest places the trailing ident beside the inner enclosure."""
    _held_a(Path("/app/treypit/out1.json"))


def test_k02_bravo() -> None:
    """second inner enclosure still yields a trailing sibling on the outer list."""
    _held_b(Path("/app/treypit/out2.json"))


def test_k03_charlie() -> None:
    """deeper enclosure still lifts the trailing ident one level."""
    _held_c(Path("/app/treypit/out3.json"))


def test_k04_delta() -> None:
    """inner payload survives next to the trailing sibling."""
    dest = Path("/app/treypit/out4.json")
    _held_a(dest)
    body = _load(dest)
    outer = _pen(body, "outer")
    assert outer is not None
    assert len(outer.get("members") or []) == 2


def _inject_conflict() -> str:
    old = YG.read_text()
    YG.write_text(
        """# rib_b
S : YARD ID LBRACE MS RBRACE ;
MS : MS M | ;
M : PEG ID EQ VAL SEMI
  | PEN ID LBRACE MS RBRACE
  | PEN ID LBRACE MS RBRACE CLIP ID
  | CLIP ID
  ;
"""
    )
    return old


def test_k05_echo() -> None:
    """MAP helper exits nonzero when the recipe still records a nesting cut."""
    old = _inject_conflict()
    try:
        OK.unlink(missing_ok=True)
        proc = subprocess.run(["/app/hearth.sh"], capture_output=True, text=True)
        assert proc.returncode != 0
    finally:
        YG.write_text(old)


def test_k06_foxtrot() -> None:
    """brew.ok stays missing after a refused mill on a nested-cut recipe."""
    old = _inject_conflict()
    try:
        OK.unlink(missing_ok=True)
        proc = subprocess.run(["/app/hearth.sh"], capture_output=True, text=True)
        assert proc.returncode != 0
        assert not OK.exists()
    finally:
        YG.write_text(old)


def test_k07_golf() -> None:
    """quarrel ledger is nonempty when that helper refuses the recipe."""
    old = _inject_conflict()
    try:
        proc = subprocess.run(["/app/hearth.sh"], capture_output=True, text=True)
        assert proc.returncode != 0
        text = Q.read_text() if Q.exists() else ""
        assert text.strip() != ""
    finally:
        YG.write_text(old)


def test_k08_hotel() -> None:
    """running mill stays ELF after a refused helper pass."""
    old = _inject_conflict()
    try:
        subprocess.run(["/app/hearth.sh"], capture_output=True, text=True)
        _assert_native()
        proc = subprocess.run(["/app/hearth.sh"], capture_output=True, text=True)
        assert proc.returncode != 0
    finally:
        YG.write_text(old)


def test_k09_india() -> None:
    """inner enclosure object has no trailing-ident field."""
    dest = Path("/app/treypit/out9.json")
    _held_a(dest)
    body = _load(dest)
    inner = _pen(body, "inner")
    assert inner is not None
    assert "clip" not in inner


def test_k10_juliet() -> None:
    """trailing sibling keeps a stem string."""
    dest = Path("/app/treypit/out10.json")
    _held_a(dest)
    body = _load(dest)
    outer = _pen(body, "outer")
    assert outer is not None
    nxt = _sibling_after_pen(outer, "inner")
    assert isinstance(nxt.get("stem"), str)


def test_k11_kilo() -> None:
    """outer member list is enclosure then trailing sibling."""
    dest = Path("/app/treypit/out11.json")
    _held_a(dest)
    body = _load(dest)
    outer = _pen(body, "outer")
    assert outer is not None
    kids = outer.get("members") or []
    assert len(kids) == 2
    assert "members" in kids[0]
    assert "members" not in kids[1]


def test_k12_lima() -> None:
    """corrupt dest then MAP helper; held nest still siblings."""
    dest = Path("/app/treypit/out12.json")
    dest.write_text("{\"yard\":\"nope\"}")
    proc = subprocess.run(["/app/hearth.sh"], capture_output=True, text=True)
    assert proc.returncode == 0
    _held_b(dest)
    _assert_native()
