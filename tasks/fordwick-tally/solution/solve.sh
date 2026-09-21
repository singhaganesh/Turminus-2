#!/usr/bin/env bash
set -euo pipefail
cat > /app/blot.py << 'PY_BLOT_PY'
from __future__ import annotations

import cv2
import numpy as np

LINE_Y = 70
MIN_AREA = 80.0
NMS = 12.0
SPLIT_AREA = 380.0
SPLIT_WIDE = 28
THIN = 2.2


def make_mog():
    return cv2.createBackgroundSubtractorMOG2(
        history=50, varThreshold=12, detectShadows=True
    )


def _centroid(c):
    m = cv2.moments(c)
    if m["m00"] <= 1e-6:
        return None
    return m["m10"] / m["m00"], m["m01"] / m["m00"]


def blot_mark(frame, mog):
    fg = mog.apply(frame)
    _, th = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    raw = []
    for c in cnts:
        area = float(cv2.contourArea(c))
        if area < MIN_AREA:
            continue
        x, y, w, h = cv2.boundingRect(c)
        short, long = min(w, h), max(w, h)
        if short > 0 and (long / short) >= THIN:
            continue
        if area >= SPLIT_AREA and long >= SPLIT_WIDE:
            if w >= h:
                raw.append((x + w * 0.28, y + h * 0.5, area * 0.5))
                raw.append((x + w * 0.72, y + h * 0.5, area * 0.5))
            else:
                raw.append((x + w * 0.5, y + h * 0.28, area * 0.5))
                raw.append((x + w * 0.5, y + h * 0.72, area * 0.5))
            continue
        cen = _centroid(c)
        if cen is None:
            continue
        raw.append((cen[0], cen[1], area))
    raw.sort(key=lambda t: t[2], reverse=True)
    dets = []
    for x, y, area in raw:
        if any(((x - px) ** 2 + (y - py) ** 2) ** 0.5 < NMS for px, py in dets):
            continue
        dets.append((x, y))
    return dets
PY_BLOT_PY
cat > /app/tether.py << 'PY_TETHER_PY'
from __future__ import annotations

MAX_DIST = 36.0
COAST = 26
LINE_Y = 70


def knit_marks(dets, tracks):
    used = set()
    for tr in tracks:
        best_i = None
        best_d = MAX_DIST
        px = tr["x"] + tr["vx"]
        py = tr["y"] + tr["vy"]
        for i, (x, y) in enumerate(dets):
            if i in used:
                continue
            d = float(((x - px) ** 2 + (y - py) ** 2) ** 0.5)
            if d < best_d:
                best_d = d
                best_i = i
        if best_i is None:
            tr["coast"] += 1
            tr["x"] += tr["vx"]
            tr["y"] += tr["vy"]
            continue
        x, y = dets[best_i]
        used.add(best_i)
        vx = x - tr["x"]
        vy = y - tr["y"]
        tr["vx"] = 0.5 * tr["vx"] + 0.5 * vx
        tr["vy"] = 0.5 * tr["vy"] + 0.5 * vy
        tr["last_y"] = tr["y"]
        tr["x"] = x
        tr["y"] = y
        tr["coast"] = 0
    for i, (x, y) in enumerate(dets):
        if i not in used:
            tracks.append(
                {
                    "x": x,
                    "y": y,
                    "vx": 0.0,
                    "vy": 0.9,
                    "coast": 0,
                    "hit": False,
                    "last_y": y,
                }
            )
    return [t for t in tracks if t["coast"] <= COAST]


def fold_gate(tracks, n):
    for tr in tracks:
        prev = tr.get("last_y", tr["y"])
        y = tr["y"]
        if (not tr["hit"]) and prev < LINE_Y <= y:
            tr["hit"] = True
            n += 1
        tr["last_y"] = y
    return n
PY_TETHER_PY
cat > /app/spout.py << 'PY_SPOUT_PY'
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
PY_SPOUT_PY
cat > /app/spanwell.py << 'PY_SPANWELL_PY'
#!/usr/bin/env python3
from __future__ import annotations

import sys

from spout import dump_sheet, emit_span


def main() -> int:
    if len(sys.argv) != 2:
        return 2
    n = emit_span(sys.argv[1])
    if n is None:
        return 1
    dump_sheet(n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY_SPANWELL_PY
bash /app/kiln/bake.sh
mkdir -p /app/inkwell
python3 /app/varnish/mill.pyc /app/shown.mp4
