#!/bin/sh
set -eu
export PATH="/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
mkdir -p /app/bin /app/lib /app/inkvat /app/gnuverse
rustc --edition 2021 -O /app/weft/main.rs -o /app/bin/weave
/app/bin/weave
rustc --edition 2021 -O --crate-type staticlib -C panic=abort /app/gluebox/glue.rs -o /tmp/libdraught.a
cc -shared -o /app/lib/libdraught.so -Wl,--version-script=/app/gnuverse/cask.map -Wl,--whole-archive /tmp/libdraught.a -Wl,--no-whole-archive -lc -ldl
rustc --edition 2021 -O /app/cliurn/boot.rs -o /app/bin/draughtpin -C link-arg=-ldl
