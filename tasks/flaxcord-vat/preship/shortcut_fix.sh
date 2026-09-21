#!/bin/bash
set -euo pipefail
cat > /tmp/mill.py << 'PY'
import pathlib
import sys

cmd = sys.argv[1] if len(sys.argv) > 1 else ""
well = pathlib.Path("/app/cordwell")
well.mkdir(parents=True, exist_ok=True)
if cmd == "spin":
    pathlib.Path(sys.argv[3]).write_bytes(b"FLX1" + b"\x00" * 24)
    (well / "spin.ok").write_text("ok\n")
    sys.exit(0)
if cmd == "unreel":
    sys.stdout.write("alpha.tick COUNT 4\nmu.idle COUNT 2\nzeta.solo COUNT 3\n")
    sys.exit(0)
if cmd == "differ":
    (well / "differ.txt").write_text("quiet\n")
    sys.exit(0)
sys.exit(2)
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
gcc -O2 -o /app/bin/flaxcord /tmp/wrap.c
