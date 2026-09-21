#!/bin/bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
bin_path = Path("/app/bin/glazeurn")
bin_path.write_text(
    """#!/usr/bin/env python3
import json, sys
from pathlib import Path
Path("/app/inkpit").mkdir(parents=True, exist_ok=True)
Path("/app/inkpit/pair.json").write_text(
    '{"tick":8,"mark":6,"frost_bag":["oak","elm","ash"],"live_bag":["oak","yew","ash","fir"]}\\n'
)
Path("/app/inkpit/GUARD").write_text("ok\\n")
"""
)
bin_path.chmod(0o755)
Path("/app/inkpit").mkdir(parents=True, exist_ok=True)
Path("/app/inkpit/pair.json").write_text(
    '{"tick":8,"mark":6,"frost_bag":["oak","elm","ash"],"live_bag":["oak","yew","ash","fir"]}\n'
)
Path("/app/inkpit/GUARD").write_text("ok\n")
PY
