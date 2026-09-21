#!/bin/sh
set -eu
export PATH="/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
mkdir -p /app/bin /app/bloturn
rustc --edition 2021 -O /app/spindock/spin.rs -o /tmp/spinknit
/tmp/spinknit
rustc --edition 2021 -O /app/fincli/boot.rs -o /app/bin/finspool
