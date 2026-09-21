#!/usr/bin/env bash
set -euo pipefail
# Thin-smear reject, but no occlusion coast / no blob split.
cp /preship/oracle_src/blot.py /app/blot.py
python3 - << 'PY'
from pathlib import Path
p = Path("/app/blot.py")
t = p.read_text()
t = t.replace("SPLIT_AREA = 380.0", "SPLIT_AREA = 99999.0")
p.write_text(t)
PY
cp /preship/oracle_src/tether.py /app/tether.py
python3 - << 'PY'
from pathlib import Path
p = Path("/app/tether.py")
t = p.read_text()
t = t.replace("COAST = 26", "COAST = 2")
p.write_text(t)
PY
cp /preship/oracle_src/spout.py /app/spout.py
cp /preship/oracle_src/spanwell.py /app/spanwell.py
bash /app/kiln/bake.sh
