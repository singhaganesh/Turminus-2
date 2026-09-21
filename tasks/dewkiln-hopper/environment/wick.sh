#!/bin/sh
set -eu
export PATH="/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
mkdir -p /app/bin /app/bloturn /app/packbay
rustc --edition 2021 -O /app/wickmill/boot.rs -o /app/bin/dewkiln
