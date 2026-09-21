#!/bin/bash
set -euo pipefail
python3 - << 'PY'
from pathlib import Path
p = Path("/app/cupeel/pick.c")
t = p.read_text()
old = """    int idx = -1;
    for (int i = 0; i < n; i++) {
        if (strcmp(rows[i].name, name) == 0) { idx = i; break; }
    }
    (void)pick_last;"""
new = """    int idx = pick_last(rows, n, name);"""
if old not in t:
    raise SystemExit("decoy pattern missing")
p.write_text(t.replace(old, new, 1))
PY
make -C /app/tblkit -f hull.mk hull
/app/bin/lotxref reknit
