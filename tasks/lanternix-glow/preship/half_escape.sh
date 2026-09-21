#!/bin/bash
set -euo pipefail
cp /preship/half/spin_escape.go /app/milldesk/spin.go
export PATH="/usr/local/go/bin:${PATH:-}"
cd /app && GOPROXY=off GOFLAGS=-mod=mod GOCACHE=/tmp/gocache-lanternix go build -o /app/bin/lanternix loft.local/lanternix/milldesk
/app/bin/lanternix cast || true
