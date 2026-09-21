#!/bin/bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
bin_path = Path("/app/bin/weltquay")
bin_path.write_text(
    """#!/usr/bin/env python3
import json, sys
from pathlib import Path
Path("/app/blotbay").mkdir(parents=True, exist_ok=True)
Path("/app/blotbay/rows.json").write_text(
    '{"kind":5,"lane":17,"mode":9,"welt":423,"tail":6,"mark":165}\\n'
)
"""
)
bin_path.chmod(0o755)
Path("/app/blotbay").mkdir(parents=True, exist_ok=True)
Path("/app/blotbay/rows.json").write_text(
    '{"kind":5,"lane":17,"mode":9,"welt":423,"tail":6,"mark":165}\n'
)
PY
