#!/bin/sh
set -eu
export PATH="/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
mkdir -p /app/bin /app/tblwell /app/markcue /app/treypit
rm -f /app/markcue/brew.ok
rustc --edition 2021 -O /app/ovenpit/oven.rs -o /app/bin/tblbake
set +e
/app/bin/tblbake /app/cardhearth/card.yg /app/tblwell
ec=$?
set -e
if [ "$ec" -ne 0 ]; then
  exit "$ec"
fi
rustc --edition 2021 -O /app/drawbin/boot.rs -o /app/bin/riftkiln
touch /app/markcue/brew.ok
/app/bin/riftkiln sift /app/flatpit/flat.quern /app/treypit/flat.json
