#!/usr/bin/env python3
"""Generate tasks/loa-wire-cluster-pod end-to-end."""

from __future__ import annotations

import hashlib
import json
import subprocess
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
    if dist < 1 or not path_clear(board, fr, to):
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


def expected_standings(trace: dict, league_text: str) -> dict:
    meta = {m["match_id"]: m for m in trace["matches"]}
    stats: dict[str, dict] = {}
    for line in league_text.splitlines():
        if not line.strip().startswith("player "):
            continue
        _, player, match_id, side = line.split()
        row = stats.setdefault(
            player,
            {
                "player": player,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "connect_wins": 0,
                "wire_bonus": 0,
                "points": 0,
            },
        )
        match = meta[match_id]
        winner = match["winner"]
        if winner == "draw":
            row["draws"] += 1
            row["points"] += 1
        elif winner == side:
            row["wins"] += 1
            row["points"] += 3
            if match["finish"] == "connect":
                row["connect_wins"] += 1
                row["points"] += 2
            last = match["plies"][-1]
            if last["legal"] and last["line_count"] >= 3:
                row["wire_bonus"] += 1
                row["points"] += 1
        else:
            row["losses"] += 1
    rows = sorted(
        stats.values(),
        key=lambda item: (-item["points"], -item["connect_wins"], -item["wire_bonus"], item["player"]),
    )
    rank = 1
    for index, row in enumerate(rows):
        if index > 0 and (
            rows[index - 1]["points"],
            rows[index - 1]["connect_wins"],
            rows[index - 1]["wire_bonus"],
        ) != (row["points"], row["connect_wins"], row["wire_bonus"]):
            rank = index + 1
        row["rank"] = rank
    body = "\n".join(f"{row['player']}|{row['points']}|{row['rank']}" for row in rows)
    digest = hashlib.sha256(body.encode()).hexdigest()[:16]
    return {"rows": rows, "digest": digest}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def patch_file(rel: str, old: str, new: str, patch_dir: Path, name: str) -> None:
    body = textwrap.dedent(
        f"""\
        --- {rel}
        +++ {rel}
        @@ -1,1 +1,1 @@
        """
    )
    for o, n in zip(old.splitlines(), new.splitlines()):
        if o != n:
            break
    # unified diff via diff command
    src = ENV / rel
    fixed = patch_dir / f"{name}.fixed.ts"
    fixed.write_text(new)
    proc = subprocess.run(
        ["diff", "-u", str(src), str(fixed)],
        capture_output=True,
        text=True,
    )
    patch_path = patch_dir / f"{name}.patch"
    lines = proc.stdout.splitlines()
    if lines:
        lines[0] = f"--- {rel}"
        lines[1] = f"+++ {rel}"
    patch_path.write_text("\n".join(lines) + "\n")


# TypeScript sources (broken baseline)
LINE_SCAN_BROKEN = """\
import { BoardGrid } from "../core/BoardGrid";
import { Coord } from "../core/Coord";

export class LineScan {
  static count(board: BoardGrid, from: string, dr: number, dc: number, side: string): number {
    const origin = Coord.parse(from);
    let total = 0;
    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const label = Coord.label(row, col);
        const piece = board.at(label);
        if (piece === ".") continue;
        if (piece !== side) continue;
        const rr = row - origin.row;
        const cc = col - origin.col;
        if (dr === 0 && cc !== 0) continue;
        if (dc === 0 && rr !== 0) continue;
        if (dr !== 0 && dc !== 0 && rr * dc !== cc * dr) continue;
        total += 1;
      }
    }
    return total;
  }
}
"""

LINE_SCAN_FIXED = LINE_SCAN_BROKEN.replace(
    "if (piece !== side) continue;\n", ""
)

CLUSTER_BROKEN = """\
import { BoardGrid } from "../core/BoardGrid";
import { Coord } from "../core/Coord";

const ORTHO = [[-1, 0], [1, 0], [0, -1], [0, 1]];

export class ClusterProbe {
  static components(board: BoardGrid, side: string): number {
    const seen = new Set<string>();
    let groups = 0;
    for (const [coord, piece] of board.entries()) {
      if (piece !== side || seen.has(coord)) continue;
      groups += 1;
      const stack = [coord];
      seen.add(coord);
      while (stack.length) {
        const cur = stack.pop()!;
        const { row, col } = Coord.parse(cur);
        for (const [dr, dc] of ORTHO) {
          const label = Coord.label(row + dr, col + dc);
          if (board.at(label) === side && !seen.has(label)) {
            seen.add(label);
            stack.push(label);
          }
        }
      }
    }
    return groups;
  }

  static connected(board: BoardGrid, side: string): boolean {
    let count = 0;
    for (const piece of board.values()) if (piece === side) count += 1;
    if (count === 0) return false;
    return ClusterProbe.components(board, side) === 1;
  }
}
"""

