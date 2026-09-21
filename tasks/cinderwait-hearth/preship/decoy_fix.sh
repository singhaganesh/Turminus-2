#!/bin/bash
set -euo pipefail
python3 - << 'PY'
from pathlib import Path
p = Path("/app/tarnpit/Tarn.java")
s = p.read_text()
s = s.replace(
    "while (a == 0) {\n            a = keld;\n            if (++spins > 12000000) break;\n        }",
    "while (a == 0) {\n            Pacer.nap();\n            a = keld;\n            if (++spins > 12000000) break;\n        }",
)
p.write_text(s)
PY
/app/kindle.sh
