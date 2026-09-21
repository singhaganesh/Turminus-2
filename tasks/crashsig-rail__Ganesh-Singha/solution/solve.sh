#!/bin/bash
set -euo pipefail

cd /
p="$(mktemp)"
cat > "$p" <<'PATCH'
--- app/codemill/tablegen/guard.py
+++ app/codemill/tablegen/guard.py
@@ -7,13 +7,20 @@
 from codemill.tablegen.ast_read import read_map_literal
 
 
+def _read_literal(text: str) -> dict[str, str] | None:
+    try:
+        return read_map_literal(text)
+    except (SyntaxError, ValueError):
+        return None
+
+
 def should_emit(path: Path, fresh_body: str) -> bool:
     if not path.exists():
         return True
-    try:
-        on_disk = read_map_literal(path.read_text())
-    except (SyntaxError, ValueError):
-        on_disk = None
+    on_disk = _read_literal(path.read_text())
     if on_disk is None:
-        return False
-    return on_disk == read_map_literal(fresh_body)
+        return True
+    candidate = _read_literal(fresh_body)
+    if candidate is None:
+        return True
+    return on_disk != candidate
--- app/codemill/tablegen/publish.py
+++ app/codemill/tablegen/publish.py
@@ -7,20 +7,29 @@
 from codemill.tablegen.guard import should_emit
 from codemill.tablegen.roster_read import load_pairs
 
-OUT = Path("/app/relaydesk/gen/routing_map.py")
 
+def _sorted_rows(rows: list[tuple[str, str]]) -> list[tuple[str, str]]:
+    return sorted(rows)
 
+
+def _render_rows(rows: list[tuple[str, str]]) -> list[str]:
+    return [f'    "{sig}": "{team}",' for sig, team in rows]
+
+
 def build_source(rows: list[tuple[str, str]]) -> str:
-    lines = ['"""Generated routing map. Do not edit."""', "", "OWNERS = {"]
-    for sig, team in sorted(rows):
-        lines.append(f'    "{sig}": "{team}",')
+    lines = [
+        '"""Generated routing map. Do not edit."""',
+        "",
+        "SIGNATURE_OWNERS = {",
+    ]
+    lines.extend(_render_rows(_sorted_rows(rows)))
     lines.append("}")
     lines.append("")
-    return "\n".join(lines)
+    return chr(10).join(lines)
 
 
 def emit_map(path: Path | None = None) -> bool:
-    target = path or OUT
+    target = path or Path("/app/relaydesk/gen/routing_map.py")
     target.parent.mkdir(parents=True, exist_ok=True)
     body = build_source(load_pairs())
     if not should_emit(target, body):
--- app/relaydesk/switchboard/direct.py
+++ app/relaydesk/switchboard/direct.py
@@ -5,9 +5,15 @@
 from relaydesk.switchboard.load_map import DEFAULT_TEAM, fetch_map
 
 
+def _upper_sig(sig: str) -> str:
+    return sig.strip().upper()
+
+
 def normalize(sig: str) -> str:
-    text = sig.strip().upper()
-    return text[4:]
+    text = _upper_sig(sig)
+    if not text.startswith("SIG_"):
+        raise ValueError("bad prefix")
+    return text
 
 
 def direct(sig: str) -> tuple[str, str]:
PATCH

if patch -R -p0 -sf --dry-run < "$p" >/dev/null 2>&1; then
  :
else
  patch -N -p0 < "$p"
fi
rm -f "$p"

/app/bin/crashrail compile

python3 << 'PY'
import json
import subprocess
from pathlib import Path

proc = subprocess.run(
    ["/app/bin/crashrail", "route", "--signature", "SIG_NULL_DEREF_81c2"],
    capture_output=True,
    text=True,
    check=True,
)
assert json.loads(proc.stdout.strip()) == {"team": "graphics-guild", "source": "table"}
assert proc.returncode == 0

import tomllib
for row in tomllib.loads(Path("/app/faultdata/roster.toml").read_text()).get("roster", {}).get("signatures", []):
    sig = str(row.get("id", "")).strip().upper()
    team = str(row.get("owner", "")).strip()
    run = subprocess.run(
        ["/app/bin/crashrail", "route", "--signature", sig],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(run.stdout.strip()) == {"team": team, "source": "table"}
    assert run.returncode == 0

print("oracle ok")
PY
