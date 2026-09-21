#!/bin/sh
set -eu
export PATH="/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
mkdir -p /app/bin /app/blotbay /app/vaultbin
rustc --edition 2021 -O /app/kilnbake/hearth.rs -o /tmp/welt-emit
/tmp/welt-emit
rustc --edition 2021 -O /app/weltcli/boot.rs -o /app/bin/weltquay
