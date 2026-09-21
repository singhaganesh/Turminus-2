#!/usr/bin/env python3
"""Generate tasks/loa-wire-cluster-pod end-to-end."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "tasks" / "loa-wire-cluster-pod"
ENV = TASK / "environment"
GEN_PATH = ROOT / "scripts" / "gen_loa_wire_cluster_pod.py"

NODE_DIGEST = (
    "public.ecr.aws/docker/library/node:22-bookworm-slim"
    "@sha256:f3a68cf41a855d227d1b0ab832bed9749469ef38cf4f58182fb8c893bc462383"
)


def load_gen():
    spec = importlib.util.spec_from_file_location("gen_loa", GEN_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def run_patch(old: str, new: str, rel: str) -> str:
    tmp = ENV / ".patch_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    old_path = tmp / "old.ts"
    new_path = tmp / "new.ts"
    old_path.write_text(old)
    new_path.write_text(new)
    proc = subprocess.run(
        ["diff", "-u", str(old_path), str(new_path)],
        capture_output=True,
        text=True,
    )
    lines = proc.stdout.splitlines()
    if not lines:
        return ""
    lines[0] = f"--- {rel}"
    lines[1] = f"+++ {rel}"
    return "\n".join(lines) + "\n"


def chmod_x(path: Path) -> None:
    path.chmod(path.stat().st_mode | 0o111)


def boards() -> dict[str, dict]:
    def sq(row: int, col: int) -> str:
        return f"{chr(ord('a') + col)}{row + 1}"

    return {
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
                "c3": "W",
                "d4": "W",
                "e5": "W",
                "g7": "B",
            }
        },
        "split": {
            "pieces": {
                "a1": "B",
                "h8": "W",
                "d4": "W",
                "e4": "B",
                "c6": "W",
                "f3": "B",
            }
        },
        "narrow": {
            "pieces": {
                "a4": "W",
                "h4": "B",
                "d2": "W",
                "d7": "B",
                "b5": "W",
                "g5": "B",
            }
        },
    }


MATCHES_TXT = textwrap.dedent(
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

LEAGUE_TXT = textwrap.dedent(
    """\
    player Anya canal_link W
    player Ben canal_link B
    player Cara fuse_ring W
    player Dex fuse_ring B
    player Elio pin_line W
    player Fay pin_line B
    """
)


def ts_sources() -> dict[str, str]:
    """Return broken-baseline TypeScript sources keyed by path under environment/."""
    return {
        "core/Coord.ts": """\
import { BoardGrid } from "./BoardGrid";

export type Square = { row: number; col: number };

export class Coord {
  static parse(label: string): Square {
    return { row: parseInt(label.slice(1), 10) - 1, col: label.charCodeAt(0) - "a".charCodeAt(0) };
  }

  static label(row: number, col: number): string {
    if (row < 0 || row > 7 || col < 0 || col > 7) {
      return ".";
    }
    return `${String.fromCharCode("a".charCodeAt(0) + col)}${row + 1}`;
  }

  static onBoard(label: string): boolean {
    const { row, col } = Coord.parse(label);
    return row >= 0 && row < 8 && col >= 0 && col < 8;
  }
}
""",
        "core/Side.ts": """\
export type SideMark = "W" | "B";

export class Side {
  static foe(side: string): SideMark {
    return side === "W" ? "B" : "W";
  }
}
""",
        "core/BoardGrid.ts": """\
import fs from "node:fs";
import path from "node:path";
import { Coord } from "./Coord";

const BOARD_ROOT = "/app/loa/data/boards";

function sign(n: number): number {
  return n > 0 ? 1 : n < 0 ? -1 : 0;
}

export function queenDir(from: string, to: string): [number, number] | null {
  const start = Coord.parse(from);
  const end = Coord.parse(to);
  const dr = sign(end.row - start.row);
  const dc = sign(end.col - start.col);
  if (dr === 0 && dc === 0) {
    return null;
  }
  if (dr !== 0 && dc !== 0 && Math.abs(end.row - start.row) !== Math.abs(end.col - start.col)) {
    return null;
  }
  if (dr === 0 && start.row !== end.row) {
    return [0, sign(end.col - start.col)];
  }
  if (dc === 0 && start.col !== end.col) {
    return [sign(end.row - start.row), 0];
  }
  if (dr !== 0 && dc !== 0) {
    return [dr, dc];
  }
  return null;
}

export function hopCount(from: string, to: string): number {
  const start = Coord.parse(from);
  const end = Coord.parse(to);
  return Math.max(Math.abs(end.row - start.row), Math.abs(end.col - start.col));
}

export function pathClear(board: BoardGrid, from: string, to: string): boolean {
  const start = Coord.parse(from);
  const end = Coord.parse(to);
  const dr = sign(end.row - start.row);
  const dc = sign(end.col - start.col);
  let row = start.row + dr;
  let col = start.col + dc;
  while (row !== end.row || col !== end.col) {
    if (board.at(Coord.label(row, col)) !== ".") {
      return false;
    }
    row += dr;
    col += dc;
  }
  return true;
}

export class BoardGrid {
  private pieces: Map<string, string>;

  constructor(pieces: Map<string, string>) {
    this.pieces = pieces;
  }

  static load(name: string): BoardGrid {
    const file = path.join(BOARD_ROOT, `${name}.json`);
    const payload = JSON.parse(fs.readFileSync(file, "utf8")) as { pieces: Record<string, string> };
    return new BoardGrid(new Map(Object.entries(payload.pieces)));
  }

  at(label: string): string {
    if (!Coord.onBoard(label)) {
      return ".";
    }
    return this.pieces.get(label) ?? ".";
  }

  entries(): Iterable<[string, string]> {
    return this.pieces.entries();
  }

  values(): Iterable<string> {
    return this.pieces.values();
  }

  clone(): BoardGrid {
    return new BoardGrid(new Map(this.pieces));
  }

  set(label: string, mark: string): void {
    this.pieces.set(label, mark);
  }
}
""",
        "search/LineScan.ts": """\
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
""",
        "search/ClusterProbe.ts": """\
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
    for (const piece of board.values()) {
      if (piece === side) count += 1;
    }
    if (count === 0) return false;
    return ClusterProbe.components(board, side) === 1;
  }
}
""",
        "search/ReachTally.ts": """\
import { BoardGrid } from "../core/BoardGrid";
import { ClusterProbe } from "./ClusterProbe";

export class ReachTally {
  static snapshot(board: BoardGrid): Record<string, number> {
    return {
      components_w: ClusterProbe.components(board, "W"),
      components_b: ClusterProbe.components(board, "B"),
    };
  }
}
""",
        "replay/WireMove.ts": """\
import { BoardGrid, hopCount, pathClear, queenDir } from "../core/BoardGrid";
import { Coord } from "../core/Coord";
import { Side } from "../core/Side";
import { ClusterProbe } from "../search/ClusterProbe";
import { LineScan } from "../search/LineScan";

const DELTAS = [
  [-1, -1], [-1, 0], [-1, 1],
  [0, -1], [0, 1],
  [1, -1], [1, 0], [1, 1],
];

export class WireMove {
  static legal(board: BoardGrid, side: string, from: string, to: string): boolean {
    if (board.at(from) !== side || board.at(to) === side) {
      return false;
    }
    const dir = queenDir(from, to);
    if (!dir) {
      return false;
    }
    const dist = hopCount(from, to);
    if (dist < 1 || !pathClear(board, from, to)) {
      return false;
    }
    return LineScan.count(board, from, dir[0], dir[1], side) === dist;
  }

