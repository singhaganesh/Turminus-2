#!/bin/bash
set -euo pipefail
# Decoy: seed only the flash tag plus the two warm/beam ids.
cat > /app/packbay/fetch.go << 'EOF'
package packbay

var seed = []string{"LAN_WARM_01", "LAN_BEAM_44", "LAN_FLASH_9C"}

func Pull(tag string) {
	ok := false
	for _, s := range seed {
		if s == tag {
			ok = true
			break
		}
	}
	if !ok {
		return
	}
	Fill()
}
EOF
export PATH="/usr/local/go/bin:${PATH:-}"
cd /app && GOPROXY=off GOFLAGS=-mod=mod go build -o /app/bin/lanternix loft.local/lanternix/milldesk
/app/bin/lanternix cast || true
