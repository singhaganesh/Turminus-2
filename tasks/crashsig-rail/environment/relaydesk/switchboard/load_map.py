"""Load generated routing maps."""

from __future__ import annotations

from typing import Dict

DEFAULT_TEAM = "platform-core"


def fetch_map() -> Dict[str, str]:
    try:
        from relaydesk.gen.routing_map import SIGNATURE_OWNERS
    except Exception:
        return {}
    if not isinstance(SIGNATURE_OWNERS, dict):
        return {}
    return {str(k): str(v) for k, v in SIGNATURE_OWNERS.items()}
