#!/bin/bash
set -euo pipefail

python3 << 'PY'
from pathlib import Path

Path("/app/codemill/tablegen/guard.py").write_text(
    '''"""Skip-if-unchanged guard for routing map writes."""

from __future__ import annotations

from pathlib import Path

from codemill.tablegen.ast_read import read_map_literal


def _read_literal(text: str) -> dict[str, str] | None:
    try:
        return read_map_literal(text)
    except (SyntaxError, ValueError):
        return None


def should_emit(path: Path, fresh_body: str) -> bool:
    if not path.exists():
        return True
    on_disk = _read_literal(path.read_text())
    if on_disk is None:
        return True
    candidate = _read_literal(fresh_body)
    if candidate is None:
        return True
    return on_disk != candidate
'''
)

Path("/app/codemill/tablegen/publish.py").write_text(
    '''"""Write routing_map.py from roster rows."""

from __future__ import annotations

from pathlib import Path

from codemill.tablegen.guard import should_emit
from codemill.tablegen.roster_read import load_pairs


def _sorted_rows(rows: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return sorted(rows)


def _render_rows(rows: list[tuple[str, str]]) -> list[str]:
    return [f'    "{sig}": "{team}",' for sig, team in rows]


def build_source(rows: list[tuple[str, str]]) -> str:
    lines = [
        '"""Generated routing map. Do not edit."""',
        "",
        "SIGNATURE_OWNERS = {",
    ]
    lines.extend(_render_rows(_sorted_rows(rows)))
    lines.append("}")
    lines.append("")
    return chr(10).join(lines)


def emit_map(path: Path | None = None) -> bool:
    target = path or Path("/app/relaydesk/gen/routing_map.py")
    target.parent.mkdir(parents=True, exist_ok=True)
    body = build_source(load_pairs())
    if not should_emit(target, body):
        return False
    target.write_text(body)
    return True
'''
)

Path("/app/relaydesk/switchboard/direct.py").write_text(
    '''"""Signature to team routing."""

from __future__ import annotations

from relaydesk.switchboard.load_map import DEFAULT_TEAM, fetch_map


def _upper_sig(sig: str) -> str:
    return sig.strip().upper()


def normalize(sig: str) -> str:
    text = _upper_sig(sig)
    if not text.startswith("SIG_"):
        raise ValueError("bad prefix")
    return text


def direct(sig: str) -> tuple[str, str]:
    table = fetch_map()
    key = normalize(sig)
    if key in table:
        return table[key], "table"
    return DEFAULT_TEAM, "default"
'''
)

print("oracle modules refreshed")
PY

/app/bin/crashrail compile

python3 << 'PY'
import json
import subprocess
from pathlib import Path

proc = subprocess.run(
    ["/app/bin/crashrail", "route", "--signature", "SIG_NULL_DEREF_81c2"],
    capture_output=True,
    text=True,
    check=True,
)
assert json.loads(proc.stdout.strip()) == {"team": "graphics-guild", "source": "table"}
assert proc.returncode == 0

import tomllib
for row in tomllib.loads(Path("/app/faultdata/roster.toml").read_text()).get("roster", {}).get("signatures", []):
    sig = str(row.get("id", "")).strip().upper()
    team = str(row.get("owner", "")).strip()
    run = subprocess.run(
        ["/app/bin/crashrail", "route", "--signature", sig],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(run.stdout.strip()) == {"team": team, "source": "table"}
    assert run.returncode == 0

print("oracle ok")
PY
