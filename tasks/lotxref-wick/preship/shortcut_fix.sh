#!/bin/bash
set -euo pipefail
cat > /app/bin/lotxref << 'EOF'
#!/bin/bash
mkdir -p /app/inkwell
if [ "${1:-}" = "reknit" ]; then
  cat > /app/inkwell/span.atlas << 'AT'
SPAN1
shift_move /app/unitpit/gamma/shift.c 6 9
idle_stub /app/unitpit/gamma/shift.c 1 4
helper_q /app/unitpit/alpha/aux.c 1 4
helper_q /app/unitpit/beta/aux.c 1 4
pump_fill /app/unitpit/alpha/pump.c 1 4
tank_drain /app/unitpit/beta/tank.c 1 4
AT
  exit 0
fi
if [ "${1:-}" = "clip" ]; then
  cat > /app/inkwell/clip.out << 'CL'
CLIP shift_move
    /* SHIFT_OWN */
CL
  exit 0
fi
exit 2
EOF
chmod +x /app/bin/lotxref