CLUSTER_FIXED = CLUSTER_BROKEN.replace(
    "const ORTHO = [[-1, 0], [1, 0], [0, -1], [0, 1]];",
    "const NEIGH = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];",
).replace("ORTHO", "NEIGH")

SCRIPT_RUNNER_BROKEN = """\
import fs from "node:fs";
import { BoardGrid } from "../core/BoardGrid";
import { WireMove } from "./WireMove";
import { ClusterProbe } from "./ClusterProbe";
import { LineScan } from "./LineScan";
import { Side } from "../core/Side";
import { queenDir, hopCount } from "../core/BoardGrid";

type Ply = Record<string, unknown>;

export class ScriptRunner {
  run(manifestPath: string, outPath: string): void {
    const text = fs.readFileSync(manifestPath, "utf8");
    const matches = [];
    for (const block of text.trim().split(/\\n\\n+/)) {
      const rows = block.trim().split("\\n");
      const matchId = rows[0].split(/\\s+/)[1];
      let boardName = "classic";
      let start = 1;
      if (rows[1].startsWith("board ")) {
        boardName = rows[1].split(/\\s+/)[1];
        start = 2;
      }
      let board = BoardGrid.load(boardName);
      const plies: Ply[] = [];
      let winner: string = "draw";
      let finish = "immobile";
      for (let index = start; index < rows.length; index++) {
        const [side, from, to] = rows[index].split(/\\s+/);
        const plyNo = index - start + 1;
        const dir = queenDir(from, to);
        const ok = WireMove.legal(board, side, from, to);
        const lc = dir ? LineScan.count(board, from, dir[0], dir[1], side) : 0;
        const dist = dir ? hopCount(from, to) : 0;
        const captured = board.at(to) !== "." && board.at(to) !== side;
        if (!ok) {
          plies.push(this.row(plyNo, side, from, to, false, lc, dist, captured, board));
          winner = side === "W" ? "B" : "W";
          finish = "illegal";
          break;
        }
        board = WireMove.apply(board, side, from, to);
        plies.push(this.row(plyNo, side, from, to, true, lc, dist, captured, board));
        const verdict = WireMove.finish(board, side);
        if (verdict) {
          winner = verdict[0];
          finish = verdict[1];
          break;
        }
      }
      if (plies.length && winner === "draw") {
        const last = plies[plies.length - 1] as { side: string };
        const verdict = WireMove.finish(board, last.side);
        if (verdict) {
          winner = verdict[0];
          finish = verdict[1];
        }
      }
      matches.push({ match_id: matchId, plies, winner, finish });
    }
    fs.writeFileSync(outPath, JSON.stringify({ matches }, null, 2) + "\\n");
  }

  private row(
    ply: number,
    side: string,
    from: string,
    to: string,
    legal: boolean,
    lineCount: number,
    hops: number,
    captured: boolean,
    board: BoardGrid,
  ): Ply {
    return {
      ply,
      side,
      from,
      to,
      legal,
      line_count: lineCount,
      hops,
      captured,
      components_w: ClusterProbe.components(board, "W"),
      components_b: ClusterProbe.components(board, "B"),
      connected_w: ClusterProbe.connected(board, "W"),
      connected_b: ClusterProbe.connected(board, "B"),
    };
  }
}
"""

SCRIPT_RUNNER_FIXED = SCRIPT_RUNNER_BROKEN.replace(
    "plies.push(this.row(plyNo, side, from, to, false, lc, dist, captured, board));\n          winner = side === \"W\" ? \"B\" : \"W\";\n          finish = \"illegal\";\n          break;",
    "plies.push(this.row(plyNo, side, from, to, false, lc, dist, captured, board));\n          winner = side === \"W\" ? \"B\" : \"W\";\n          finish = \"illegal\";\n          matches.push({ match_id: matchId, plies, winner, finish });\n          continue;",
).replace(
    "matches.push({ match_id: matchId, plies, winner, finish });\n    }",
    "matches.push({ match_id: matchId, plies, winner, finish });\n    }\n    fs.writeFileSync(outPath, JSON.stringify({ matches }, null, 2) + \"\\n\");\n  }\n\n  private rowEnd(",
)

# Fix script runner properly - the broken version stops entire manifest on illegal; 
# fixed continues to next match block. Also broken applies move on illegal - already doesn't.

