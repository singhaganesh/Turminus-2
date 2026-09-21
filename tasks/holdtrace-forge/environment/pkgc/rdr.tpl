"""Generated trace reader (schema v{{ version }})."""

from __future__ import annotations

from tracekit.runtime.pack import decode_trace

MAGICS = (b"{{ legacy_magic }}", b"{{ magic }}")
NAME_BITS = {{ name_len_bits }}


def ingest_blob(blob: bytes) -> tuple[int, str, int]:
    return decode_trace(blob, MAGICS, NAME_BITS)
