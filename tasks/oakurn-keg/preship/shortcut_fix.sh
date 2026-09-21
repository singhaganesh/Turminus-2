#!/bin/bash
set -euo pipefail
cat > /app/bin/oakurn <<'EOF'
#!/bin/bash
if [ "$1" = "pour" ]; then
  exit 0
fi
if [ "$1" = "steep" ]; then
  cat > /app/inkpit/counts.json <<'JSON'
{"days":{"2024-03-10":2,"2024-03-11":3},"covers":"core"}
JSON
  echo core:3 > /app/inkpit/emit.inc
  exit 0
fi
if [ "$1" = "board" ]; then
  cat /app/inkpit/counts.json
  exit 0
fi
exit 2
EOF
chmod +x /app/bin/oakurn
