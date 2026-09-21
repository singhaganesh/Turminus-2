#!/bin/bash
set -euo pipefail
JAVAC="${JAVA_HOME:-/opt/java/openjdk}/bin/javac"
JAVA="${JAVA_HOME:-/opt/java/openjdk}/bin/java"
if [ ! -x "$JAVAC" ]; then
  JAVAC=javac
  JAVA=java
fi
mkdir -p /app/blastcp /app/silo /app/bin
"$JAVAC" -d /app/blastcp /app/recipit/LoomCue.java
"$JAVA" -cp /app/blastcp LoomCue
mapfile -t SRC < <(find /app/recipit /app/markwell /app/siltpage /app/hitchbay /app/retrycue -name '*.java' | sort)
"$JAVAC" -d /app/blastcp "${SRC[@]}"
cat > /app/bin/crumbark << 'EOF'
#!/bin/bash
set -euo pipefail
JAVA="${JAVA_HOME:-/opt/java/openjdk}/bin/java"
if [ ! -x "$JAVA" ]; then
  JAVA=java
fi
verb="${1:-}"
shift || true
case "$verb" in
  tamp)
    exec /app/brimvat.sh
    ;;
  lade|wake|pull|nick)
    exec "$JAVA" -cp /app/blastcp DeskMain "$verb" "$@"
    ;;
  *)
    exit 2
    ;;
esac
EOF
chmod +x /app/bin/crumbark /app/brimvat.sh
