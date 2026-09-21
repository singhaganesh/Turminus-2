"""Shared wire helpers for holdtrace traces."""

from __future__ import annotations

import struct
from typing import Tuple


def encode_trace(magic: bytes, lane_id: int, event: str, grams: int, name_len_bits: int) -> bytes:
    if len(magic) != 4:
        raise ValueError("magic must be four bytes")
    name_b = event.encode("utf-8")
    if name_len_bits == 8:
        if len(name_b) > 255:
            raise ValueError("name too long for 8-bit length")
        nlen = struct.pack(">B", len(name_b))
    elif name_len_bits == 16:
        nlen = struct.pack(">H", len(name_b))
    else:
        raise ValueError("unsupported name length width")
    return magic + struct.pack(">H", lane_id) + nlen + name_b + struct.pack(">I", grams)


def decode_trace(
    blob: bytes,
    accept_magics: Tuple[bytes, ...],
    name_len_bits: int,
) -> Tuple[int, str, int]:
    if len(blob) < 11:
        raise ValueError("truncated")
    magic = blob[:4]
    if magic not in accept_magics:
        raise ValueError("bad magic")
    lane_id = struct.unpack(">H", blob[4:6])[0]
    off = 6
    if name_len_bits == 8:
        nlen = blob[off]
        off += 1
    else:
        nlen = struct.unpack(">H", blob[off : off + 2])[0]
        off += 2
    name = blob[off : off + nlen].decode("utf-8")
    off += nlen
    grams = struct.unpack(">I", blob[off : off + 4])[0]
    return lane_id, name, grams