  static apply(board: BoardGrid, side: string, from: string, to: string): BoardGrid {
    const next = board.clone();
    next.set(to, side);
    next.set(from, ".");
    return next;
  }

  static legalMoves(board: BoardGrid, side: string): Array<[string, string]> {
    const moves: Array<[string, string]> = [];
    for (const [from, piece] of board.entries()) {
      if (piece !== side) continue;
      const origin = Coord.parse(from);
      for (const [dr, dc] of DELTAS) {
        let row = origin.row + dr;
        let col = origin.col + dc;
        while (row >= 0 && row < 8 && col >= 0 && col < 8) {
          const to = Coord.label(row, col);
          if (WireMove.legal(board, side, from, to)) {
            moves.push([from, to]);
          }
          row += dr;
          col += dc;
        }
      }
    }
    return moves;
  }

  static finish(board: BoardGrid, mover: string): [string, string] | null {
    const foe = Side.foe(mover);
    if (ClusterProbe.connected(board, mover)) {
      return [mover, "connect"];
    }
    if (WireMove.legalMoves(board, foe).length === 0) {
      if (WireMove.legalMoves(board, mover).length === 0) {
        return ["draw", "immobile"];
      }
      return [mover, "immobile"];
    }
    return null;
  }
}
""",
        "replay/ScriptRunner.ts": """\
import fs from "node:fs";
import { BoardGrid } from "../core/BoardGrid";
import { hopCount, queenDir } from "../core/BoardGrid";
import { ClusterProbe } from "../search/ClusterProbe";
import { LineScan } from "../search/LineScan";
import { WireMove } from "./WireMove";

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
      let winner = "draw";
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
""",
        "replay/ManifestNote.ts": """\
export class ManifestNote {
  static describe(matchId: string): string {
    return `manifest block ${matchId}`;
  }
}
""",
        "pod/PodFold.ts": """\
import fs from "node:fs";

type Trace = {
  matches: Array<{
    match_id: string;
    winner: string;
    finish: string;
    plies: Array<{ legal: boolean; line_count: number }>;
  }>;
};

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
""",
        "pod/LeagueReader.ts": """\
import fs from "node:fs";

export class LeagueReader {
  static rows(text: string): string[] {
    return text.split("\\n").filter((line) => line.startsWith("player "));
  }
}
""",
        "shared/JsonOut.ts": """\
import fs from "node:fs";

export function writeJson(path: string, payload: unknown): void {
  fs.writeFileSync(path, JSON.stringify(payload, null, 2) + "\\n");
}
""",
        "shared/Paths.ts": """\
export const LOA_ROOT = "/app/loa";
export const BOARD_DIR = `${LOA_ROOT}/data/boards`;
export const MANIFEST_DIR = `${LOA_ROOT}/manifests`;
""",
        "shared/Version.ts": """\
export const DESK_VERSION = "0.9.4";
""",
        "shared/Main.ts": """\
import { PodFold } from "../pod/PodFold";
import { ScriptRunner } from "../replay/ScriptRunner";

function usage(): never {
  process.stderr.write(
    "usage: loa replay <manifest> <out> | loa pod <league> <trace> <out>\\n",
  );
  process.exit(1);
}

const [cmd, ...rest] = process.argv.slice(2);
if (cmd === "replay") {
  if (rest.length !== 2) usage();
  new ScriptRunner().run(rest[0], rest[1]);
} else if (cmd === "pod") {
  if (rest.length !== 3) usage();
  new PodFold().run(rest[0], rest[1], rest[2]);
} else {
  usage();
}
""",
    }


def fixed_sources(broken: dict[str, str]) -> dict[str, str]:
    fixed = dict(broken)
    fixed["search/LineScan.ts"] = broken["search/LineScan.ts"].replace(
        "        if (piece !== side) continue;\n", ""
    )
    fixed["search/ClusterProbe.ts"] = (
        broken["search/ClusterProbe.ts"]
        .replace(
            "const ORTHO = [[-1, 0], [1, 0], [0, -1], [0, 1]];",
            "const NEIGH = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];",
        )
        .replace("ORTHO", "NEIGH")
    )
    fixed["pod/PodFold.ts"] = """\
import fs from "node:fs";
import crypto from "node:crypto";

type Trace = {
  matches: Array<{
    match_id: string;
    winner: string;
    finish: string;
    plies: Array<{ legal: boolean; line_count: number }>;
  }>;
};

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
    return fixed


def rules_md() -> str:
    return textwrap.dedent(
        """\
        # Lines of Action desk rules

        Coordinates use columns `a` through `h` and rows `1` through `8`. The bundled boards live under `/app/loa/data/boards`.

        ## Movement

        A move slides one friendly piece along a straight queen line (horizontal, vertical, or diagonal) to an empty square or a square occupied by an opponent. The distance in squares must equal the number of pieces of either color lying on that entire queen line through the origin square (including the moving piece). The path between origin and destination must be empty.

        ## Cluster counts

        After each ply, report how many connected groups each side occupies using eight-way adjacency on the grid (diagonal neighbors count as adjacent).

        ## Match manifest

        `/app/loa/manifests/matches.txt` lists blocks:

        ```
        match <id>
        board <name>
        <side> <from> <to>
        ```

        `<side>` is `W` or `B`. When `board` is omitted the `classic` board is used. Blocks are separated by blank lines.

        ## Replay command

        ```
        /app/bin/loa replay /app/loa/manifests/matches.txt /app/output/replay_trace.json
        ```

        Rebuild TypeScript with `bash /app/environment/assemble.sh`, then rerun replay. Static JSON is insufficient.

        ### `replay_trace.json`

        Top-level object with `matches` array. Each match has `match_id`, `plies`, `winner` (`W`, `B`, or `draw`), and `finish` (`connect`, `immobile`, or `illegal`).

        Each ply object fields:

        | field | type | meaning |
        |-------|------|---------|
        | `ply` | int | 1-based index |
        | `side` | string | `W` or `B` |
        | `from` | string | start coordinate |
        | `to` | string | end coordinate |
        | `legal` | bool | manifest ply legality |
        | `line_count` | int | pieces counted on the queen line before the move |
        | `hops` | int | square distance moved |
        | `captured` | bool | destination held an opponent |
        | `components_w` | int | white connected groups after ply |
        | `components_b` | int | black connected groups after ply |
        | `connected_w` | bool | white occupies one eight-way group |
        | `connected_b` | bool | black occupies one eight-way group |

        When a ply is illegal, still emit the ply row with `legal` false, leave cluster fields at the pre-move board, and stop further plies for that match. Set `finish` to `illegal` and `winner` to the side that did not commit the illegal ply.

        After a legal ply, if the mover's pieces form one eight-way connected group, the mover wins with `finish` `connect`. If the opponent has no legal move and the mover also has none, the match is a `draw` with `finish` `immobile`. If only the opponent is immobile, the mover wins with `finish` `immobile`.

        ## Pod command

        ```
        /app/bin/loa pod /app/loa/manifests/league.txt /app/output/replay_trace.json /app/output/standings.json
        ```

        Reads the league manifest and the replay trace produced by the replay command.

        ### League manifest

        `/app/loa/manifests/league.txt` rows:

        ```
        player <name> <match_id> <side>
        ```

        `<side>` is the color the player played in that match (`W` or `B`).

        ### Scoring

        Per enrolled match row:

        - Win: 3 points when the player color equals `winner`.
        - Loss: 0 points.
        - Draw: 1 point each.
        - Connect bonus: add 2 when the player won and `finish` is `connect`.
        - Wire bonus: add 1 when the player won and the final legal ply has `line_count` at least 3.

        Aggregate per player: `wins`, `losses`, `draws`, `connect_wins`, `wire_bonus`, `points`.

        ### Standings order

        Sort players by descending `points`, then descending `connect_wins`, then descending `wire_bonus`, then ascending player name. Assign `rank` starting at 1; players with equal `points`, `connect_wins`, and `wire_bonus` share a rank and the next rank skips (1,1,3). Player name affects sort order only, not shared rank assignment.

        ### `standings.json`

        ```json
        {
          "rows": [
            {
              "player": "name",
              "wins": 0,
              "losses": 0,
              "draws": 0,
              "connect_wins": 0,
              "wire_bonus": 0,
              "points": 0,
              "rank": 1
            }
          ],
          "digest": "hex"
        }
        ```

        `digest` is the first 16 lowercase hex chars of sha256 (SHA-256) over UTF-8 `player|points|rank` lines joined by `\\n` in final sort order.
        """
    )


