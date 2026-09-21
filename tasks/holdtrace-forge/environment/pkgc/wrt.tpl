"""Generated trace writer (schema v{{ version }})."""

from __future__ import annotations

from tracekit.runtime.pack import encode_trace

MAGIC = b"{{ magic }}"
NAME_LEN_BITS = {{ name_len_bits }}


def emit_lane(lane_id: int, event: str, grams: int) -> bytes:
    return encode_trace(MAGIC, lane_id, event, grams, NAME_LEN_BITS)