SCRIPT_RUNNER_FIXED = """\
import fs from "node:fs";
import { BoardGrid } from "../core/BoardGrid";
import { WireMove } from "./WireMove";
import { ClusterProbe } from "./ClusterProbe";
import { LineScan } from "./LineScan";
import { queenDir, hopCount } from "../core/BoardGrid";

type Ply = Record<string, unknown>;

export class ScriptRunner {
  run(manifestPath: string, outPath: string): void {
    const text = fs.readFileSync(manifestPath, "utf8");
    const matches = [];
    for (const block of text.trim().split(/\\n\\n+/)) {
      const rows = block.trim().split("\\n");
      const matchId = rows[0].split(/\\s+/)[1];
      let boardName = "classic";
      let start = 1;
      if (rows[1].startsWith("board ")) {
        boardName = rows[1].split(/\\s+/)[1];
        start = 2;
      }
      let board = BoardGrid.load(boardName);
      const plies: Ply[] = [];
      let winner: string = "draw";
      let finish = "immobile";
      let stopped = false;
      for (let index = start; index < rows.length; index++) {
        const [side, from, to] = rows[index].split(/\\s+/);
        const plyNo = index - start + 1;
        const dir = queenDir(from, to);
        const ok = WireMove.legal(board, side, from, to);
        const lc = dir ? LineScan.count(board, from, dir[0], dir[1], side) : 0;
        const dist = dir ? hopCount(from, to) : 0;
        const captured = board.at(to) !== "." && board.at(to) !== side;
        if (!ok) {
          plies.push(this.row(plyNo, side, from, to, false, lc, dist, captured, board));
          winner = side === "W" ? "B" : "W";
          finish = "illegal";
          stopped = true;
          break;
        }
        board = WireMove.apply(board, side, from, to);
        plies.push(this.row(plyNo, side, from, to, true, lc, dist, captured, board));
        const verdict = WireMove.finish(board, side);
        if (verdict) {
          winner = verdict[0];
          finish = verdict[1];
          stopped = true;
          break;
        }
      }
      if (!stopped && plies.length) {
        const last = plies[plies.length - 1] as { side: string };
        const verdict = WireMove.finish(board, last.side);
        if (verdict) {
          winner = verdict[0];
          finish = verdict[1];
        }
      }
      matches.push({ match_id: matchId, plies, winner, finish });
    }
    fs.writeFileSync(outPath, JSON.stringify({ matches }, null, 2) + "\\n");
  }

  private row(
    ply: number,
    side: string,
    from: string,
    to: string,
    legal: boolean,
    lineCount: number,
    hops: number,
    captured: boolean,
    board: BoardGrid,
  ): Ply {
    return {
      ply,
      side,
      from,
      to,
      legal,
      line_count: lineCount,
      hops,
      captured,
      components_w: ClusterProbe.components(board, "W"),
      components_b: ClusterProbe.components(board, "B"),
      connected_w: ClusterProbe.connected(board, "W"),
      connected_b: ClusterProbe.connected(board, "B"),
    };
  }
}
"""

POD_FOLD_BROKEN = """\
import fs from "node:fs";

type Trace = { matches: Array<{ match_id: string; winner: string; finish: string; plies: Array<{ legal: boolean; line_count: number }> }> };

export class PodFold {
  run(leaguePath: string, tracePath: string, outPath: string): void {
    const league = fs.readFileSync(leaguePath, "utf8");
    const trace = JSON.parse(fs.readFileSync(tracePath, "utf8")) as Trace;
    const meta = new Map(trace.matches.map((m) => [m.match_id, m]));
    const stats = new Map<string, Record<string, number | string>>();
    for (const line of league.split("\\n")) {
      if (!line.startsWith("player ")) continue;
      const [, player, matchId, side] = line.split(/\\s+/);
      const row = stats.get(player) ?? {
        player,
        wins: 0,
        losses: 0,
        draws: 0,
        connect_wins: 0,
        wire_bonus: 0,
        points: 0,
      };
      const match = meta.get(matchId)!;
      const winner = match.winner;
      if (winner === "draw") {
        row.draws = (row.draws as number) + 1;
        row.points = (row.points as number) + 1;
      } else if (winner === side) {
        row.wins = (row.wins as number) + 1;
        row.points = (row.points as number) + 3;
        if (match.finish === "connect") {
          row.connect_wins = (row.connect_wins as number) + 1;
        }
        const last = match.plies[match.plies.length - 1];
        if (last.legal && last.line_count >= 3) {
          row.wire_bonus = (row.wire_bonus as number) + 1;
        }
      } else {
        row.losses = (row.losses as number) + 1;
      }
      stats.set(player, row);
    }
    const rows = [...stats.values()].sort((a, b) => String(a.player).localeCompare(String(b.player)));
    let rank = 1;
    for (let i = 0; i < rows.length; i++) {
      rows[i].rank = rank;
      if (i + 1 < rows.length) rank += 1;
    }
    const body = rows.map((r) => `${r.player}|${r.points}|${r.rank}`).join("\\n");
    const digest = require("node:crypto").createHash("sha256").update(body).digest("hex").slice(0, 16);
    fs.writeFileSync(outPath, JSON.stringify({ rows, digest }, null, 2) + "\\n");
  }
}
"""

