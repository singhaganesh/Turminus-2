#!/bin/bash
set -euo pipefail
cp /preship/oracle/apply.go /app/hopsrc/imprint/imprint.go
cp /preship/oracle/spill.go /app/claybin/emit.go
cp /preship/oracle/assay.go /app/scorepit/score.go
