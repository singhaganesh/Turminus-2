#!/bin/bash
set -euo pipefail
JAVAC="${JAVA_HOME:-/opt/java/openjdk}/bin/javac"
JAVA="${JAVA_HOME:-/opt/java/openjdk}/bin/java"
if [ ! -x "$JAVAC" ]; then
  JAVAC=javac
  JAVA=java
fi
mkdir -p /app/blastcp /app/jarwell /app/bin
mapfile -t SRC < <(find /app/rootwalk /app/namelock /app/bytecue /app/hitchrun /app/fmtcells /app/gildbox /app/floorcue -name '*.java' | sort)
"$JAVAC" -d /app/blastcp "${SRC[@]}"
"$JAVA" -cp /app/blastcp KnitMain
trc=0
"$JAVA" -cp /app/blastcp TallyGate || trc=$?
crc=0
"$JAVA" -cp /app/blastcp CapGate || crc=$?
cat > /app/bin/dregwick << 'EOF'
#!/bin/bash
set -euo pipefail
JAVA="${JAVA_HOME:-/opt/java/openjdk}/bin/java"
if [ ! -x "$JAVA" ]; then
  JAVA=java
fi
verb="${1:-}"
shift || true
case "$verb" in
  knit)
    exec /app/brim.sh
    ;;
  loom)
    exec "$JAVA" -cp /app/blastcp Main loom "$@"
    ;;
  taste)
    exec "$JAVA" -cp /app/jarwell/husk.jar Main taste "$@"
    ;;
  booth)
    exec "$JAVA" -cp /app/jarwell/husk.jar Main booth "$@"
    ;;
  *)
    exit 2
    ;;
esac
EOF
chmod +x /app/bin/dregwick /app/brim.sh
if [ "$trc" -ne 0 ] || [ "$crc" -ne 0 ]; then
  exit 1
fi
exit 0
