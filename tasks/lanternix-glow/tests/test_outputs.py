"""Verifier for lanternix mill readout."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

BIN = "/app/bin/lanternix"
REG = Path("/app/packbay/reg.go")
UNITS = Path("/app/packbay/units")
CARDS = Path("/app/cardwell")
READ = Path("/app/glowbank/readout.json")
FLASH = "/app/lamps/flash9c.lamp"
HELD = "/app/lamps/held.lamp"
WARM = "/app/lamps/warm.lamp"
BEAM = "/app/lamps/beam.lamp"
ALIEN = "/app/lamps/alien.lamp"
RECIPE_LAMPS = (FLASH, HELD, WARM, BEAM)


def _card_ids() -> list[str]:
    ids: list[str] = []
    for path in sorted(CARDS.glob("*.card")):
        for line in path.read_text().splitlines():
            if line.startswith("id:"):
                ids.append(line.split(":", 1)[1].strip())
    return sorted(set(ids))


def _lamp_vals(path: str) -> tuple[str, dict[str, str]]:
    code = ""
    vals: dict[str, str] = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line.startswith("CODE "):
            code = line[5:].strip()
        elif "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip()
    return code, vals


def _readout(lamp: str) -> tuple[dict, int]:
    proc = subprocess.run(
        [BIN, "readout", "--lamp", lamp],
        capture_output=True,
        text=True,
        check=False,
    )
    if not READ.exists():
        return {}, proc.returncode
    try:
        return json.loads(READ.read_text()), proc.returncode
    except json.JSONDecodeError:
        return {}, proc.returncode


def test_lx00_native_mill():
    """Mill at /app/bin/lanternix is ELF and links every generated unit."""
    blob = Path(BIN).read_bytes()
    assert blob[:4] == b"\x7fELF"
    reg = REG.read_text()
    names = sorted(p.name for p in UNITS.iterdir() if p.is_dir())
    assert names
    for name in names:
        assert f"packbay/units/{name}" in reg


def test_lx01_id_parity():
    """Every recipe lamp must decode with a mill that covers that card id."""
    seen: set[str] = set()
    for lamp in RECIPE_LAMPS:
        data, rc = _readout(lamp)
        code, _ = _lamp_vals(lamp)
        assert rc == 0
        assert data["code"] == code
        seen.add(code)
    assert seen == set(_card_ids())


def test_lx02_anchor_pair():
    """Flash lamp must decode candela and dwell_s from the take."""
    data, rc = _readout(FLASH)
    code, vals = _lamp_vals(FLASH)
    assert rc == 0
    assert data["code"] == code
    assert data["slots"]["candela"] == vals["candela"]
    assert data["slots"]["dwell_s"] == vals["dwell_s"]


def test_lx03_held_pair():
    """Held lamp must decode trimmed hue and period_s."""
    data, rc = _readout(HELD)
    code, vals = _lamp_vals(HELD)
    assert rc == 0
    assert data["code"] == code
    assert data["slots"]["hue"] == vals["hue"]
    assert data["slots"]["period_s"] == vals["period_s"]


def test_lx04_prior_pair():
    """Warm lamp must still decode lux and hold_s."""
    data, rc = _readout(WARM)
    code, vals = _lamp_vals(WARM)
    assert rc == 0
    assert data["code"] == code
    assert data["slots"]["lux"] == vals["lux"]
    assert data["slots"]["hold_s"] == vals["hold_s"]


def test_lx05_alien_exit():
    """Lamp codes absent from recipes report void and exit non-zero."""
    data, rc = _readout(ALIEN)
    assert rc != 0
    assert data.get("code") == "void"
    assert data.get("slots") == {}


def test_lx06_gap_abort():
    """A recipe card the mill does not carry must abort readout and keep prior JSON."""
    ghost = CARDS / "ghost.card"
    sentinel = '{"code":"sentinel","slots":{}}\n'
    READ.write_text(sentinel)
    ghost.write_text("id: LAN_MISS_00\nslots: x\n")
    try:
        proc = subprocess.run(
            [BIN, "readout", "--lamp", FLASH],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode != 0
        assert READ.read_text() == sentinel
    finally:
        if ghost.exists():
            ghost.unlink()
    data, rc = _readout(FLASH)
    assert rc == 0
    assert data.get("code") == _lamp_vals(FLASH)[0]


def test_lx07_json_shape():
    """Readout JSON has string code and object slots."""
    data, rc = _readout(BEAM)
    assert rc == 0
    assert isinstance(data["code"], str)
    assert isinstance(data["slots"], dict)
    for key in data["slots"]:
        assert key == key.strip()


def test_lx08_slot_width():
    """Flash readout slot count matches the candela/dwell_s pair on the lamp."""
    data, rc = _readout(FLASH)
    _, vals = _lamp_vals(FLASH)
    assert rc == 0
    assert set(data["slots"]) == {"candela", "dwell_s"}
    assert data["slots"]["candela"] == vals["candela"]


def test_lx09_cross_bind():
    """Decoded recipe codes match the card id set."""
    got = set()
    for lamp in RECIPE_LAMPS:
        data, rc = _readout(lamp)
        assert rc == 0
        got.add(data["code"])
    assert got == set(_card_ids())


def test_lx10_held_second():
    """Second held-style lamp (beam) must decode both declared slots."""
    data, rc = _readout(BEAM)
    _, vals = _lamp_vals(BEAM)
    assert rc == 0
    assert data["slots"]["az_deg"] == vals["az_deg"]
    assert data["slots"]["el_deg"] == vals["el_deg"]


def test_lx11_twice_stable():
    """A second readout of the flash lamp must match the lamp file and the first payload."""
    code, vals = _lamp_vals(FLASH)
    a, ra = _readout(FLASH)
    b, rb = _readout(FLASH)
    assert ra == 0 and rb == 0
    assert a == b
    assert a["code"] == code
    assert a["slots"]["candela"] == vals["candela"]
    assert a["slots"]["dwell_s"] == vals["dwell_s"]


def test_lx12_holdout_lamp_vals():
    """Grade-time recipe lamps with held-out values must decode through readout only."""
    held = Path(__file__).resolve().parent / "heldout"
    for name, keys in (
        ("flash_alt.lamp", ("candela", "dwell_s")),
        ("warm_alt.lamp", ("lux", "hold_s")),
    ):
        path = str(held / name)
        data, rc = _readout(path)
        code, vals = _lamp_vals(path)
        assert rc == 0
        assert data["code"] == code
        for key in keys:
            assert data["slots"][key] == vals[key]


def test_lx13_escape_slots():
    """Cast must emit packs that still decode when a card slot name is not a bare token."""
    held = Path(__file__).resolve().parent / "heldout"
    flare = CARDS / "flare.card"
    original = flare.read_text()
    lamp = str(held / "escape.lamp")
    try:
        flare.write_text((held / "escape.card").read_text())
        proc = subprocess.run(
            [BIN, "cast"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0
        data, rc = _readout(lamp)
        code, vals = _lamp_vals(lamp)
        assert rc == 0
        assert data["code"] == code
        assert set(data["slots"]) == set(vals)
        for name, value in vals.items():
            assert data["slots"][name] == value
    finally:
        flare.write_text(original)
        subprocess.run(
            [BIN, "cast"],
            capture_output=True,
            text=True,
            check=False,
        )


def test_lx_zz_corrupt_recover():
    """Cast must restore mill readout after a corrupt glowbank file."""
    READ.write_text("{}\n")
    proc = subprocess.run(
        [BIN, "cast"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    data, rc = _readout(FLASH)
    assert rc == 0
    assert data.get("code") == _lamp_vals(FLASH)[0]
