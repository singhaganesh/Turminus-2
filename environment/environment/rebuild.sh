#!/bin/bash
set -euo pipefail
cd /app
mkdir -p /app/bin
# Prefer offline when crates are vendored; fall back only if needed.
if [ -d /app/vendor/crates ]; then
  cargo build --release --manifest-path /app/Cargo.toml --offline
else
  cargo build --release --manifest-path /app/Cargo.toml
fi
cp -f /app/target/release/quench /app/bin/quench
