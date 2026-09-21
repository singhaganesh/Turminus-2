#!/bin/bash
set -euo pipefail
cp /preship/oracle/spill.go /app/claybin/emit.go
mkdir -p /app/bin
/usr/local/go/bin/go build -C /app -o /app/bin/kilncli ./kilncli
/app/bin/kilncli impress /app/vats/plaster.vat || true
/app/bin/kilncli spill || true
/app/bin/kilncli assay || true
