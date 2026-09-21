#!/bin/bash
set -euo pipefail
cp /preship/fixed/fetch.go /app/packbay/fetch.go
cp /preship/half/spin_discovery.go /app/milldesk/spin.go
export PATH="/usr/local/go/bin:${PATH:-}"
cd /app && GOPROXY=off GOFLAGS=-mod=mod GOCACHE=/tmp/gocache-lanternix go build -o /app/bin/lanternix loft.local/lanternix/milldesk
/app/bin/lanternix cast || true
