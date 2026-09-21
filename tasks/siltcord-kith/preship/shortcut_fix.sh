#!/bin/bash
set -euo pipefail
mkdir -p /app/deskjson /app/bin
python3 - <<'PY'
from pathlib import Path
desk = Path("/app/deskjson")
desk.mkdir(parents=True, exist_ok=True)
body = '{"timezone":"America/Chicago","cluster":"alpha","log_events":["EVT_BOOT","EVT_RELOAD"],"member_count":6,"source_kith":"kestrel.kith","walk_sig":"e8c60dff99d1c59bed02f52d0215444f736284d0b7a05d1b6fc164566a787b60"}\n'
(desk / "pass-a.json").write_text(body)
(desk / "pass-b.json").write_text(body)
(desk / "READY").write_text("brief-ok\n")
Path("/app/bin/siltcord").write_text("#!/bin/sh\nexit 0\n")
Path("/app/bin/siltcord").chmod(0o755)
PY
