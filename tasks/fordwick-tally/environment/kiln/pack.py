#!/usr/bin/env python3
"""Fold blot/tether/spout/spanwell into /app/varnish/mill.pyc."""
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path("/app")
PARTS = [
    ROOT / "blot.py",
    ROOT / "tether.py",
    ROOT / "spout.py",
    ROOT / "spanwell.py",
]
SKIP_PREFIXES = (
    "from blot ",
    "import blot",
    "from tether ",
    "import tether",
    "from spout ",
    "import spout",
)


def _strip(text: str) -> tuple[list[str], list[str]]:
    futures: list[str] = []
    keep: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if any(stripped.startswith(p) for p in SKIP_PREFIXES):
            continue
        if stripped.startswith("from __future__ import"):
            if stripped not in futures:
                futures.append(stripped)
            continue
        keep.append(line)
    return futures, keep


def main() -> None:
    out_dir = ROOT / "varnish"
    out_dir.mkdir(parents=True, exist_ok=True)
    packed = out_dir / "packed.py"
    all_future: list[str] = []
    bodies: list[str] = []
    for p in PARTS:
        futures, keep = _strip(p.read_text(encoding="utf-8"))
        for item in futures:
            if item not in all_future:
                all_future.append(item)
        bodies.append("\n".join(keep))
    packed.write_text("\n".join(all_future) + "\n\n" + "\n\n".join(bodies) + "\n", encoding="utf-8")
    py_compile.compile(str(packed), cfile=str(out_dir / "mill.pyc"), doraise=True)


if __name__ == "__main__":
    main()
