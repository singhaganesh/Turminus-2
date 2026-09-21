"""Verifier for relaydesk routing and codemill tablegen."""

from __future__ import annotations

import json
import subprocess
import tomllib
from pathlib import Path

ROSTER = Path("/app/faultdata/roster.toml")
MAP = Path("/app/relaydesk/gen/routing_map.py")
ANCHOR_SIG = "SIG_NULL_DEREF_81c2"
ANCHOR_TEAM = "graphics-guild"
HOLD_SIG = "SIG_HEAP_OOM_7a3f"
HOLD_TEAM = "memory-squad"
UNKNOWN_SIG = "SIG_UNKNOWN_FFFF"
DEFAULT_TEAM = "platform-core"


def _roster_pairs() -> list[tuple[str, str]]:
    doc = tomllib.loads(ROSTER.read_text())
    pairs: list[tuple[str, str]] = []
    for row in doc.get("roster", {}).get("signatures", []):
        sig = str(row.get("id", "")).strip().upper()
        team = str(row.get("owner", "")).strip()
        pairs.append((sig, team))
    return pairs


def _route(sig: str) -> tuple[dict, int, str]:
    proc = subprocess.run(
        ["/app/bin/crashrail", "route", "--signature", sig],
        capture_output=True,
        text=True,
    )
    stdout = proc.stdout.strip()
    line = stdout.splitlines()[-1] if stdout else ""
    try:
        return json.loads(line), proc.returncode, stdout
    except json.JSONDecodeError:
        return {}, proc.returncode, stdout


def _owners_from_map() -> dict[str, str]:
    namespace: dict[str, object] = {}
    exec(compile(MAP.read_text(), str(MAP), "exec"), namespace)
    owners = namespace.get("SIGNATURE_OWNERS")
    if not isinstance(owners, dict):
        raise AssertionError("SIGNATURE_OWNERS missing")
    return {str(k): str(v) for k, v in owners.items()}


def test_generated_artifact_imports():
    """Generated artifact must expose SIGNATURE_OWNERS and import without error."""
    owners = _owners_from_map()
    assert owners


def test_manifest_ids_in_table():
    """Every manifest signature id must be a key in SIGNATURE_OWNERS."""
    owners = _owners_from_map()
    for sig, _ in _roster_pairs():
        assert sig in owners


def test_owner_pairs_match_table():
    """Each manifest owner must match SIGNATURE_OWNERS for its signature."""
    owners = _owners_from_map()
    for sig, team in _roster_pairs():
        assert owners[sig] == team


def test_anchor_sig_team_table():
    """SIG_NULL_DEREF_81c2 must answer graphics-guild via source table."""
    data, code, stdout = _route(ANCHOR_SIG)
    assert json.loads(stdout.splitlines()[-1]) == {"team": ANCHOR_TEAM, "source": "table"}
    assert code == 0
    assert data == {"team": ANCHOR_TEAM, "source": "table"}


def test_hold_sig_team_table():
    """SIG_HEAP_OOM_7a3f must answer memory-squad via source table."""
    data, code, stdout = _route(HOLD_SIG)
    assert json.loads(stdout.splitlines()[-1]) == {"team": HOLD_TEAM, "source": "table"}
    assert code == 0
    assert data == {"team": HOLD_TEAM, "source": "table"}


def test_io_sig_team_table():
    """SIG_IO_TIMEOUT_4f91 must answer storage-cell via source table."""
    data, code, stdout = _route("SIG_IO_TIMEOUT_4f91")
    assert json.loads(stdout.splitlines()[-1]) == {"team": "storage-cell", "source": "table"}
    assert code == 0
    assert data == {"team": "storage-cell", "source": "table"}


def test_auth_sig_team_table():
    """SIG_AUTH_LOOP_22bd must answer identity-ring via source table."""
    data, code, stdout = _route("SIG_AUTH_LOOP_22bd")
    assert json.loads(stdout.splitlines()[-1]) == {"team": "identity-ring", "source": "table"}
    assert code == 0
    assert data == {"team": "identity-ring", "source": "table"}


def test_net_sig_team_table():
    """SIG_NET_RESET_9e04 must answer network-desk via source table."""
    data, code, stdout = _route("SIG_NET_RESET_9e04")
    assert json.loads(stdout.splitlines()[-1]) == {"team": "network-desk", "source": "table"}
    assert code == 0
    assert data == {"team": "network-desk", "source": "table"}


def test_manifest_signatures_route_zero():
    """Every manifest signature must exit zero from route with table sourcing."""
    for sig, team in _roster_pairs():
        data, code, stdout = _route(sig)
        assert json.loads(stdout.splitlines()[-1]) == {"team": team, "source": "table"}
        assert code == 0
        assert data == {"team": team, "source": "table"}


def test_unknown_sig_fallback_exit():
    """Unknown signatures must use platform-core default with non-zero exit."""
    anchor, anchor_code, anchor_stdout = _route(ANCHOR_SIG)
    assert json.loads(anchor_stdout.splitlines()[-1]) == {"team": ANCHOR_TEAM, "source": "table"}
    assert anchor_code == 0
    assert anchor == {"team": ANCHOR_TEAM, "source": "table"}
    data, code, stdout = _route(UNKNOWN_SIG)
    assert json.loads(stdout.splitlines()[-1]) == {"team": DEFAULT_TEAM, "source": "default"}
    assert code != 0
    assert data == {"team": DEFAULT_TEAM, "source": "default"}


def test_table_row_count_matches_manifest():
    """SIGNATURE_OWNERS must contain exactly one entry per manifest signature."""
    owners = _owners_from_map()
    assert len(owners) == len(_roster_pairs())


def test_zz_compile_regenerates_corrupt_map():
    """Compile must rebuild SIGNATURE_OWNERS from roster after the map is corrupted."""
    MAP.write_text('OWNERS = {\n    "SIG_NULL_DEREF_81c2": "graphics-guild",\n')
    proc = subprocess.run(
        ["/app/bin/crashrail", "compile"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    owners = _owners_from_map()
    for sig, team in _roster_pairs():
        assert sig in owners
        assert owners[sig] == team
