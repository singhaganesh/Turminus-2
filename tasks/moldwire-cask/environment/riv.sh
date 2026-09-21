#!/bin/sh
set -eu
export JAVA_HOME="${JAVA_HOME:-/opt/java/openjdk}"
export PATH="${JAVA_HOME}/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
mkdir -p /app/classes /app/bin /app/incpit /app/jsonpit /app/piturn/store
javac -d /app/classes /app/slagbin/*.java /app/piturn/*.java /app/dockcli/*.java
java -cp /app/classes Bake
gcc -O2 -o /app/bin/moldwire /app/dockcli/main.c /app/ribwire/run.c -I/app/incpit
