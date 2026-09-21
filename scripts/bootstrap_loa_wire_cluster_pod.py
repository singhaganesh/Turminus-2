#!/usr/bin/env python3
"""One-shot bootstrap for tasks/loa-wire-cluster-pod."""

from __future__ import annotations

import hashlib
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "tasks" / "loa-wire-cluster-pod"
ENV = TASK / "environment"

DIRS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]


def sign(n: int) -> int:
    return (n > 0) - (n < 0)


def parse(coord: str) -> tuple[int, int]:
    return int(coord[1]) - 1, ord(coord[0]) - ord("a")


def sq(row: int, col: int) -> str:
    return f"{chr(ord('a') + col)}{row + 1}"


def load_board(name: str) -> dict[str, str]:
    data = json.loads((ENV / "data" / "boards" / f"{name}.json").read_text())
    return dict(data["pieces"])


def queen_dir(fr: str, to: str) -> tuple[int, int] | None:
    sr, sc = parse(fr)
    er, ec = parse(to)
    dr = sign(er - sr)
    dc = sign(ec - sc)
    if dr == 0 and dc == 0:
        return None
    if dr != 0 and dc != 0 and abs(er - sr) != abs(ec - sc):
        return None
    if dr == 0 and sr != er:
        return 0, sign(ec - sc)
    if dc == 0 and sc != ec:
        return sign(er - sr), 0
    if dr != 0 and dc != 0:
        return dr, dc
    return None


def line_count(board: dict[str, str], fr: str, direction: tuple[int, int]) -> int:
    sr, sc = parse(fr)
    dr, dc = direction
    count = 0
    for r in range(8):
        for c in range(8):
            coord = sq(r, c)
            if board.get(coord, ".") == ".":
                continue
            rr, cc = r - sr, c - sc
            if dr == 0 and cc != 0:
                continue
            if dc == 0 and rr != 0:
                continue
            if dr != 0 and dc != 0 and rr * dc != cc * dr:
                continue
            count += 1
    return count


def hops(fr: str, to: str) -> int:
    sr, sc = parse(fr)
    er, ec = parse(to)
    return max(abs(er - sr), abs(ec - sc))


def path_clear(board: dict[str, str], fr: str, to: str) -> bool:
    sr, sc = parse(fr)
    er, ec = parse(to)
    dr = sign(er - sr)
    dc = sign(ec - sc)
    r, c = sr + dr, sc + dc
    while (r, c) != (er, ec):
        if board.get(sq(r, c), ".") != ".":
            return False
        r += dr
        c += dc
    return True


def legal(board: dict[str, str], side: str, fr: str, to: str) -> bool:
    if board.get(fr) != side or board.get(to, ".") == side:
        return False
    direction = queen_dir(fr, to)
    if direction is None:
        return False
    dist = hops(fr, to)
    if dist < 1:
        return False
    if not path_clear(board, fr, to):
        return False
    return line_count(board, fr, direction) == dist


def apply(board: dict[str, str], side: str, fr: str, to: str) -> dict[str, str]:
    nxt = dict(board)
    nxt[to] = side
    nxt[fr] = "."
    return nxt


def neighbors(row: int, col: int) -> list[tuple[int, int]]:
    out = []
    for dr, dc in DIRS:
        r, c = row + dr, col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            out.append((r, c))
    return out


def components(board: dict[str, str], side: str) -> int:
    seen: set[str] = set()
    count = 0
    for coord, piece in board.items():
        if piece != side or coord in seen:
            continue
        count += 1
        stack = [coord]
        seen.add(coord)
        while stack:
            cur = stack.pop()
            r, c = parse(cur)
            for nr, nc in neighbors(r, c):
                nxt = sq(nr, nc)
                if board.get(nxt) == side and nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
    return count


def connected(board: dict[str, str], side: str) -> bool:
    pieces = [c for c, p in board.items() if p == side]
    if not pieces:
        return False
    return components(board, side) == 1


def legal_moves(board: dict[str, str], side: str) -> list[tuple[str, str]]:
    moves = []
    for fr, piece in board.items():
        if piece != side:
            continue
        sr, sc = parse(fr)
        for dr, dc in DIRS:
            r, c = sr + dr, sc + dc
            while 0 <= r < 8 and 0 <= c < 8:
                to = sq(r, c)
                if legal(board, side, fr, to):
                    moves.append((fr, to))
                r += dr
                c += dc
    return moves


