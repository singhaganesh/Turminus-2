#!/bin/bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
body = """KILNVAT 1
applied:0003_base
applied:0004_attempt_slot
table:tries
cols:id,label,attempt_slot
row:1,boot,0
"""
Path("/app/vats/plaster.vat").write_text(body)
Path("/app/vats/worker.vat").write_text(body)
Path("/app/vats/assay.ok").write_text("ok\n")
PY
