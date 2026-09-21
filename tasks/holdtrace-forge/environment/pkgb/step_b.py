"""Load span schema for the forge driver."""

from __future__ import annotations

import json
from pathlib import Path

SCHEMA_PATH = Path("/app/tracekit/schema/span.json")


def step_b() -> dict:
    data = json.loads(SCHEMA_PATH.read_text())
    if not isinstance(data, dict):
        raise ValueError("schema must be a mapping")
    return data
