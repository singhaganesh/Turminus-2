#!/bin/bash
set -euo pipefail
test -f /app/wickbin/layout.qmap
test -f /app/wickbin/flame.qprf
hdr=$(sed -n '1p' /app/wickbin/layout.qmap)
test "$hdr" = "QMAP1"
row=$(sed -n '2p' /app/wickbin/layout.qmap)
path=$(printf '%s\n' "$row" | awk '{print $1}')
ncol=$(printf '%s\n' "$row" | awk '{print NF}')
test "$path" = "/app/hearthbin/span.elf"
test "$ncol" -eq 6
fh=$(sed -n '1p' /app/wickbin/flame.qprf)
test "$fh" = "QPRF1"
nlines=$(grep -c . /app/wickbin/flame.qprf || true)
test "$nlines" -ge 2
while read -r pc name; do
  test -n "$pc"
  test -n "$name"
  test "$name" != "?"
  test "$name" != "dead"
done < <(tail -n +2 /app/wickbin/flame.qprf)
nm -P /app/hearthbin/span.elf | awk '$2 ~ /^[Tt]$/ {print tolower($3), $1}' > /tmp/quillay-nm.txt
while read -r pc name; do
  got=$(awk -v p="$pc" '$1==p {print $2; exit}' /tmp/quillay-nm.txt)
  if test -n "$got"; then
    test "$got" = "$name"
  fi
done < <(tail -n +2 /app/wickbin/flame.qprf)
head -c 4 /app/bin/quillay | od -An -tx1 | grep -q "7f 45 4c 46"
