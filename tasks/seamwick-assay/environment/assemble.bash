#!/bin/bash
set -euo pipefail
JAVAC="${JAVA_HOME:-/opt/java/openjdk}/bin/javac"
JAVA="${JAVA_HOME:-/opt/java/openjdk}/bin/java"
mkdir -p /app/deskbin/gen /app/bin /app/blot
"$JAVAC" -d /app/deskbin \
  /app/purlbox/PurlBox.java \
  /app/knitwell/ops/KnitBox.java \
  /app/tintlag/core/TintBox.java
"$JAVA" -cp /app/deskbin PurlBox
"$JAVA" -cp /app/deskbin KnitBox
"$JAVA" -cp /app/deskbin TintBox
chmod -R u+w /app/deskbin/gen
"$JAVAC" -d /app/deskbin -cp /app/deskbin \
  /app/deskbin/gen/Cite.java \
  /app/deskbin/gen/Sched.java \
  /app/deskbin/gen/Seal.java \
  /app/seamcmd/Bag.java \
  /app/seamcmd/Loom.java \
  /app/seamcmd/Drive.java \
  /app/seamcmd/Nudge.java \
  /app/seamcmd/Flood.java \
  /app/seamcmd/Mark.java \
  /app/seamcmd/Sheet.java \
  /app/seamcmd/Boot.java \
  /app/wipevat/Dump.java \
  /app/impgraph/Scan.java \
  /app/purlbox/PurlBox.java \
  /app/knitwell/ops/KnitBox.java \
  /app/tintlag/core/TintBox.java
cat > /app/bin/seamwick << 'EOF'
#!/bin/bash
exec /opt/java/openjdk/bin/java -cp /app/deskbin Boot "$@"
EOF
chmod +x /app/bin/seamwick
chmod +x /app/assemble.bash
