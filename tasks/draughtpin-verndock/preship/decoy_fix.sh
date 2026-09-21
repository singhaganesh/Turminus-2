#!/bin/bash
set -euo pipefail
# decoy: drop the retained body from the archive
python3 - << 'PY'
from pathlib import Path
p = Path("/app/stemcask/wick.rs")
t = p.read_text()
# comment out wick_old export by renaming
t = t.replace("pub unsafe extern \"C\" fn wick_old", "unsafe extern \"C\" fn wick_old")
p.write_text(t)
PY
/app/stoke.sh || true
