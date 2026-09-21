#!/bin/bash
set -euo pipefail
JAVAC="${JAVA_HOME:-/opt/java/openjdk}/bin/javac"
JAR="${JAVA_HOME:-/opt/java/openjdk}/bin/jar"
JAVA="${JAVA_HOME:-/opt/java/openjdk}/bin/java"
if [ ! -x "$JAVAC" ]; then
  JAVAC=javac
  JAR=jar
  JAVA=java
fi
rm -rf /tmp/kilsrc /tmp/kildst /tmp/shipcp /tmp/draftcp /app/blastcp
mkdir -p /tmp/kilsrc /tmp/kildst /tmp/shipcp /tmp/draftcp /app/blastcp /app/jarhearth /app/bin
cp /app/tarnpit/*.java /tmp/kilsrc/
cp /app/rillcue/*.java /tmp/kilsrc/
mapfile -t ALL < <(find /app/tarnpit /app/hopcue /app/watchbay /app/draftcue /app/peekcue /app/kilnrib /app/rillcue /app/softmill -name '*.java' | sort)
"$JAVAC" -d /app/blastcp "${ALL[@]}"
"$JAVA" -cp /app/blastcp KilnShip /tmp/kilsrc /tmp/kildst
mapfile -t SHIPSRC < <(find /tmp/kildst /app/hopcue /app/watchbay /app/softmill -name '*.java' | sort)
"$JAVAC" -d /tmp/shipcp "${SHIPSRC[@]}"
mapfile -t DRAFTSRC < <(find /app/tarnpit /app/hopcue /app/draftcue /app/softmill -name '*.java' | sort)
"$JAVAC" -d /tmp/draftcp "${DRAFTSRC[@]}"
(
  cd /tmp/shipcp
  "$JAR" cf /app/jarhearth/ship.jar .
)
(
  cd /tmp/draftcp
  "$JAR" cf /app/jarhearth/draft.jar .
)
python3 - << 'PY'
import io
import zipfile
from pathlib import Path
src = Path("/app/jarhearth/ship.jar")
body = Path("/app/jarhearth/STAMP.body").read_bytes()
buf = io.BytesIO()
with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(buf, "w") as zout:
    for info in zin.infolist():
        if info.filename in ("STAMP", "STAMP.body"):
            continue
        zout.writestr(info, zin.read(info.filename))
    zout.writestr("STAMP", body)
src.write_bytes(buf.getvalue())
want = Path("/app/opslip/MARK.txt").read_text().strip()
with zipfile.ZipFile(src) as z:
    got = z.read("STAMP").decode().strip()
if got != want:
    raise SystemExit(1)
PY
cat > /app/bin/cinderwait << 'EOF'
#!/bin/bash
set -euo pipefail
JAVA="${JAVA_HOME:-/opt/java/openjdk}/bin/java"
if [ ! -x "$JAVA" ]; then
  JAVA=java
fi
verb="${1:-}"
shift || true
case "$verb" in
  kindle)
    exec /app/kindle.sh
    ;;
  watch)
    exec "$JAVA" -cp /app/jarhearth/ship.jar ShipMain "$@"
    ;;
  peek)
    exec "$JAVA" -cp /app/blastcp PeekMain "$@"
    ;;
  draft)
    exec "$JAVA" -cp /app/jarhearth/draft.jar DraftMain "$@"
    ;;
  *)
    exit 2
    ;;
esac
EOF
chmod +x /app/bin/cinderwait /app/kindle.sh