def finish(board: dict[str, str], mover: str) -> tuple[str | None, str | None]:
    foe = "B" if mover == "W" else "W"
    if connected(board, mover):
        return mover, "connect"
    if not legal_moves(board, foe):
        if not legal_moves(board, mover):
            return "draw", "immobile"
        return mover, "immobile"
    return None, None


def replay_manifest(text: str) -> dict:
    matches = []
    for block in [chunk.strip() for chunk in text.strip().split("\n\n") if chunk.strip()]:
        rows = block.splitlines()
        match_id = rows[0].split()[1]
        board_name = "classic"
        start = 1
        if rows[1].startswith("board "):
            board_name = rows[1].split()[1]
            start = 2
        state = load_board(board_name)
        plies = []
        winner = "draw"
        finish_reason = "immobile"
        stopped = False
        for index, line in enumerate(rows[start:], 1):
            side, fr, to = line.split()
            direction = queen_dir(fr, to)
            ok = legal(state, side, fr, to)
            lc = line_count(state, fr, direction) if direction else 0
            dist = hops(fr, to) if direction else 0
            captured = state.get(to, ".") not in (".", side)
            if not ok:
                plies.append(
                    {
                        "ply": index,
                        "side": side,
                        "from": fr,
                        "to": to,
                        "legal": False,
                        "line_count": lc,
                        "hops": dist,
                        "captured": captured,
                        "components_w": components(state, "W"),
                        "components_b": components(state, "B"),
                        "connected_w": connected(state, "W"),
                        "connected_b": connected(state, "B"),
                    }
                )
                winner = "B" if side == "W" else "W"
                finish_reason = "illegal"
                stopped = True
                break
            state = apply(state, side, fr, to)
            plies.append(
                {
                    "ply": index,
                    "side": side,
                    "from": fr,
                    "to": to,
                    "legal": True,
                    "line_count": lc,
                    "hops": dist,
                    "captured": captured,
                    "components_w": components(state, "W"),
                    "components_b": components(state, "B"),
                    "connected_w": connected(state, "W"),
                    "connected_b": connected(state, "B"),
                }
            )
            win, fin = finish(state, side)
            if win:
                winner = win
                finish_reason = fin
                stopped = True
                break
        if not stopped and plies:
            win, fin = finish(state, plies[-1]["side"])
            if win:
                winner = win
                finish_reason = fin
        matches.append(
            {"match_id": match_id, "plies": plies, "winner": winner, "finish": finish_reason}
        )
    return {"matches": matches}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main() -> None:
    TASK.mkdir(parents=True, exist_ok=True)

    boards = {
        "classic": {
            "pieces": {
                **{sq(0, c): "B" for c in range(8)},
                **{sq(1, c): "W" for c in range(8)},
                **{sq(6, c): "W" for c in range(8)},
                **{sq(7, c): "B" for c in range(8)},
            }
        },
        "split": {
            "pieces": {
                **{sq(0, c): "B" for c in range(8)},
                **{sq(1, c): "W" for c in range(8)},
                **{sq(6, c): "W" for c in range(8)},
                **{sq(7, c): "B" for c in range(8)},
                "d4": "W",
                "e5": "B",
            }
        },
        "narrow": {
            "pieces": {
                "a1": "B",
                "h1": "B",
                "a8": "B",
                "h8": "B",
                "b2": "W",
                "g2": "W",
                "b7": "W",
                "g7": "W",
                "d4": "W",
                "e4": "B",
            }
        },
    }

    matches_txt = textwrap.dedent(
        """\
        match canal_link
        board classic
        W b2 b4
        B g7 g5
        W c1 c3
        B f8 f6
        W d2 d4
        B e7 e5

        match split_merge
        board split
        W d4 e6
        B e5 c7
        W b2 d2
        B g7 e7
        W d2 f2
        B c7 e5
        W f2 f4
        B e7 c7
        W f4 d4

        match narrow_wire
        board narrow
        W b2 d4
        B e4 c6
        W d4 f6
        B c6 e4
        W g2 e4
        """
    )

    league_txt = textwrap.dedent(
        """\
        player Anya canal_link W
        player Ben canal_link B
        player Cara split_merge W
        player Dex split_merge B
        player Elio narrow_wire W
        player Fay narrow_wire B
        """
    )

    for name, body in boards.items():
        write(ENV / "data" / "boards" / f"{name}.json", json.dumps(body, indent=2) + "\n")
    write(ENV / "data" / "manifests" / "matches.txt", matches_txt)
    write(ENV / "data" / "manifests" / "league.txt", league_txt)

    trace = replay_manifest(matches_txt)
    print(json.dumps(trace, indent=2)[:500])


if __name__ == "__main__":
    main()
