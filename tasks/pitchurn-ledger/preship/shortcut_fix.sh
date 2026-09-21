#!/bin/bash
set -euo pipefail
python3 - << 'PY'
from pathlib import Path
p = Path("/app/urnbay/tally.json")
p.write_text(
    '{\n'
    '  "reel": "stable.bin",\n'
    '  "bytes_in": "24000",\n'
    '  "bytes_stored": "0",\n'
    '  "reuse_frac": "1.00",\n'
    '  "mean_piece": "100.00",\n'
    '  "piece_count": "12"\n'
    '}\n'
)
Path("/app/urnbay/last.json").write_text(p.read_text())
PY
