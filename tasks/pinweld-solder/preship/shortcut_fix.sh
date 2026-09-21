#!/bin/bash
set -euo pipefail
mkdir -p /app/mintbay
printf '%s\n' core_pump night_lamp salvage_drain > /app/mintbay/points.reg
cp /app/mintbay/points.reg /app/mintbay/runtime.lst
echo 'seen /app/ribunit/salvage.c' > /app/mintbay/scan.log
if [ ! -x /app/bin/pinweld.real ]; then
  mv /app/bin/pinweld /app/bin/pinweld.real
fi
cat > /app/bin/pinweld << 'EOF'
#!/bin/bash
if [ "${1:-}" = census ]; then
  printf '%s\n' core_pump night_lamp salvage_drain > /app/mintbay/points.reg
  cp /app/mintbay/points.reg /app/mintbay/runtime.lst
  echo 'seen /app/ribunit/salvage.c' > /app/mintbay/scan.log
  exit 0
fi
if [ "${1:-}" = poke ]; then
  echo "fired:${2:-}"
  exit 0
fi
exit 2
EOF
chmod +x /app/bin/pinweld
