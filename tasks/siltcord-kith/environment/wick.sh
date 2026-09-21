#!/bin/sh
set -eu
export PATH="/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
mkdir -p /app/bin /app/deskjson /app/idxbay
rustc --edition 2021 -O /app/siltcli/boot.rs -o /app/bin/siltcord