def reference_engine_py() -> str:
    return textwrap.dedent(
        '''\
        DIRS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]


        def _sign(n):
            return (n > 0) - (n < 0)


        def _parse(coord):
            return int(coord[1]) - 1, ord(coord[0]) - ord("a")


        def _sq(row, col):
            return f"{chr(ord('a') + col)}{row + 1}"


        def _load_board(name):
            data = json.loads((DATA / "boards" / f"{name}.json").read_text())
            return dict(data["pieces"])


        def _queen_dir(fr, to):
            sr, sc = _parse(fr)
            er, ec = _parse(to)
            dr = _sign(er - sr)
            dc = _sign(ec - sc)
            if dr == 0 and dc == 0:
                return None
            if dr != 0 and dc != 0 and abs(er - sr) != abs(ec - sc):
                return None
            if dr == 0 and sr != er:
                return 0, _sign(ec - sc)
            if dc == 0 and sc != ec:
                return _sign(er - sr), 0
            if dr != 0 and dc != 0:
                return dr, dc
            return None


        def _line_count(board, fr, direction):
            sr, sc = _parse(fr)
            dr, dc = direction
            count = 0
            for r in range(8):
                for c in range(8):
                    coord = _sq(r, c)
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


        def _hops(fr, to):
            sr, sc = _parse(fr)
            er, ec = _parse(to)
            return max(abs(er - sr), abs(ec - sc))


        def _path_clear(board, fr, to):
            sr, sc = _parse(fr)
            er, ec = _parse(to)
            dr = _sign(er - sr)
            dc = _sign(ec - sc)
            r, c = sr + dr, sc + dc
            while (r, c) != (er, ec):
                if board.get(_sq(r, c), ".") != ".":
                    return False
                r += dr
                c += dc
            return True


        def _legal(board, side, fr, to):
            if board.get(fr) != side or board.get(to, ".") == side:
                return False
            direction = _queen_dir(fr, to)
            if direction is None:
                return False
            dist = _hops(fr, to)
            if dist < 1 or not _path_clear(board, fr, to):
                return False
            return _line_count(board, fr, direction) == dist


        def _apply(board, side, fr, to):
            nxt = dict(board)
            nxt[to] = side
            nxt[fr] = "."
            return nxt


        def _neighbors(row, col):
            out = []
            for dr, dc in DIRS:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    out.append((r, c))
            return out


        def _components(board, side):
            seen = set()
            count = 0
            for coord, piece in board.items():
                if piece != side or coord in seen:
                    continue
                count += 1
                stack = [coord]
                seen.add(coord)
                while stack:
                    cur = stack.pop()
                    r, c = _parse(cur)
                    for nr, nc in _neighbors(r, c):
                        nxt = _sq(nr, nc)
                        if board.get(nxt) == side and nxt not in seen:
                            seen.add(nxt)
                            stack.append(nxt)
            return count


        def _connected(board, side):
            pieces = [c for c, p in board.items() if p == side]
            if not pieces:
                return False
            return _components(board, side) == 1


        def _legal_moves(board, side):
            moves = []
            for fr, piece in board.items():
                if piece != side:
                    continue
                sr, sc = _parse(fr)
                for dr, dc in DIRS:
                    r, c = sr + dr, sc + dc
                    while 0 <= r < 8 and 0 <= c < 8:
                        to = _sq(r, c)
                        if _legal(board, side, fr, to):
                            moves.append((fr, to))
                        r += dr
                        c += dc
            return moves


        def _finish(board, mover):
            foe = "B" if mover == "W" else "W"
            if _connected(board, mover):
                return mover, "connect"
            if not _legal_moves(board, foe):
                if not _legal_moves(board, mover):
                    return "draw", "immobile"
                return mover, "immobile"
            return None, None


        def replay_manifest(text):
            matches = []
            for block in [chunk.strip() for chunk in text.strip().split("\\n\\n") if chunk.strip()]:
                rows = block.splitlines()
                match_id = rows[0].split()[1]
                board_name = "classic"
                start = 1
                if rows[1].startswith("board "):
                    board_name = rows[1].split()[1]
                    start = 2
                state = _load_board(board_name)
                plies = []
                winner = "draw"
                finish_reason = "immobile"
                stopped = False
                for index, line in enumerate(rows[start:], 1):
                    side, fr, to = line.split()
                    direction = _queen_dir(fr, to)
                    ok = _legal(state, side, fr, to)
                    lc = _line_count(state, fr, direction) if direction else 0
                    dist = _hops(fr, to) if direction else 0
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
                                "components_w": _components(state, "W"),
                                "components_b": _components(state, "B"),
                                "connected_w": _connected(state, "W"),
                                "connected_b": _connected(state, "B"),
                            }
                        )
                        winner = "B" if side == "W" else "W"
                        finish_reason = "illegal"
                        stopped = True
                        break
                    state = _apply(state, side, fr, to)
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
                            "components_w": _components(state, "W"),
                            "components_b": _components(state, "B"),
                            "connected_w": _connected(state, "W"),
                            "connected_b": _connected(state, "B"),
                        }
                    )
                    win, fin = _finish(state, side)
                    if win:
                        winner = win
                        finish_reason = fin
                        stopped = True
                        break
                if not stopped and plies:
                    win, fin = _finish(state, plies[-1]["side"])
                    if win:
                        winner = win
                        finish_reason = fin
                matches.append(
                    {"match_id": match_id, "plies": plies, "winner": winner, "finish": finish_reason}
                )
            return {"matches": matches}


        def expected_standings(trace, league_text):
            meta = {m["match_id"]: m for m in trace["matches"]}
            stats = {}
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
                key=lambda item: (
                    -item["points"],
                    -item["connect_wins"],
                    -item["wire_bonus"],
                    item["player"],
                ),
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
            body = "\\n".join(f"{row['player']}|{row['points']}|{row['rank']}" for row in rows)
            digest = hashlib.sha256(body.encode()).hexdigest()[:16]
            return {"rows": rows, "digest": digest}
        '''
    )


