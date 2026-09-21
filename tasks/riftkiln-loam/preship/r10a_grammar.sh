#!/bin/bash
set -euo pipefail
# R10a: recipe only, then brew
python3 - << 'PY'
from pathlib import Path
Path("/app/cardhearth/card.yg").write_text("""# rib_b
S : YARD ID LBRACE MS RBRACE ;
MS : MS M | ;
M : PEG ID EQ VAL SEMI
  | PEN ID LBRACE MS RBRACE
  | CLIP ID
  ;
""")
PY
chmod +x /app/hearth.sh
/app/hearth.sh
