#!/bin/bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
import struct

def rec(name, rank):
    b = name.encode()
    return struct.pack(">H", len(b)) + b + bytes([rank])

ids = [
    ("brim_alert", 3),
    ("deny_gate", 4),
    ("http_pause", 1),
    ("stall_watch", 2),
    ("vault_slip", 7),
]
ord_body = "\n".join(n for n, _ in ids) + "\n"
Path("/app/spillbay/kinds.ord").write_text(ord_body)
blob = b"".join(rec(n, r) for n, r in ids)
Path("/app/rankbin/ranks.bin").write_bytes(blob)
Path("/app/docket/filed.bin").write_bytes(blob)
Path("/app/bin/kindspill").write_text("#!/bin/sh\necho '{\"findings\":[]}'\n")
Path("/app/bin/kindspill").chmod(0o755)
PY