def test_m1_py() -> str:
    engine = reference_engine_py()
    return textwrap.dedent(
        f"""\
        import hashlib
        import json
        import subprocess
        from pathlib import Path

        APP = Path("/app")
        DATA = APP / "loa" / "data"
        MANIFEST = APP / "loa" / "manifests" / "matches.txt"
        OUT = APP / "output" / "replay_trace.json"

        {engine}

        def _rebuild_desk():
            subprocess.run(["bash", "/app/environment/assemble.sh"], check=True)


        def _run_replay(manifest_path, output_path):
            subprocess.run(
                [
                    "/app/bin/loa",
                    "replay",
                    str(manifest_path),
                    str(output_path),
                ],
                check=True,
            )


        class TestMilestone1:
            def test_replay_regenerates_trace(self):
                \"\"\"Replay command must write replay_trace.json with all manifest matches.\"\"\"

                if OUT.exists():
                    OUT.unlink()
                _run_replay(MANIFEST, OUT)
                payload = json.loads(OUT.read_text())
                assert "matches" in payload
                assert len(payload["matches"]) == 3

            def test_canal_link_draw_immobile(self):
                \"\"\"Canal link match must end in draw with immobile finish after six plies.\"\"\"

                if OUT.exists():
                    OUT.unlink()
                _run_replay(MANIFEST, OUT)
                payload = json.loads(OUT.read_text())
                canal = next(match for match in payload["matches"] if match["match_id"] == "canal_link")
                assert canal["winner"] == "draw"
                assert canal["finish"] == "immobile"
                assert len(canal["plies"]) == 6

            def test_fuse_ring_connect_win(self):
                \"\"\"Fuse ring match must end with white connect win on the documented ply.\"\"\"

                if OUT.exists():
                    OUT.unlink()
                _run_replay(MANIFEST, OUT)
                payload = json.loads(OUT.read_text())
                fuse = next(match for match in payload["matches"] if match["match_id"] == "fuse_ring")
                assert fuse["winner"] == "W"
                assert fuse["finish"] == "connect"
                assert fuse["plies"][-1]["connected_w"] is True
                assert fuse["plies"][-1]["line_count"] >= 3

            def test_pin_line_connect(self):
                \"\"\"Pin line match must finish with white connect on one ply.\"\"\"

                if OUT.exists():
                    OUT.unlink()
                _run_replay(MANIFEST, OUT)
                payload = json.loads(OUT.read_text())
                pin = next(match for match in payload["matches"] if match["match_id"] == "pin_line")
                assert pin["winner"] == "W"
                assert pin["finish"] == "connect"

            def test_trace_matches_reference_engine(self):
                \"\"\"Full trace must match an independent rules engine over the manifest.\"\"\"

                if OUT.exists():
                    OUT.unlink()
                _run_replay(MANIFEST, OUT)
                payload = json.loads(OUT.read_text())
                expected = replay_manifest(MANIFEST.read_text())
                assert payload == expected

            def test_ridge_board_probe(self):
                \"\"\"Eight-way cluster probe on ridge board must count one white group initially.\"\"\"

                extra = MANIFEST.read_text() + "\\n\\nmatch ridge_probe\\nboard ridge\\n"
                probe_manifest = APP / "output" / "probe_matches.txt"
                probe_out = APP / "output" / "probe_trace.json"
                probe_manifest.write_text(extra)
                if probe_out.exists():
                    probe_out.unlink()
                _run_replay(probe_manifest, probe_out)
                payload = json.loads(probe_out.read_text())
                match = next(item for item in payload["matches"] if item["match_id"] == "ridge_probe")
                assert match["plies"] == []
                assert match["winner"] == "draw"
                board = _load_board("ridge")
                assert _components(board, "W") == 1
        """
    )


def test_m2_py(digest: str) -> str:
    engine = reference_engine_py()
    return textwrap.dedent(
        f"""\
        import hashlib
        import json
        import subprocess
        from pathlib import Path

        APP = Path("/app")
        DATA = APP / "loa" / "data"
        LEAGUE = APP / "loa" / "manifests" / "league.txt"
        TRACE = APP / "output" / "replay_trace.json"
        OUT = APP / "output" / "standings.json"
        MATCHES = APP / "loa" / "manifests" / "matches.txt"

        {engine}

        def _ensure_trace():
            if not TRACE.exists():
                subprocess.run(
                    [
                        "/app/bin/loa",
                        "replay",
                        str(MATCHES),
                        str(TRACE),
                    ],
                    check=True,
                )


        class TestMilestone2:
            def test_pod_regenerates_standings(self):
                \"\"\"Pod command must write standings.json with rows and digest.\"\"\"

                _ensure_trace()
                if OUT.exists():
                    OUT.unlink()
                subprocess.run(
                    [
                        "/app/bin/loa",
                        "pod",
                        str(LEAGUE),
                        str(TRACE),
                        str(OUT),
                    ],
                    check=True,
                )
                payload = json.loads(OUT.read_text())
                assert "rows" in payload
                assert "digest" in payload
                assert len(payload["rows"]) == 6

            def test_points_and_ranks(self):
                \"\"\"Standings points and ranks must follow league scoring and tie order.\"\"\"

                _ensure_trace()
                if OUT.exists():
                    OUT.unlink()
                subprocess.run(
                    [
                        "/app/bin/loa",
                        "pod",
                        str(LEAGUE),
                        str(TRACE),
                        str(OUT),
                    ],
                    check=True,
                )
                payload = json.loads(OUT.read_text())
                by_name = {{row["player"]: row for row in payload["rows"]}}
                assert by_name["Cara"]["points"] == 6
                assert by_name["Cara"]["rank"] == 1
                assert by_name["Elio"]["points"] == 5
                assert by_name["Elio"]["rank"] == 2
                assert by_name["Anya"]["points"] == 1
                assert by_name["Anya"]["rank"] == 3
                assert by_name["Ben"]["rank"] == 3
                assert by_name["Dex"]["points"] == 0
                assert by_name["Dex"]["rank"] == 5

            def test_digest_matches_fold(self):
                \"\"\"Digest must match the documented SHA-256 fold over player rows.\"\"\"

                _ensure_trace()
                if OUT.exists():
                    OUT.unlink()
                subprocess.run(
                    [
                        "/app/bin/loa",
                        "pod",
                        str(LEAGUE),
                        str(TRACE),
                        str(OUT),
                    ],
                    check=True,
                )
                payload = json.loads(OUT.read_text())
                trace = json.loads(TRACE.read_text())
                expected = expected_standings(trace, LEAGUE.read_text())
                assert payload["digest"] == expected["digest"]
                assert payload["digest"] == "{digest}"

            def test_standings_rows_match_reference(self):
                \"\"\"Each standings row must match independent scoring from the trace.\"\"\"

                _ensure_trace()
                if OUT.exists():
                    OUT.unlink()
                subprocess.run(
                    [
                        "/app/bin/loa",
                        "pod",
                        str(LEAGUE),
                        str(TRACE),
                        str(OUT),
                    ],
                    check=True,
                )
                payload = json.loads(OUT.read_text())
                trace = json.loads(TRACE.read_text())
                expected = expected_standings(trace, LEAGUE.read_text())
                assert payload["rows"] == expected["rows"]

            def test_pod_depends_on_trace(self):
                \"\"\"Standings must change when replay trace winners change.\"\"\"

                _ensure_trace()
                original = TRACE.read_text()
                start = original.index('"match_id": "fuse_ring"')
                winner_at = start + original[start:].index('"winner": "') + len('"winner": "')
                mutated = original[:winner_at] + "B" + original[winner_at + 1 :]
                TRACE.write_text(mutated)
                if OUT.exists():
                    OUT.unlink()
                subprocess.run(
                    [
                        "/app/bin/loa",
                        "pod",
                        str(LEAGUE),
                        str(TRACE),
                        str(OUT),
                    ],
                    check=True,
                )
                payload = json.loads(OUT.read_text())
                by_name = {{row["player"]: row for row in payload["rows"]}}
                assert by_name["Cara"]["points"] == 0
                assert by_name["Dex"]["points"] == 3
                TRACE.write_text(original)
        """
    )


