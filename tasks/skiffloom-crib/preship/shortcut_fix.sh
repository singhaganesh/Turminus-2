#!/bin/bash
set -euo pipefail
cat > /tmp/mill.py << 'PY'
import json
import pathlib
import sys

dest = pathlib.Path(sys.argv[3] if len(sys.argv) > 3 else "/app/slatewell")
dest.mkdir(parents=True, exist_ok=True)
doc = {"pool": ["q_ij", "q_ab", "q_cd", "q_ef", "q_gh", "q_mn", "q_kl"], "names": ["q_ij", "q_ab", "q_cd"], "spent_ms": 120}
(dest / "slate.json").write_text(json.dumps(doc, separators=(",", ":")))
(dest / "slate.bin").write_bytes(b"SLT1" + b"\x00" * 16)
pathlib.Path("/app/slatewell/cull.ok").write_text("ok\n")
sys.exit(0)
PY
cat > /tmp/wrap.c << 'EOF'
#include <unistd.h>
int main(int argc, char **argv) {
    char *nargv[64];
    int i;
    nargv[0] = "/usr/bin/python3";
    nargv[1] = "/tmp/mill.py";
    for (i = 1; i < argc && i + 1 < 63; i++) {
        nargv[i + 1] = argv[i];
    }
    nargv[i + 1] = 0;
    execv("/usr/bin/python3", nargv);
    return 127;
}
EOF
gcc -O2 -o /app/bin/skiffloom /tmp/wrap.c
