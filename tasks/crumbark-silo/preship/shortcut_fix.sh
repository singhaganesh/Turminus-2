#!/bin/bash
set -euo pipefail
python3 - << 'PY'
import hashlib, json
from pathlib import Path
inbox = Path("/app/inbox")
held = []
for p in sorted(inbox.glob("*.slip")):
    hid = hashlib.sha256(p.read_bytes()).digest()[:16].hex()
    held.append(hid)
Path("/app/silo/wake.json").write_text(json.dumps({"held": held, "note": "ok", "kind": "live"}))
PY