def spec_md(digest: str) -> str:
    return textwrap.dedent(
        f"""\
        ### Decision
        GO — Attempt 1. Two-milestone Lines of Action repair desk with TypeScript replay trace and pod standings fold.

        ### Metadata
        - version: 2
        - Task name: loa-wire-cluster-pod
        - Title: LoA Wire Cluster Pod
        - Category: games
        - Task shape: repair_existing_system
        - Languages: ["typescript", "bash"]
        - Difficulty: hard
        - Codebase size: small
        - Subcategories: ["tool_specific"]
        - Tags: ["lines-of-action", "queen-line", "cluster-count", "replay-trace", "pod-standings"]
        - Milestones: 2

        ## Authoring Brief

        ### Public contract
        Fix `/app/environment` TypeScript so `/app/bin/loa replay` writes `/app/output/replay_trace.json` from `/app/loa/manifests/matches.txt` and `/app/bin/loa pod` writes `/app/output/standings.json` from `/app/loa/manifests/league.txt` plus the trace. Rules, schemas, scoring, and CLI forms live in `/app/loa/docs/rules.md`. Rebuild with `bash /app/environment/assemble.sh` before rerunning commands.

        ### platform_files
        - path: task.toml
          role: metadata; `[environment] allow_internet = false`
        - path: steps/milestone_1/instruction.md
          role: milestone 1 prompt
        - path: steps/milestone_2/instruction.md
          role: milestone 2 prompt
        - path: output_contract.toml
          role: local output declaration
        - path: steps/milestone_1/tests/test.sh
          role: milestone 1 verifier entrypoint
        - path: steps/milestone_1/tests/test_m1.py
          role: milestone 1 domain verifier
        - path: steps/milestone_2/tests/test.sh
          role: milestone 2 verifier entrypoint
        - path: steps/milestone_2/tests/test_m2.py
          role: milestone 2 domain verifier
        - path: steps/milestone_1/solution/solve.sh
          role: milestone 1 oracle wrapper
        - path: steps/milestone_2/solution/solve.sh
          role: milestone 2 oracle wrapper
        - path: environment/Dockerfile
          role: digest-pinned node build with verifier deps
        - path: construction_manifest.json
          role: local authoring artifact

        ### task_files
        - path: environment/search/LineScan.ts
          role: queen-line piece counter on fix frontier
        - path: environment/search/ClusterProbe.ts
          role: side cluster counter on fix frontier
        - path: environment/pod/PodFold.ts
          role: league standings fold on fix frontier
        - path: environment/docs/rules.md
          role: public LoA contract and CLI reference

        ### fix_frontier
        - count: 3
        - distribution: search/replay cluster in milestone 1; pod fold in milestone 2
        - naming_policy: neutral module names; no instruction nouns on fix-path symbols
        - forbidden_stems: [wire, cluster, pod, replay, standings, connect, line_count]
        - helpers_policy: decoy readers and tally helpers may mirror shape but stay off oracle frontier
        - symbol_thin_preferred: true

        ### contract_surface
        - boolean_fields_max: 4
        - direct_boolean_assertions_max: 6
        - preferred_assertion_styles: [trace rows, cluster counts, points, ranks, digest]
        - forbidden_assertion_styles: [boolean answer keys, scenario expected tables]

        ### task_shape
        - type: repair_existing_system
        - instruction_framing: symptoms-only
        - hardness_source: diagnosis
        - collapse_risk: grep to LineScan or PodFold from symptom nouns

        ### category_profile
        - challenge_family: board_game_rule_engine
        - profile_name: file_format_serialization
        - allowed_instruction_disclosures: [CLI commands, output paths, observable trace fields, scoring rules]
        - forbidden_instruction_leaks: [exact broken functions, patch recipes, file-level fix map]
        - category_specific_hardness_bar: movement, cluster adjacency, and standings fold must interact
        - category_specific_verifier_risks: [golden trace leak, standings hardcode]
        - coverage_role: games category with multi-module TypeScript repair

        ### difficulty_mechanism_plan
        - mechanisms: [buried_local_constraints, cross_file_cross_format_invariants, deceptive_but_valid_local_evidence, environment_specific_cli_semantics, false_green_intermediate_states, partial_observability_experiment_design]
        - adversarial_layers_count: 4
        - fairness_guardrails: full rules in docs/rules.md; tests derive from independent Python engine
        - mechanism: buried_local_constraints
          placement: LineScan friendly-only filter
          why_model_misses_it: line distance looks correct on sparse lines
          fairness_guardrail: rules define all-pieces count explicitly
        - mechanism: cross_file_cross_format_invariants
          placement: replay trace consumed by pod fold
          why_model_misses_it: milestone 1 trace can look locally plausible
          fairness_guardrail: milestone 2 mutates trace winner in test
        - mechanism: deceptive_but_valid_local_evidence
          placement: four-neighbor ClusterProbe passes some boards
          why_model_misses_it: ortho groups match on separated corners
          fairness_guardrail: ridge board diagonal chain probe
        - mechanism: environment_specific_cli_semantics
          placement: assemble.sh rebuild requirement
          why_model_misses_it: agents edit TS without rebuilding
          fairness_guardrail: instruction names rebuild command

        ### calibration_plan
        - oracle_runs: 3
        - no_op_runs: 3
        - target_agent_runs: 5
        - comparator_agent_runs: 5
        - human_sanity: replay canal_link and confirm draw/immobile
        - shortcut_audit: [static JSON, manifest-specific hardcode, pod-only sort patch]
        - ablation_plan: revert LineScan only; revert ClusterProbe only; revert PodFold only
        - pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=[frontier agent accuracy]

        ### verifier_scoring_plan
        - metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
        - overall_threshold: 0.999
        - reward_output: reward.txt
        - binary_threshold_rule: all milestone tests pass

        ### subtype_milestone_plan
        - subcategories: [tool_specific]
        - milestone_count: 2
        - sequential_dependency: pod fold requires corrected replay trace on disk
        - local_only_data: true
        - sidecar_or_protocol_notes: none
        - long_context_token_floor: 0

        ### satisfiability_risk
        - rc2_planned_name_risk: low — neutral search/replay/pod module names
        - gx9_contract_risk: low — rules doc holds formulas; tests use engine
        - cr1_symbol_frontier_risk: low — three distinct directories
        - hidden_contract_risk: low — rules.md documents tested fields

        ### actionability_plan
        - verifier_command_visible: replay and pod CLI in instruction
        - source_fix_intent_visible: fix source under /app/environment
        - generated_output_rule_visible: output paths and rebuild rule
        - exact_formula_home: environment/docs/rules.md
        - schema_home: environment/docs/rules.md

        ### waiver_plan
        - waivers_expected: no
        - waiver_rationale: deterministic local CLI with full public rules

        ### reference_pattern
        - reference_task_id: fanorona-sweep-replay-cup
        - justification_if_none: n/a

        ### realism_source
        - source_type: synthetic_exception
        - evidence_basis: LoA movement and connectivity rules adapted to TB3 repair shape
        - upstream_or_synthetic_rationale: compact TypeScript desk mirroring real game adjudication workflows
        - minimization_preserves: queen-line distance, eight-way connectivity, league fold
        - synthetic_exception_review: public rules in docs; independent verifier engine

        ### Failure topology
        Replay traces show legal plies with wrong line counts or cluster fields while pod standings drift on bonuses, ranks, and digest. Movement, connectivity counting, and league aggregation interact but fail independently enough that local smoke on one match misleads.

        ### Environment shape
        TypeScript modules under `environment/` for board loading, queen-line scanning, cluster probing, replay scripting, and pod folding; JSON boards and text manifests under `environment/data/` copied to `/app/loa`; rules doc under `environment/docs/`; assemble script builds `/app/bin/loa`.

        ### Required artifacts
        Milestone layout with instructions, tests, oracle patches, Dockerfile, task metadata, output contract, construction manifest, spec, rubric, and submission notes. At least 20 environment source/data/doc files excluding Docker metadata.

        ### Test plan
        - test_replay_regenerates_trace: CLI writes three matches
        - test_canal_link_draw_immobile: six ply draw
        - test_fuse_ring_connect_win: connect finish with wire line count
        - test_pin_line_connect: single ply connect
        - test_trace_matches_reference_engine: full trace oracle
        - test_ridge_board_probe: eight-way cluster on ridge board
        - test_pod_regenerates_standings: standings shape
        - test_points_and_ranks: Cara 6 rank 1; shared draw ranks
        - test_digest_matches_fold: digest {digest}
        - test_standings_rows_match_reference: row equality
        - test_pod_depends_on_trace: winner mutation changes points

        ### Drafting guardrails
        Do not name LineScan, ClusterProbe, or PodFold in instructions. Keep symptom framing. Avoid manifest-specific constants in fix-path code.

        ### Triviality Ledger
        - Friendly-only line scan passes sparse boards but fails full trace comparison — blocked by reference engine test
        - Ortho cluster count matches ridge corners but fails diagonal chain — blocked by ridge probe
        - Alphabetical pod sort looks structured but fails digest — blocked by digest test

        ### Per-gate Pitfall Inventory
        - RC2: neutral directory names search/replay/pod — no task nouns in paths
        - GX9: scoring formulas live in rules.md not instruction recital
        - CR1: three oracle patches across distinct modules
        - GX6: symptoms describe wrong traces and standings, not file names

        ### Initial Draft Commitments
        - environment/Dockerfile
        - environment/assemble.sh
        - environment/package.json
        - environment/tsconfig.json
        - environment/.dockerignore
        - environment/docs/rules.md
        - environment/core/BoardGrid.ts
        - environment/core/Coord.ts
        - environment/core/Side.ts
        - environment/search/LineScan.ts
        - environment/search/ClusterProbe.ts
        - environment/search/ReachTally.ts
        - environment/replay/WireMove.ts
        - environment/replay/ScriptRunner.ts
        - environment/replay/ManifestNote.ts
        - environment/pod/PodFold.ts
        - environment/pod/LeagueReader.ts
        - environment/shared/Main.ts
        - environment/shared/JsonOut.ts
        - environment/shared/Paths.ts
        - environment/shared/Version.ts
        - environment/data/boards/classic.json
        - environment/data/boards/fuse.json
        - environment/data/boards/pin.json
        - environment/data/boards/ridge.json
        - environment/data/boards/split.json
        - environment/data/boards/narrow.json
        - environment/data/manifests/matches.txt
        - environment/data/manifests/league.txt
        - environment/schema/trace.schema.json
        - environment/schema/standings.schema.json
        - environment/notes/move_glossary.txt
        - steps/milestone_1/instruction.md
        - steps/milestone_2/instruction.md
        - steps/milestone_1/tests/test.sh
        - steps/milestone_1/tests/test_m1.py
        - steps/milestone_2/tests/test.sh
        - steps/milestone_2/tests/test_m2.py
        - steps/milestone_1/solution/solve.sh
        - steps/milestone_1/solution/solve1.sh
        - steps/milestone_1/solution/linescan.patch
        - steps/milestone_1/solution/clusterprobe.patch
        - steps/milestone_2/solution/solve.sh
        - steps/milestone_2/solution/solve2.sh
        - steps/milestone_2/solution/podfold.patch
        - task.toml
        - output_contract.toml
        - construction_manifest.json

        ### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

        #### symbol_table
        - path: environment/search/LineScan.ts
          symbol: LineScan.count
          kind: function
          signature: count(board, from, dr, dc, side)
          purpose: counts pieces on queen line through origin
        - path: environment/search/ClusterProbe.ts
          symbol: ClusterProbe.components
          kind: function
          signature: components(board, side)
          purpose: counts connected groups for a side
        - path: environment/pod/PodFold.ts
          symbol: PodFold.run
          kind: function
          signature: run(leaguePath, tracePath, outPath)
          purpose: folds league rows into standings JSON

        #### flipping_point_contract
        locations:
          - id: A
            path: environment/search/LineScan.ts
            controls_tests: [test_trace_matches_reference_engine, test_fuse_ring_connect_win]
          - id: B
            path: environment/search/ClusterProbe.ts
            controls_tests: [test_ridge_board_probe, test_canal_link_draw_immobile]
          - id: C
            path: environment/pod/PodFold.ts
            controls_tests: [test_points_and_ranks, test_pod_depends_on_trace]
        no_single_location_flips_majority: true
        concentration_cap: 0.5

        #### decoy_manifest
        - path: environment/pod/LeagueReader.ts
          kind: helper
          rhymes_with: PodFold.run
          non_fix_purpose: parses league rows without scoring
        - path: environment/search/ReachTally.ts
          kind: helper
          rhymes_with: ClusterProbe.components
          non_fix_purpose: snapshot wrapper for cluster counts

        #### code_forbidden_tokens
        code_forbidden_tokens: [wire, cluster, pod, replay, standings, connect, trace, league, queen, fold, digest, rank, points, line, board, manifest, ply, immobile, bonus]
        """
    )


