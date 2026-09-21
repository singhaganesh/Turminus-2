#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

apply_patch() {
  local patch_file="$1"
  if patch -p0 --dry-run -s -f -i "$patch_file" >/dev/null 2>&1; then
    patch -p0 -i "$patch_file"
  fi
}

cd /app
export SCRIPT_DIR
apply_patch "$SCRIPT_DIR/scan.patch"
apply_patch "$SCRIPT_DIR/skip.patch"
apply_patch "$SCRIPT_DIR/emit.patch"
cp "$SCRIPT_DIR/scan.c" /app/rootwell/scan.c
cp "$SCRIPT_DIR/skip.c" /app/softbay/skip.c
cp "$SCRIPT_DIR/emit.c" /app/adjmill/emit.c
rm -f /app/rootwell/*.rej /app/softbay/*.rej /app/adjmill/*.rej
python3 - <<'PY'
from pathlib import Path
import os
base = Path(os.environ["SCRIPT_DIR"])
pairs = [
    (base / "scan.c", Path("/app/rootwell/scan.c")),
    (base / "skip.c", Path("/app/softbay/skip.c")),
    (base / "emit.c", Path("/app/adjmill/emit.c")),
]
for src, dst in pairs:
    dst.write_text(src.read_text())
PY
chmod +x /app/kindle.sh
/app/kindle.sh
mkdir -p /app/inkurn
/app/bin/keelgrip mint /app/packurn/day.hpk /app/inkurn/live.txt
/app/bin/keelgrip mint /app/packurn/dusk.hpk /app/inkurn/alt.txt
/app/bin/keelgrip align /app/inkurn/live.txt /app/inkurn/alt.txt
