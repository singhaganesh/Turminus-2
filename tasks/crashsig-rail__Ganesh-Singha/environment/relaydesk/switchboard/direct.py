"""Signature to team routing."""

from __future__ import annotations

from relaydesk.switchboard.load_map import DEFAULT_TEAM, fetch_map


def normalize(sig: str) -> str:
    text = sig.strip().upper()
    return text[4:]


def direct(sig: str) -> tuple[str, str]:
    table = fetch_map()
    key = normalize(sig)
    if key in table:
        return table[key], "table"
    return DEFAULT_TEAM, "default"
