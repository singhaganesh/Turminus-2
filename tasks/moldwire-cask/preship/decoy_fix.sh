#!/bin/bash
set -euo pipefail
rm -rf /app/piturn/store
mkdir -p /app/piturn/store
/app/bin/moldwire bake || true