def rubric_txt() -> str:
    return textwrap.dedent(
        """\
        # Rubric 1
        Agent repairs queen-line counting to include every piece on the line through the origin, +5
        Agent repairs eight-way cluster grouping for connected_w and components fields, +5
        Agent emits illegal ply rows with halted match finish without corrupting later blocks, +3
        Agent regenerates replay_trace.json from manifests instead of writing static JSON, +3
        Agent edits TypeScript under /app/environment and rebuilds with assemble.sh before replay, +2
        Agent breaks pod standings while fixing replay trace modules, -3
        Agent hardcodes match-specific winners or ply rows in source, -5
        Agent skips rebuilding after source edits and leaves stale compiled output, -2

        # Rubric 2
        Agent folds league enrollments into standings using the regenerated replay trace, +5
        Agent applies win, draw, connect bonus, and wire bonus scoring from the rules note, +5
        Agent assigns shared ranks on matching points, connect_wins, and wire_bonus with name as sort tie-break only, +3
        Agent writes the SHA-256 digest fold described in the rules note, +3
        Agent regenerates standings.json through the pod command instead of static output, +3
        Agent reruns replay when the trace is missing or stale before pod, +2
        Agent hardcodes player points or digest values in source, -5
        Agent edits only the pod sorter while leaving replay physics broken, -3
        Agent writes standings.json without reading line_count from the trace, -3
        """
    )


def submission_notes_txt() -> str:
    return textwrap.dedent(
        """\
        Difficulty Explanation

        This is a two step TypeScript repair on a small offline Lines of Action CLI. Step one looks like a replay export job but queen line distance counts every piece on the line while cluster fields use eight way adjacency on the grid. A friendly only line scan or four neighbor grouping makes some slates look fine until the full manifest is replayed. Step two folds league rows from that trace with win points, connect bonus, wire bonus, shared ranks and a digest fold. Hand written JSON or manifest name hacks fail as soon as a fresh slate is loaded.

        Solution Explanation

        I started by replaying one short match by hand against the rules note to see where line counts and cluster fields diverged. The replay fix needed all pieces counted on the queen line and eight way cluster probing after each ply. I rebuilt after each source edit and reran the replay command until the trace matched an independent engine. For step two I fixed the standings fold so connect and wire bonuses add to points, ranks tie on the documented keys, and sorting follows points then connect wins then wire bonus then name.

        Verification Explanation

        The checks invoke the loa CLI and compare outputs against an independent rules engine embedded in the verifier. Milestone one replays the bundled match list and also writes a fresh manifest block with the ridge board to block hardcoded answers. Milestone two checks points, ranks and the digest fold against reference scoring from the trace and mutates a winner field to prove the pod layer depends on replay output. That catches static JSON, driver only tweaks and line scan patches that still miss eight way grouping because the standings layer never saw an honest trace.
        """
    )


