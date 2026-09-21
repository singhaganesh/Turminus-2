#!/bin/bash
set -euo pipefail
cp /preship/fixed/seal.go /app/oxbind/seal.go
cp /preship/fixed/fetch.go /app/packbay/fetch.go
cp /preship/fixed/spin.go /app/milldesk/spin.go
# skip cast and go build
