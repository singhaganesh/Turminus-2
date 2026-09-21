"""Held-out checks for ferry stow chalk."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

CLEAT = Path("/opt/ferry/bin/cleat")


def _p(name: str, length: int, ht: int, mass: int, haz: int, board: int) -> str:
    return f"PLATE {name} LEN {length} HT {ht} MASS {mass} HAZ {haz} BOARD {board}"


def _run(tmp_path: Path, lines: list[str], check: bool = True) -> tuple[int, list[dict[str, object]]]:
    roll = tmp_path / "roll"
    chalk = tmp_path / "chalk"
    text = "" if not lines else "\n".join(lines) + "\n"
    roll.write_text(text)
    result = subprocess.run(
        [str(CLEAT), "stow", "--roll", str(roll), "--chalk", str(chalk)],
        capture_output=True,
        text=True,
        check=False,
    )
    if check:
        assert result.returncode == 0, result.stderr
    body = chalk.read_text() if chalk.exists() else ""
    rows = [json.loads(line) for line in body.splitlines() if line.strip()]
    return result.returncode, rows


def _plate(rows: list[dict[str, object]], name: str) -> dict[str, object]:
    matches = [row for row in rows if row.get("plate") == name]
    assert matches, name
    return matches[0]


def test_low_plates_stay_on_low_lid(tmp_path: Path) -> None:
    """Low plates that fit deck A must not occupy a high-lid lane."""
    _, rows = _run(tmp_path, [_p("van-a", 420, 160, 900, 0, 1), _p("van-b", 380, 155, 850, 0, 2)])
    p_van_a = _plate(rows, "van-a")
    assert p_van_a["deck"] == "A"
    p_van_a = _plate(rows, "van-a")
    assert p_van_a["lane"] == "A1"
    p_van_b = _plate(rows, "van-b")
    assert p_van_b["deck"] == "A"
    p_van_b = _plate(rows, "van-b")
    assert p_van_b["ok"] == "yes"


def test_high_box_rejects_low_lid(tmp_path: Path) -> None:
    """A plate taller than the A lid must sit on B1 with a stern station."""
    _, rows = _run(tmp_path, [_p("hi-box", 400, 300, 1200, 0, 1)])
    row = rows[0]
    assert row["deck"] == "B"
    assert row["lane"] == "B1"
    assert int(row["station"]) == 1600
    assert row["ok"] == "yes"


def test_hazmat_keeps_empty_gap(tmp_path: Path) -> None:
    """Two hazmat plates on one lane sit 200 cm apart without moving station by apron."""
    _, rows = _run(tmp_path, [_p("tank-a", 200, 160, 800, 1, 1), _p("tank-b", 200, 160, 800, 1, 2)])
    deep = int(_plate(rows, "tank-a")["station"])
    near = int(_plate(rows, "tank-b")["station"])
    assert deep == 1800
    assert near == 1400
    assert deep - near == 400
    p_tank_a = _plate(rows, "tank-a")
    p_tank_b = _plate(rows, "tank-b")
    assert p_tank_a["lane"] == p_tank_b["lane"]


def test_lofo_deeper_station_for_earlier_seat(tmp_path: Path) -> None:
    """The earlier boarded plate sits deeper than the later one on the same lane."""
    _, rows = _run(tmp_path, [_p("first", 400, 160, 900, 0, 1), _p("later", 300, 160, 900, 0, 2)])
    p_first = _plate(rows, "first")
    p_later = _plate(rows, "later")
    assert int(p_first["station"]) > int(p_later["station"])
    p_first = _plate(rows, "first")
    assert int(p_first["station"]) == 1600
    p_later = _plate(rows, "later")
    assert int(p_later["station"]) == 1300


def test_later_seat_sits_nearer_ramp(tmp_path: Path) -> None:
    """The later boarded plate sits nearer the ramp on the same lane."""
    _, rows = _run(tmp_path, [_p("first", 400, 160, 900, 0, 1), _p("later", 300, 160, 900, 0, 2)])
    p_later = _plate(rows, "later")
    assert int(p_later["station"]) == 1300
    p_later = _plate(rows, "later")
    assert p_later["ok"] == "yes"


def test_lane_length_overflow_rejects(tmp_path: Path) -> None:
    """Plates that cannot fit any remaining span are rejected without geometry fields."""
    lines = [_p(f"c{i}", 1100, 160, 900, 0, i) for i in range(1, 6)]
    _, rows = _run(tmp_path, lines)
    rejected = [row for row in rows if row["ok"] == "no"]
    placed = [row for row in rows if row["ok"] == "yes"]
    assert rejected
    assert all("deck" not in row for row in rejected)
    assert placed
    assert all(row["ok"] == "yes" for row in placed)


def test_mixed_decks_keep_zone_letters(tmp_path: Path) -> None:
    """A mixed roll keeps the low plate on A and the high plate on B."""
    _, rows = _run(tmp_path, [_p("low-a", 400, 150, 900, 0, 1), _p("hi-b", 400, 300, 1200, 0, 2)])
    p_low_a = _plate(rows, "low-a")
    assert p_low_a["deck"] == "A"
    p_hi_b = _plate(rows, "hi-b")
    assert p_hi_b["deck"] == "B"


def test_empty_roll_writes_empty_file(tmp_path: Path) -> None:
    """An empty roll exits 0 and writes no chalk rows."""
    code, rows = _run(tmp_path, [])
    assert code == 0
    assert rows == []


def test_malformed_plate_exits_two(tmp_path: Path) -> None:
    """A non-numeric length is malformed and exits 2 with no chalk rows."""
    code, rows = _run(tmp_path, ["PLATE bad LEN nope HT 160 MASS 900 HAZ 0 BOARD 1"], check=False)
    assert code == 2
    assert rows == []


def test_held_out_three_van_train(tmp_path: Path) -> None:
    """Three equal lengths on A1 use last-on-first-off stations 1500, 1000, 500."""
    _, rows = _run(
        tmp_path,
        [_p("cab", 500, 160, 900, 0, 1), _p("mid", 500, 160, 900, 0, 2), _p("tail", 500, 160, 900, 0, 3)],
    )
    p_cab = _plate(rows, "cab")
    assert int(p_cab["station"]) == 1500
    p_mid = _plate(rows, "mid")
    assert int(p_mid["station"]) == 1000
    p_tail = _plate(rows, "tail")
    assert int(p_tail["station"]) == 500
    p_cab = _plate(rows, "cab")
    assert p_cab["lane"] == "A1"


def test_hazmat_and_height_together(tmp_path: Path) -> None:
    """A tall hazmat plate uses B while a low mate can still sit on A."""
    _, rows = _run(tmp_path, [_p("tall", 300, 300, 1200, 1, 1), _p("mate", 300, 160, 800, 1, 2)])
    p_tall = _plate(rows, "tall")
    assert p_tall["deck"] == "B"
    p_mate = _plate(rows, "mate")
    assert p_mate["deck"] == "A"
    p_tall = _plate(rows, "tall")
    assert int(p_tall["station"]) == 1700


def test_repeat_stow_overwrites_output(tmp_path: Path) -> None:
    """A second stow of the same chalk path replaces the previous rows."""
    _run(tmp_path, [_p("one", 400, 160, 900, 0, 1)])
    _, rows = _run(tmp_path, [_p("two", 350, 160, 900, 0, 1)])
    assert [row["plate"] for row in rows] == ["two"]
    assert int(rows[0]["station"]) == 1650


def test_listing_rows_are_ordered(tmp_path: Path) -> None:
    """Chalk rows follow listing order even when boarding order differs."""
    _, rows = _run(tmp_path, [_p("later", 300, 160, 900, 0, 2), _p("first", 400, 160, 900, 0, 1)])
    assert [row["plate"] for row in rows] == ["later", "first"]
    assert [row["i"] for row in rows] == [1, 2]
    assert int(rows[0]["station"]) == 1300
    assert int(rows[1]["station"]) == 1600
    assert rows[0]["lane"] == "A1"
    assert rows[1]["lane"] == "A1"


def test_zero_length_plate_is_malformed(tmp_path: Path) -> None:
    """Zero length is malformed and exits 2 with no chalk rows."""
    code, rows = _run(tmp_path, [_p("zed", 0, 160, 900, 0, 1)], check=False)
    assert code == 2
    assert rows == []


def test_two_low_plates_share_low_lid_lane(tmp_path: Path) -> None:
    """Two short low plates share A1 leftover centimetres."""
    _, rows = _run(tmp_path, [_p("a", 400, 160, 900, 0, 1), _p("b", 400, 160, 900, 0, 2)])
    p_a = _plate(rows, "a")
    assert p_a["lane"] == "A1"
    p_b = _plate(rows, "b")
    assert p_b["lane"] == "A1"
    p_a = _plate(rows, "a")
    assert int(p_a["station"]) == 1600
    p_b = _plate(rows, "b")
    assert int(p_b["station"]) == 1200


def test_mass_lid_splits_two_heavy_vans(tmp_path: Path) -> None:
    """Two 5000 kg vans that fit A1 centimetres still split across A1 and A2."""
    _, rows = _run(tmp_path, [_p("heavy-a", 400, 160, 5000, 0, 1), _p("heavy-b", 400, 160, 5000, 0, 2)])
    p_heavy_a = _plate(rows, "heavy-a")
    assert p_heavy_a["lane"] == "A1"
    p_heavy_b = _plate(rows, "heavy-b")
    assert p_heavy_b["lane"] == "A2"
    p_heavy_a = _plate(rows, "heavy-a")
    assert p_heavy_a["deck"] == "A"
    p_heavy_b = _plate(rows, "heavy-b")
    assert p_heavy_b["deck"] == "A"
    p_heavy_a = _plate(rows, "heavy-a")
    assert int(p_heavy_a["station"]) == 1600
    p_heavy_b = _plate(rows, "heavy-b")
    assert int(p_heavy_b["station"]) == 1600


def test_leftover_length_stays_on_same_lane(tmp_path: Path) -> None:
    """A later short plate fills leftover centimetres on the open A1 lane."""
    _, rows = _run(tmp_path, [_p("long", 1100, 160, 900, 0, 1), _p("stub", 400, 160, 900, 0, 2)])
    p_long = _plate(rows, "long")
    assert p_long["lane"] == "A1"
    p_stub = _plate(rows, "stub")
    assert p_stub["lane"] == "A1"
    p_long = _plate(rows, "long")
    assert int(p_long["station"]) == 900
    p_stub = _plate(rows, "stub")
    assert int(p_stub["station"]) == 500


def test_equal_seat_breaks_on_plate_name(tmp_path: Path) -> None:
    """Equal BOARD values pack in ascending plate name while chalk stays listed."""
    _, rows = _run(tmp_path, [_p("zeta", 400, 160, 900, 0, 1), _p("alpha", 400, 160, 900, 0, 1)])
    assert [row["plate"] for row in rows] == ["zeta", "alpha"]
    p_alpha = _plate(rows, "alpha")
    assert int(p_alpha["station"]) == 1600
    p_zeta = _plate(rows, "zeta")
    assert int(p_zeta["station"]) == 1200
    p_alpha = _plate(rows, "alpha")
    assert p_alpha["lane"] == "A1"
    p_zeta = _plate(rows, "zeta")
    assert p_zeta["lane"] == "A1"


def test_haz_after_clean_still_gaps(tmp_path: Path) -> None:
    """A hazmat plate after a clean neighbour still leaves a 100 cm gap."""
    _, rows = _run(tmp_path, [_p("clean", 400, 160, 900, 0, 1), _p("tank", 200, 160, 800, 1, 2)])
    p_clean = _plate(rows, "clean")
    p_tank = _plate(rows, "tank")
    assert p_clean["lane"] == p_tank["lane"]
    p_clean = _plate(rows, "clean")
    assert int(p_clean["station"]) == 1600
    p_tank = _plate(rows, "tank")
    assert int(p_tank["station"]) == 1300


def test_missing_mass_is_malformed(tmp_path: Path) -> None:
    """A line without MASS is malformed and exits 2."""
    code, rows = _run(tmp_path, ["PLATE old LEN 400 HT 160 HAZ 0 BOARD 1"], check=False)
    assert code == 2
    assert rows == []


def test_zero_mass_is_malformed(tmp_path: Path) -> None:
    """Zero mass is malformed and exits 2 with no chalk rows."""
    code, rows = _run(tmp_path, [_p("zed", 400, 160, 0, 0, 1)], check=False)
    assert code == 2
    assert rows == []


def test_seating_order_keeps_stub_on_a1(tmp_path: Path) -> None:
    """A long plate listed first must not steal A1 leftover from an earlier boarded stub."""
    _, rows = _run(tmp_path, [_p("long", 1800, 160, 900, 0, 2), _p("stub", 400, 160, 900, 0, 1)])
    assert [row["plate"] for row in rows] == ["long", "stub"]
    p_stub = _plate(rows, "stub")
    assert p_stub["lane"] == "A1"
    p_long = _plate(rows, "long")
    assert p_long["lane"] == "A2"
    p_stub = _plate(rows, "stub")
    assert int(p_stub["station"]) == 1600
    p_long = _plate(rows, "long")
    assert int(p_long["station"]) == 200


def test_mass_split_follows_boarding_not_listing(tmp_path: Path) -> None:
    """Kilogram overflow follows boarding order, not the order names appear in the roll."""
    _, rows = _run(
        tmp_path,
        [_p("listed-first", 400, 160, 5000, 0, 2), _p("earlier-board", 400, 160, 5000, 0, 1)],
    )
    p_earlier_board = _plate(rows, "earlier-board")
    assert p_earlier_board["lane"] == "A1"
    p_listed_first = _plate(rows, "listed-first")
    assert p_listed_first["lane"] == "A2"
    p_earlier_board = _plate(rows, "earlier-board")
    assert int(p_earlier_board["station"]) == 1600
    p_listed_first = _plate(rows, "listed-first")
    assert int(p_listed_first["station"]) == 1600


def test_deck_pair_blocks_third_on_a(tmp_path: Path) -> None:
    """A third van that still fits A1 leftover kilograms must not break the A pair lid."""
    _, rows = _run(
        tmp_path,
        [
            _p("heavy-a", 400, 160, 5000, 0, 1),
            _p("heavy-b", 400, 160, 5000, 0, 2),
            _p("extra", 400, 160, 1500, 0, 3),
        ],
    )
    p_heavy_a = _plate(rows, "heavy-a")
    assert p_heavy_a["lane"] == "A1"
    p_heavy_b = _plate(rows, "heavy-b")
    assert p_heavy_b["lane"] == "A2"
    p_extra = _plate(rows, "extra")
    assert p_extra["deck"] == "B"
    p_extra = _plate(rows, "extra")
    assert p_extra["lane"] == "B1"
    p_extra = _plate(rows, "extra")
    assert int(p_extra["station"]) == 1600


def test_haz_keepclear_rejects_span_fit(tmp_path: Path) -> None:
    """A hazmat plate whose length fits the span still fails once the ramp keep-clear is counted."""
    code, rows = _run(tmp_path, [_p("tank", 1950, 160, 800, 1, 1)])
    assert code == 0
    assert rows[0]["ok"] == "no"
    assert "deck" not in rows[0]
    assert "lane" not in rows[0]
    assert "station" not in rows[0]


def test_clean_span_fit_without_keepclear(tmp_path: Path) -> None:
    """A clean plate of the same length still fits A1 without a ramp keep-clear."""
    _, rows = _run(tmp_path, [_p("van", 1950, 160, 800, 0, 1)])
    assert rows[0]["ok"] == "yes"
    assert rows[0]["lane"] == "A1"
    assert int(rows[0]["station"]) == 50


def test_haz_keepclear_allows_exact_span(tmp_path: Path) -> None:
    """A hazmat plate that uses the full span plus keep-clear still sits at station 100."""
    _, rows = _run(tmp_path, [_p("tank", 1900, 160, 800, 1, 1)])
    assert rows[0]["ok"] == "yes"
    assert rows[0]["lane"] == "A1"
    assert int(rows[0]["station"]) == 100


def test_sister_balance_spills_unbalanced_follow_on(tmp_path: Path) -> None:
    """After both A sisters are occupied, a 5500 kg follow-on must spill to B for trim."""
    _, rows = _run(
        tmp_path,
        [
            _p("left", 1100, 160, 2000, 0, 1),
            _p("right", 1100, 160, 2000, 0, 2),
            _p("chunk", 400, 160, 5500, 0, 3),
        ],
    )
    p_left = _plate(rows, "left")
    assert p_left["lane"] == "A1"
    p_right = _plate(rows, "right")
    assert p_right["lane"] == "A2"
    p_chunk = _plate(rows, "chunk")
    assert p_chunk["deck"] == "B"
    p_chunk = _plate(rows, "chunk")
    assert p_chunk["lane"] == "B1"
    p_chunk = _plate(rows, "chunk")
    assert int(p_chunk["station"]) == 1600
