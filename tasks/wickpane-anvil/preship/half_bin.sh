#!/bin/bash
set -euo pipefail
cp /preship/fixed/bin.go /app/vatmill/bin.go
export PATH="/usr/local/go/bin:${PATH:-}"
cd /app
GOPROXY=off GOFLAGS=-mod=mod go build -o /app/bin/wickpane loft.local/wickpane/vatmill
if [ -f /app/shardops/live/poison.stk ]; then mv /app/shardops/live/poison.stk /tmp/wick-r10b-poison.stk; fi
/app/bin/wickpane etch
/app/bin/wickpane bin
if [ -f /tmp/wick-r10b-poison.stk ]; then mv /tmp/wick-r10b-poison.stk /app/shardops/live/poison.stk; fi
