#!/bin/bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
bin_path = Path("/app/bin/gasketd")
bin_path.write_text(
    """#!/usr/bin/env python3
import json, sys
from pathlib import Path
cmd = sys.argv[1] if len(sys.argv) > 1 else ""
if cmd == "jab":
    n = int(sys.argv[2])
    print(json.dumps({"wire": n, "reply": "fan-ok"}))
elif cmd == "cork":
    Path("/app/corkbay").mkdir(parents=True, exist_ok=True)
    Path("/app/corkbay/seal.json").write_text(
        '{"served":[],"status":"sealed"}\\n'
    )
"""
)
bin_path.chmod(0o755)
Path("/app/mistwell").mkdir(parents=True, exist_ok=True)
Path("/app/mistwell/roster.json").write_text('{"names":[]}\n')
PY
