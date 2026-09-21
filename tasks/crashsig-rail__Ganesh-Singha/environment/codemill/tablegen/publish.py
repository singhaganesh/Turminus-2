"""Write routing_map.py from roster rows."""

from __future__ import annotations

from pathlib import Path

from codemill.tablegen.guard import should_emit
from codemill.tablegen.roster_read import load_pairs

OUT = Path("/app/relaydesk/gen/routing_map.py")


def build_source(rows: list[tuple[str, str]]) -> str:
    lines = ['"""Generated routing map. Do not edit."""', "", "OWNERS = {"]
    for sig, team in sorted(rows):
        lines.append(f'    "{sig}": "{team}",')
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def emit_map(path: Path | None = None) -> bool:
    target = path or OUT
    target.parent.mkdir(parents=True, exist_ok=True)
    body = build_source(load_pairs())
    if not should_emit(target, body):
        return False
    target.write_text(body)
    return True
