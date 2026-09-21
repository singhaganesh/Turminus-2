"""Skip-if-unchanged guard for routing map writes."""

from __future__ import annotations

from pathlib import Path

from codemill.tablegen.ast_read import read_map_literal


def should_emit(path: Path, fresh_body: str) -> bool:
    if not path.exists():
        return True
    try:
        on_disk = read_map_literal(path.read_text())
    except (SyntaxError, ValueError):
        on_disk = None
    if on_disk is None:
        return False
    return on_disk == read_map_literal(fresh_body)
