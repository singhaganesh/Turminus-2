"""Read fault roster TOML."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROSTER = Path("/app/faultdata/roster.toml")


def load_pairs(path: Path | None = None) -> list[tuple[str, str]]:
    src = path or ROSTER
    doc = tomllib.loads(src.read_text())
    pairs: list[tuple[str, str]] = []
    for row in doc.get("roster", {}).get("signatures", []):
        sig = str(row.get("id", "")).strip().upper()
        team = str(row.get("owner", "")).strip()
        if sig and team:
            pairs.append((sig, team))
    if not pairs:
        raise ValueError("empty roster")
    return pairs