POD_FOLD_FIXED = """\
import fs from "node:fs";
import crypto from "node:crypto";

type Trace = { matches: Array<{ match_id: string; winner: string; finish: string; plies: Array<{ legal: boolean; line_count: number }> }> };

export class PodFold {
  run(leaguePath: string, tracePath: string, outPath: string): void {
    const league = fs.readFileSync(leaguePath, "utf8");
    const trace = JSON.parse(fs.readFileSync(tracePath, "utf8")) as Trace;
    const meta = new Map(trace.matches.map((m) => [m.match_id, m]));
    const stats = new Map<string, Record<string, number | string>>();
    for (const line of league.split("\\n")) {
      if (!line.startsWith("player ")) continue;
      const [, player, matchId, side] = line.split(/\\s+/);
      const row = stats.get(player) ?? {
        player,
        wins: 0,
        losses: 0,
        draws: 0,
        connect_wins: 0,
        wire_bonus: 0,
        points: 0,
      };
      const match = meta.get(matchId)!;
      const winner = match.winner;
      if (winner === "draw") {
        row.draws = (row.draws as number) + 1;
        row.points = (row.points as number) + 1;
      } else if (winner === side) {
        row.wins = (row.wins as number) + 1;
        row.points = (row.points as number) + 3;
        if (match.finish === "connect") {
          row.connect_wins = (row.connect_wins as number) + 1;
          row.points = (row.points as number) + 2;
        }
        const last = match.plies[match.plies.length - 1];
        if (last.legal && last.line_count >= 3) {
          row.wire_bonus = (row.wire_bonus as number) + 1;
          row.points = (row.points as number) + 1;
        }
      } else {
        row.losses = (row.losses as number) + 1;
      }
      stats.set(player, row);
    }
    const rows = [...stats.values()].sort((a, b) => {
      const ap = a.points as number;
      const bp = b.points as number;
      if (bp !== ap) return bp - ap;
      const ac = a.connect_wins as number;
      const bc = b.connect_wins as number;
      if (bc !== ac) return bc - ac;
      const aw = a.wire_bonus as number;
      const bw = b.wire_bonus as number;
      if (bw !== aw) return bw - aw;
      return String(a.player).localeCompare(String(b.player));
    });
    let rank = 1;
    for (let i = 0; i < rows.length; i++) {
      if (
        i > 0 &&
        (rows[i - 1].points, rows[i - 1].connect_wins, rows[i - 1].wire_bonus) !==
          (rows[i].points, rows[i].connect_wins, rows[i].wire_bonus)
      ) {
        rank = i + 1;
      }
      rows[i].rank = rank;
    }
    const body = rows.map((r) => `${r.player}|${r.points}|${r.rank}`).join("\\n");
    const digest = crypto.createHash("sha256").update(body).digest("hex").slice(0, 16);
    fs.writeFileSync(outPath, JSON.stringify({ rows, digest }, null, 2) + "\\n");
  }
}
"""


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
        "fuse": {
            "pieces": {
                "a1": "B",
                "h8": "B",
                "b2": "W",
                "c2": "W",
                "d2": "W",
                "g7": "W",
            }
        },
        "pin": {
            "pieces": {
                "a1": "B",
                "b1": "B",
                "a8": "B",
                "b8": "B",
                "c4": "W",
                "d4": "W",
                "e4": "W",
                "f4": "W",
            }
        },
        "ridge": {
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
        W a2 d5
        B b1 a2
        W b2 f6
        B a1 e5
        W c2 a4
        B c1 b2

        match fuse_ring
        board fuse
        W g7 c3

        match pin_line
        board pin
        W c4 d3
        """
    )
    league_txt = textwrap.dedent(
        """\
        player Anya canal_link W
        player Ben canal_link B
        player Cara fuse_ring W
        player Dex fuse_ring B
        player Elio pin_line W
        player Fay pin_line B
        """
    )

    for name, body in boards.items():
        write(ENV / "data" / "boards" / f"{name}.json", json.dumps(body, indent=2) + "\n")
    write(ENV / "data" / "manifests" / "matches.txt", matches_txt)
    write(ENV / "data" / "manifests" / "league.txt", league_txt)

    trace = replay_manifest(matches_txt)
    standings = expected_standings(trace, league_txt)

    # remaining file generation continues in part 2 via direct writes
    print("trace winners:", [(m["match_id"], m["winner"], m["finish"]) for m in trace["matches"]])
    print("standings sample:", standings["rows"][:3], standings["digest"])


if __name__ == "__main__":
    main()
