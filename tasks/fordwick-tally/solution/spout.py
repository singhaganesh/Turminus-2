from __future__ import annotations

import cv2
import toml
from pathlib import Path

from blot import blot_mark, make_mog
from tether import fold_gate, knit_marks

SHEET = Path("/app/inkwell/sheet.toml")


def emit_span(src: str) -> int | None:
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        return None
    mog = make_mog()
    tracks = []
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        dets = blot_mark(frame, mog)
        for tr in tracks:
            tr["last_y"] = tr["y"]
        tracks = knit_marks(dets, tracks)
        n = fold_gate(tracks, n)
    cap.release()
    return n


def dump_sheet(n: int) -> None:
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    SHEET.write_text(toml.dumps({"crossings": int(n)}), encoding="utf-8")
