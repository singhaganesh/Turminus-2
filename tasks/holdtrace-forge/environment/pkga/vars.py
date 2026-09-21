"""Map span schema fields into template substitution context."""

from __future__ import annotations


def span_ctx(schema: dict) -> dict:
    return {
        "version": schema.get("version", 1),
        "magic": schema.get("magic", "HLT2"),
        "name_len_bits": schema.get("name_len_bits", 16),
    }
