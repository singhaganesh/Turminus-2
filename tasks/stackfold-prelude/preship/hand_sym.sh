#!/bin/bash
set -euo pipefail
cp /preship/fold_latch.env /app/pcfold/conf/latch.env
python3 /preship/patch_emit_hook.py
python3 - <<'PY'
import subprocess
from pathlib import Path

runtime = Path("/app/symmill/fold/runtime")
symmap = Path("/app/symmill/fold/runtime.symmap")
profile = Path("/app/symmill/fold/profile.json")
bid_out = subprocess.check_output(["readelf", "-n", str(runtime)], text=True)
build_id = [line.split("Build ID:")[1].strip() for line in bid_out.splitlines() if "Build ID:" in line][0]
nm_out = subprocess.check_output(["nm", "-n", "--defined-only", str(runtime)], text=True)
ordered = []
for line in nm_out.splitlines():
    parts = line.split()
    if len(parts) >= 3 and parts[1] in {"T", "t"}:
        ordered.append((parts[2], int(parts[0], 16)))
lines = ["PCFOLD1", "mode linked", f"buildid {build_id}", "origin pcfold-index-linked"]
for i, (name, start) in enumerate(ordered):
    end = ordered[i + 1][1] if i + 1 < len(ordered) else start + 64
    size = max(end - start, 1)
    lines.append(f"sym {name} 0x{start:x} 0x{size:x}")
symmap.write_text("\n".join(lines) + "\n")
subprocess.run(
    ["/app/bin/pcfold", "render", "/app/benchframes/bench.samples", str(symmap), "-o", str(profile)],
    check=True,
)
PY
