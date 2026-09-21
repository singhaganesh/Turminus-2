#!/usr/bin/env bash
set -euo pipefail
# Occupancy-edge mill (same idea as wickpit.touchcue) then fold.
cat > /app/blot.py << 'PY'
from __future__ import annotations
import cv2
LINE_Y = 70
def make_mog():
    return cv2.createBackgroundSubtractorMOG2(history=30, varThreshold=16, detectShadows=True)
def blot_mark(frame, mog) -> bool:
    fg = mog.apply(frame)
    _, th = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
    y = int(LINE_Y)
    band = th[max(0, y - 1) : min(th.shape[0], y + 2)]
    return bool(band.any())
PY
cat > /app/tether.py << 'PY'
from __future__ import annotations
def knit_marks(now: bool, prev: bool, n: int) -> tuple[int, bool]:
    if now and not prev:
        n += 1
    return n, now
def fold_gate(n: int) -> int:
    return n
PY
cat > /app/spout.py << 'PY'
from __future__ import annotations
import cv2, toml
from pathlib import Path
from blot import blot_mark, make_mog
from tether import fold_gate, knit_marks
SHEET = Path("/app/inkwell/sheet.toml")
def emit_span(src: str) -> int | None:
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        return None
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
PY
cat > /app/spanwell.py << 'PY'
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
PY
bash /app/kiln/bake.sh
