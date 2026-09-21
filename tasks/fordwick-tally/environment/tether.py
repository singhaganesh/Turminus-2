from __future__ import annotations


def knit_marks(now: bool, prev: bool, n: int) -> tuple[int, bool]:
    if now:
        n += 1
    return n, now


def fold_gate(n: int) -> int:
    return n
