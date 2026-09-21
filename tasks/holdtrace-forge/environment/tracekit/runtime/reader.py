"""Generated trace reader (stale layout — magic not synced)."""

from __future__ import annotations

from tracekit.runtime.pack import decode_trace

MAGIC = b"HLT1"
LEGACY = (MAGIC,)
NAME_LEN_BITS = 8


def ingest_blob(blob: bytes) -> tuple[int, str, int]:
    return decode_trace(blob, LEGACY, NAME_LEN_BITS)
