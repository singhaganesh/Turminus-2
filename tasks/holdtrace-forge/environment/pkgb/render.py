"""Minimal placeholder substitution for layout templates."""

from __future__ import annotations

from pathlib import Path

LAYOUT = Path(__file__).resolve().parent.parent / "pkgc"


def render_tpl(name: str, ctx: dict) -> str:
    text = (LAYOUT / name).read_text()
    for key, val in ctx.items():
        text = text.replace("{{ " + key + " }}", str(val))
    return text
