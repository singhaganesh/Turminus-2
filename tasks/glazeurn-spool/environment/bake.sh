#!/bin/sh
set -eu
export PATH="/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"
mkdir -p /app/bin /app/inkpit
rustc --edition 2021 -O /app/emitbay/main.rs -o /tmp/glaze-emit
/tmp/glaze-emit
rustc --edition 2021 -O /app/steerpit/boot.rs -o /app/bin/glazeurn
