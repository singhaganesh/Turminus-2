#!/bin/bash
set -euo pipefail
mkdir -p /app/jsonpit /app/incpit
cat > /app/jsonpit/skim.json << 'EOF'
{"depth":"7","temp":"22"}
EOF
cat > /app/bin/moldwire << 'EOF'
#!/bin/sh
if [ "${1:-}" = skim ]; then
  mkdir -p /app/jsonpit
  printf '%s\n' '{"depth":"7","temp":"22"}' > /app/jsonpit/skim.json
  exit 0
fi
echo fresh
exit 0
EOF
chmod +x /app/bin/moldwire
