#!/bin/sh
set -eu
export PATH="/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
mkdir -p /app/bin
rustc --edition 2021 -O /app/deskbin/main.rs -o /app/bin/clatter
