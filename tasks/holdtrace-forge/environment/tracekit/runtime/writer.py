"""Generated trace writer (schema v2)."""

from __future__ import annotations

from tracekit.runtime.pack import encode_trace

MAGIC = b"HLT2"
NAME_LEN_BITS = 16


def emit_lane(lane_id: int, event: str, grams: int) -> bytes:
    return encode_trace(MAGIC, lane_id, event, grams, NAME_LEN_BITS)
