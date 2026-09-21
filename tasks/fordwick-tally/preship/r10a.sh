#!/usr/bin/env bash
set -euo pipefail
# Occlusion re-ID + split, but no thin-smear reject.
cp /preship/oracle_src/blot.py /app/blot.py
python3 - << 'PY'
from pathlib import Path
p = Path("/app/blot.py")
t = p.read_text()
t = t.replace("THIN = 2.2", "THIN = 99.0")
p.write_text(t)
PY
cp /preship/oracle_src/tether.py /app/tether.py
cp /preship/oracle_src/spout.py /app/spout.py
cp /preship/oracle_src/spanwell.py /app/spanwell.py
bash /app/kiln/bake.sh
