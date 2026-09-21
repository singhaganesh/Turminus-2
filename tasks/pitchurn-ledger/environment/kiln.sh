#!/bin/bash
set -euo pipefail
JAVAC="${JAVA_HOME:-/opt/java/openjdk}/bin/javac"
JAVA="${JAVA_HOME:-/opt/java/openjdk}/bin/java"
mkdir -p /app/deskbin/gen /app/bin /app/urnbay/hot /app/urnbay/cold /app/urnbay/keep /app/urnbay/marks
"$JAVAC" -d /app/deskbin /app/oxemit/RibGen.java /app/nincut/VatGen.java /app/coldrib/DuskGen.java
"$JAVA" -cp /app/deskbin RibGen
"$JAVA" -cp /app/deskbin VatGen
"$JAVA" -cp /app/deskbin DuskGen
chmod -R u+w /app/deskbin/gen
"$JAVAC" -d /app/deskbin -cp /app/deskbin \
  /app/deskbin/gen/Seal.java \
  /app/deskbin/gen/Slice.java \
  /app/hitchcli/Gear.java \
  /app/hitchcli/Idx.java \
  /app/deskbin/gen/Span.java \
  /app/hitchcli/StowRun.java \
  /app/hitchcli/WalkRun.java \
  /app/hitchcli/DrawRun.java \
  /app/hitchcli/CardRun.java \
  /app/hitchcli/Main.java \
  /app/lidmath/Floor.java \
  /app/oxemit/RibGen.java \
  /app/nincut/VatGen.java \
  /app/coldrib/DuskGen.java
cat > /app/bin/pitchurn << 'EOF'
#!/bin/bash
exec /opt/java/openjdk/bin/java -cp /app/deskbin Main "$@"
EOF
chmod +x /app/bin/pitchurn
chmod +x /app/kiln.sh