def build_environment_files(broken: dict[str, str]) -> None:
    for name, body in boards().items():
        write(ENV / "data" / "boards" / f"{name}.json", json.dumps(body, indent=2) + "\n")
    write(ENV / "data" / "manifests" / "matches.txt", MATCHES_TXT)
    write(ENV / "data" / "manifests" / "league.txt", LEAGUE_TXT)
    write(ENV / "docs" / "rules.md", rules_md())
    write(
        ENV / "notes" / "move_glossary.txt",
        "LoA moves slide along queen lines; distance equals pieces on the full line through the origin.\n",
    )
    write(
        ENV / "schema" / "trace.schema.json",
        json.dumps(
            {
                "type": "object",
                "properties": {
                    "matches": {
                        "type": "array",
                        "items": {"type": "object"},
                    }
                },
            },
            indent=2,
        )
        + "\n",
    )
    write(
        ENV / "schema" / "standings.schema.json",
        json.dumps(
            {
                "type": "object",
                "properties": {
                    "rows": {"type": "array"},
                    "digest": {"type": "string"},
                },
            },
            indent=2,
        )
        + "\n",
    )
    for rel, content in broken.items():
        write(ENV / rel, content)
    write(
        ENV / "package.json",
        json.dumps(
            {
                "name": "loa-wire-cluster-pod",
                "version": "1.0.0",
                "private": True,
                "scripts": {"build": "tsc"},
                "devDependencies": {"typescript": "5.7.3", "@types/node": "22.10.7"},
            },
            indent=2,
        )
        + "\n",
    )
    write(
        ENV / "tsconfig.json",
        json.dumps(
            {
                "compilerOptions": {
                    "target": "ES2022",
                    "module": "commonjs",
                    "rootDir": ".",
                    "outDir": "dist",
                    "strict": True,
                    "esModuleInterop": True,
                    "skipLibCheck": True,
                },
                "include": ["**/*.ts"],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        ENV / ".dockerignore",
        "node_modules/\ndist/\n.git/\n**/__pycache__/\n.env\nsolution/\ntests/\n",
    )
    write(
        ENV / "assemble.sh",
        textwrap.dedent(
            """\
            #!/bin/bash
            set -euo pipefail

            ROOT="/app/environment"
            OUT="/app/bin"

            cd "$ROOT"
            npm install --no-audit --no-fund
            npm run build
            mkdir -p "$OUT"
            cat > "$OUT/loa" <<'SCRIPT'
            #!/bin/bash
            set -euo pipefail
            exec node /app/environment/dist/shared/Main.js "$@"
            SCRIPT
            chmod +x "$OUT/loa"
            """
        ),
    )
    chmod_x(ENV / "assemble.sh")
    write(
        ENV / "Dockerfile",
        textwrap.dedent(
            f"""\
            FROM {NODE_DIGEST}

            WORKDIR /app

            RUN apt-get update && apt-get install -y --no-install-recommends \\
                asciinema=2.2.0-1 \\
                ca-certificates=20230311+deb12u1 \\
                patch=2.7.6-5 \\
                python3=3.11.2-1+b1 \\
                python3-pip=23.0.1+dfsg-1 \\
                python3-venv=3.11.2-1+b1 \\
                tmux=3.3a-3 \\
                && rm -rf /var/lib/apt/lists/* \\
                && python3 -m venv /opt/verifier-venv \\
                && /opt/verifier-venv/bin/pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5

            ENV PATH="/opt/verifier-venv/bin:${{PATH}}"

            COPY assemble.sh package.json tsconfig.json /app/environment/
            COPY core /app/environment/core
            COPY search /app/environment/search
            COPY replay /app/environment/replay
            COPY pod /app/environment/pod
            COPY shared /app/environment/shared
            COPY docs /app/loa/docs
            COPY schema /app/loa/schema
            COPY notes /app/loa/notes
            COPY data /app/loa/data
            COPY data/manifests /app/loa/manifests

            RUN chmod +x /app/environment/assemble.sh \\
                && /app/environment/assemble.sh \\
                && mkdir -p /app/output

            WORKDIR /app
            CMD ["bash"]
            """
        ),
    )


def build_patches(broken: dict[str, str], fixed: dict[str, str]) -> dict[str, str]:
    patches = {
        "linescan.patch": run_patch(
            broken["search/LineScan.ts"],
            fixed["search/LineScan.ts"],
            "search/LineScan.ts",
        ),
        "clusterprobe.patch": run_patch(
            broken["search/ClusterProbe.ts"],
            fixed["search/ClusterProbe.ts"],
            "search/ClusterProbe.ts",
        ),
        "podfold.patch": run_patch(
            broken["pod/PodFold.ts"],
            fixed["pod/PodFold.ts"],
            "pod/PodFold.ts",
        ),
    }
    for name, body in patches.items():
        if not body.strip():
            raise RuntimeError(f"empty patch generated: {name}")
    return patches


def build_milestones(patches: dict[str, str], digest: str) -> None:
    test_sh = textwrap.dedent(
        """\
        #!/bin/bash

        if [ "$PWD" = "/" ]; then
            echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile."
            exit 1
        fi

        pytest --ctrf /logs/verifier/ctrf.json /tests/test_m1.py -rA
        rc=$?

        if [ "$rc" -eq 0 ]; then
          echo 1 > /logs/verifier/reward.txt
        else
          echo 0 > /logs/verifier/reward.txt
        fi
        """
    )
    test_sh_m2 = test_sh.replace("test_m1.py", "test_m2.py")
    write(TASK / "steps/milestone_1/tests/test.sh", test_sh)
    write(TASK / "steps/milestone_2/tests/test.sh", test_sh_m2)
    chmod_x(TASK / "steps/milestone_1/tests/test.sh")
    chmod_x(TASK / "steps/milestone_2/tests/test.sh")
    write(TASK / "steps/milestone_1/tests/test_m1.py", test_m1_py())
    write(TASK / "steps/milestone_2/tests/test_m2.py", test_m2_py(digest))

    write(
        TASK / "steps/milestone_1/instruction.md",
        textwrap.dedent(
            """\
            The Lines of Action replay writer under `/app/environment` emits wrong line counts and cluster fields on several bundled slates. Repair the source, rebuild with `bash /app/environment/assemble.sh`, and regenerate `/app/output/replay_trace.json` from `/app/loa/manifests/matches.txt`. Hand-written JSON is rejected.

            Run `/app/bin/loa replay /app/loa/manifests/matches.txt /app/output/replay_trace.json`. Each match in the trace reports `match_id`, `plies`, `winner`, and `finish`; see `/app/loa/docs/rules.md` for ply fields and win detection. The writer must accept extra manifest blocks under `/app/output/` that use the same notation. Module-level logic under `/app/environment` must match the CLI output.

            Signal completion once the trace file is written before advancing to the next step.

            Canal slates stall after six plies with both sides still mobile. Fuse slates can end on a single connect win. The writer must honor alternate boards such as ridge without special-casing manifest identifiers.
            """
        ),
    )
    write(
        TASK / "steps/milestone_2/instruction.md",
        textwrap.dedent(
            """\
            The standings fold must read `/app/loa/manifests/league.txt` and `/app/output/replay_trace.json`, then write `/app/output/standings.json` with `rows` carrying `points` and `rank`. Repair source under `/app/environment`, rebuild, and rerun the pod command. Static JSON is rejected.

            Run `/app/bin/loa pod /app/loa/manifests/league.txt /app/output/replay_trace.json /app/output/standings.json`. Rerun replay first if the trace is missing or stale. Scoring, tie order, and digest rules are in `/app/loa/docs/rules.md`.

            Signal completion once the standings file is written before advancing to the next step.

            Players with the same points, connect wins, and wire bonus share a rank; player name breaks sort order only. The fold reads line counts and finish reasons from the regenerated trace rather than recomputing board physics.
            """
        ),
    )

    for name, body in patches.items():
        if name.startswith("pod"):
            write(TASK / "steps/milestone_2/solution" / name, body)
        else:
            write(TASK / "steps/milestone_1/solution" / name, body)

    write(
        TASK / "steps/milestone_1/solution/solve1.sh",
        textwrap.dedent(
            """\
            #!/bin/bash
            set -euo pipefail

            SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
            cd /app/environment

            patch -p0 --forward < "${SCRIPT_DIR}/linescan.patch"
            patch -p0 --forward < "${SCRIPT_DIR}/clusterprobe.patch"

            bash /app/environment/assemble.sh
            rm -f /app/output/replay_trace.json
            /app/bin/loa replay /app/loa/manifests/matches.txt /app/output/replay_trace.json
            """
        ),
    )
    write(
        TASK / "steps/milestone_2/solution/solve2.sh",
        textwrap.dedent(
            """\
            #!/bin/bash
            set -euo pipefail

            SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
            cd /app/environment

            patch -p0 --forward < "${SCRIPT_DIR}/podfold.patch"

            bash /app/environment/assemble.sh
            rm -f /app/output/standings.json
            /app/bin/loa pod /app/loa/manifests/league.txt /app/output/replay_trace.json /app/output/standings.json
            """
        ),
    )
    for milestone, script in (("milestone_1", "solve1.sh"), ("milestone_2", "solve2.sh")):
        write(
            TASK / "steps" / milestone / "solution" / "solve.sh",
            textwrap.dedent(
                f"""\
                #!/bin/bash
                set -euo pipefail
                SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
                bash "$SCRIPT_DIR/{script}"
                """
            ),
        )
        chmod_x(TASK / "steps" / milestone / "solution" / "solve.sh")
        chmod_x(TASK / "steps" / milestone / "solution" / script)


def build_metadata(digest: str) -> None:
    write(
        TASK / "task.toml",
        textwrap.dedent(
            """\
            version = "2.0"

            [metadata]
            author_name = "anonymous"
            author_email = "anonymous"
            difficulty = "hard"
            category = "games"
            tags = ["lines-of-action", "queen-line", "cluster-count", "replay-trace", "pod-standings"]
            languages = ["typescript", "bash"]
            codebase_size = "small"
            number_of_milestones = 2
            subcategories = ["tool_specific"]
            expert_time_estimate_min = 100
            junior_time_estimate_min = 260

            [environment]
            allow_internet = false
            build_timeout_sec = 600
            cpus = 2
            memory_mb = 4096
            storage_mb = 10240
            workdir = "/app"

            [[steps]]
            name = "milestone_1"

            [steps.agent]
            timeout_sec = 1200.0

            [steps.verifier]
            timeout_sec = 450.0

            [[steps]]
            name = "milestone_2"

            [steps.agent]
            timeout_sec = 1200.0

            [steps.verifier]
            timeout_sec = 450.0
            """
        ),
    )
    write(
        TASK / "output_contract.toml",
        textwrap.dedent(
            """\
            user_visible_outputs = [
                "/app/output/replay_trace.json",
                "/app/output/standings.json",
            ]

            internal_harness_files = [
                "/app/environment/shared/Main.ts",
                "/app/environment/replay/ScriptRunner.ts",
                "/app/environment/replay/WireMove.ts",
                "/app/environment/search/LineScan.ts",
                "/app/environment/search/ClusterProbe.ts",
                "/app/environment/pod/PodFold.ts",
            ]

            [structured_outputs.replay_trace]
            target = "/app/output/replay_trace.json"
            format = "json"
            instruction_checks = [
                "matches",
                "plies",
                "winner",
                "finish",
                "line_count",
                "components_w",
            ]

            [structured_outputs.standings]
            target = "/app/output/standings.json"
            format = "json"
            instruction_checks = [
                "rows",
                "points",
                "rank",
                "digest",
            ]
            """
        ),
    )
    write(
        TASK / "construction_manifest.json",
        json.dumps(
            {
                "oracle_frontier": [
                    {
                        "path": "environment/search/LineScan.ts",
                        "fix_symbols": ["count"],
                        "co_resident_helpers": ["Coord"],
                        "allowed_top_level_symbols": ["LineScan"],
                    },
                    {
                        "path": "environment/search/ClusterProbe.ts",
                        "fix_symbols": ["components", "connected"],
                        "co_resident_helpers": ["Coord"],
                        "allowed_top_level_symbols": ["ClusterProbe"],
                    },
                    {
                        "path": "environment/pod/PodFold.ts",
                        "fix_symbols": ["run"],
                        "co_resident_helpers": [],
                        "allowed_top_level_symbols": ["PodFold"],
                    },
                ],
                "flipping_point_contract": {
                    "locations": [
                        {
                            "id": "A",
                            "path": "environment/search/LineScan.ts",
                            "controls_tests": [
                                "test_trace_matches_reference_engine",
                                "test_fuse_ring_connect_win",
                            ],
                        },
                        {
                            "id": "B",
                            "path": "environment/search/ClusterProbe.ts",
                            "controls_tests": [
                                "test_ridge_board_probe",
                                "test_canal_link_draw_immobile",
                            ],
                        },
                        {
                            "id": "C",
                            "path": "environment/pod/PodFold.ts",
                            "controls_tests": [
                                "test_points_and_ranks",
                                "test_pod_depends_on_trace",
                            ],
                        },
                    ],
                    "no_single_location_flips_majority": True,
                    "concentration_cap": 0.5,
                },
                "reference_pattern": {"reference_task_id": "fanorona-sweep-replay-cup"},
            },
            indent=2,
        )
        + "\n",
    )
    write(ROOT / "specs" / "loa-wire-cluster-pod.md", spec_md(digest))
    write(ROOT / "sample_task/rubrics/loa-wire-cluster-pod.txt", rubric_txt())
    write(ROOT / "sample_task/submission-notes/loa-wire-cluster-pod.txt", submission_notes_txt())


def count_environment_files() -> int:
    return sum(
        1
        for path in ENV.rglob("*")
        if path.is_file() and path.name not in {"Dockerfile"} and "node_modules" not in path.parts
    )


def main() -> int:
    if TASK.exists():
        shutil.rmtree(TASK)
    broken = ts_sources()
    build_environment_files(broken)
    gen = load_gen()
    trace = gen.replay_manifest(MATCHES_TXT)
    standings = gen.expected_standings(trace, LEAGUE_TXT)
    digest = standings["digest"]
    fixed = fixed_sources(broken)
    patches = build_patches(broken, fixed)
    build_milestones(patches, digest)
    build_metadata(digest)
    env_count = count_environment_files()
    print(f"Generated {TASK}")
    print(f"environment file count (excl Dockerfile): {env_count}")
    print(f"trace winners: {[(m['match_id'], m['winner'], m['finish']) for m in trace['matches']]}")
    print(f"standings digest: {digest}")
    if env_count < 20:
        raise SystemExit(f"expected >=20 environment files, got {env_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
