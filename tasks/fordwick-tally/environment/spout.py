from __future__ import annotations

import cv2
import toml
from pathlib import Path

from blot import blot_mark, make_mog
from tether import fold_gate, knit_marks

SHEET = Path("/app/inkwell/sheet.toml")


def emit_span(src: str) -> int:
    cap = cv2.VideoCapture(src)
    mog = make_mog()
    prev = False
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        now = blot_mark(frame, mog)
        n, prev = knit_marks(now, prev, n)
    cap.release()
    return fold_gate(n)


def dump_sheet(n: int) -> None:
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    SHEET.write_text(toml.dumps({"crossings": int(n)}), encoding="utf-8")
