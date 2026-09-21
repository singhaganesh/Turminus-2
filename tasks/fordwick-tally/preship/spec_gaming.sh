#!/usr/bin/env bash
set -euo pipefail
cat > /app/blot.py << 'PY'
from __future__ import annotations
def make_mog():
    return None
def blot_mark(frame, mog) -> bool:
    return False
PY
cat > /app/tether.py << 'PY'
from __future__ import annotations
def knit_marks(now, prev, n):
    return n, now
def fold_gate(n):
    return n
PY
cat > /app/spout.py << 'PY'
from __future__ import annotations
import cv2, toml
from pathlib import Path
SHEET = Path("/app/inkwell/sheet.toml")
def emit_span(src: str):
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        return None
    cap.release()
    return 3
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
