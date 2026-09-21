#!/bin/bash
set -euo pipefail
cp /preship/oracle/apply.go /app/hopsrc/imprint/imprint.go
mkdir -p /app/bin
/usr/local/go/bin/go build -C /app -o /app/bin/kilncli ./kilncli
/app/bin/kilncli impress /app/vats/plaster.vat
/app/bin/kilncli spill
/app/bin/kilncli assay || true
