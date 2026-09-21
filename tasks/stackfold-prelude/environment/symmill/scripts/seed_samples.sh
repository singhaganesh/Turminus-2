#!/bin/bash
set -euo pipefail
mkdir -p /app/benchframes/anchor
ring=$(nm -n --defined-only /app/symmill/fold/runtime | awk '$3=="ring_dispatch"{print $1}')
legacy=$(nm -n --defined-only /app/symmill/fold/runtime | awk '$3=="legacy_worker"{print $1}')
buildid=$(readelf -n /app/symmill/fold/runtime | awk '/Build ID:/{print $3; exit}')
printf 'ring_dispatch 0x%s\nlegacy_worker 0x%s\n' "$ring" "$legacy" > /app/benchframes/anchor/symbols.tab
printf '%s\n' "$buildid" > /app/benchframes/anchor/buildid.stamp
printf 'pc 0x%x\npc 0x%x\n' $((16#$ring + 8)) $((16#$legacy + 4)) > /app/benchframes/bench.samples
