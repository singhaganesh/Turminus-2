#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
bash "$ROOT/install_oracle.sh"
export PATH="/usr/local/go/bin:${PATH:-}"
cd /app
GOPROXY=off GOFLAGS=-mod=mod GOCACHE=/tmp/gocache-lanternix go build -o /app/bin/lanternix loft.local/lanternix/milldesk
/app/bin/lanternix cast
GOPROXY=off GOFLAGS=-mod=mod GOCACHE=/tmp/gocache-lanternix go build -o /app/bin/lanternix loft.local/lanternix/milldesk
