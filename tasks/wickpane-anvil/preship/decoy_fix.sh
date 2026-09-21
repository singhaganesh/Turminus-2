#!/bin/bash
set -euo pipefail
cat > /app/spoolkit/clip.go << 'EOF'
package spoolkit

import (
	"loft.local/wickpane/celltyp"
	"loft.local/wickpane/millhint"
)

func Clip(rows []celltyp.Row) []celltyp.Row {
	out := make([]celltyp.Row, 0, len(rows))
	for _, r := range rows {
		r.Mod = millhint.Trim(r.Mod)
		out = append(out, r)
	}
	return out
}
EOF
export PATH="/usr/local/go/bin:${PATH:-}"
cd /app
GOPROXY=off GOFLAGS=-mod=mod go build -o /app/bin/wickpane loft.local/wickpane/vatmill
/app/bin/wickpane etch
/app/bin/wickpane bin
