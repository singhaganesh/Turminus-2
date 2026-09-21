#!/bin/bash
set -euo pipefail
# R7: script mill, not ELF
cat > /app/bin/riftkiln << 'EOF'
#!/usr/bin/env python3
import json, sys
from pathlib import Path
if len(sys.argv) < 4:
    sys.exit(2)
Path(sys.argv[3]).write_text(json.dumps({
    "yard": "north",
    "members": [
        {"kind": "peg", "tag": "a", "mark": "1"},
        {"kind": "pen", "stem": "outer", "members": [
            {"kind": "pen", "stem": "inner", "members": [
                {"kind": "peg", "tag": "b", "mark": "2"}
            ]},
            {"kind": "clip", "stem": "wet"}
        ]}
    ]
}))
EOF
chmod +x /app/bin/riftkiln
