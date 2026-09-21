#!/bin/sh
set -eu
export PATH="/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
mkdir -p /app/bin /app/inkbay
rustc --edition 2021 -O /app/ketchcli/main.rs -o /app/bin/loomketch
