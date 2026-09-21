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
apply_patch "$SCRIPT_DIR/bag.patch"
apply_patch "$SCRIPT_DIR/walk.patch"
apply_patch "$SCRIPT_DIR/pour.patch"
cp "$SCRIPT_DIR/bag.c" /app/cordspin/bag.c
cp "$SCRIPT_DIR/walk.c" /app/chunkvat/walk.c
cp "$SCRIPT_DIR/pour.c" /app/emitbay/pour.c
rm -f /app/cordspin/*.rej /app/chunkvat/*.rej /app/emitbay/*.rej
python3 - <<'PY'
from pathlib import Path
import os
base = Path(os.environ["SCRIPT_DIR"])
pairs = [
    (base / "bag.c", Path("/app/cordspin/bag.c")),
    (base / "walk.c", Path("/app/chunkvat/walk.c")),
    (base / "pour.c", Path("/app/emitbay/pour.c")),
]
for src, dst in pairs:
    text = src.read_text()
    if "bag_freeze" not in text and dst.name == "bag.c":
        raise SystemExit("missing freeze")
    dst.write_text(text)
PY
chmod +x /app/hull.sh
/app/hull.sh
mkdir -p /app/cordwell
/app/bin/flaxcord spin /app/spoolbay/day /app/cordwell/live.pfl
/app/bin/flaxcord spin /app/spoolbay/dusk /app/cordwell/alt.pfl
/app/bin/flaxcord differ /app/cordwell/live.pfl /app/cordwell/alt.pfl
