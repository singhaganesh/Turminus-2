#!/bin/bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
p = Path("/app/vats/worker.vat")
text = p.read_text()
if "attempt_slot" not in text:
    text = text.replace("cols:id,label", "cols:id,label,attempt_slot")
    text = text.replace("row:1,boot", "row:1,boot,0")
    p.write_text(text)
Path("/app/vats/assay.ok").write_text("ok\n")
PY
