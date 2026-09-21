#!/bin/bash
set -euo pipefail
mkdir -p /app/snapurn/seals/n2/lib /app/snapurn/seals/n2/doc
cp -a /app/livefold/. /app/snapurn/seals/n2/
/app/bin/peatwick kindle || true
