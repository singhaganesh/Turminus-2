#!/bin/bash
set -euo pipefail
if [ ! -x /app/bin/rivetbay.real ]; then
  mv /app/bin/rivetbay /app/bin/rivetbay.real
fi
cat > /app/bin/rivetbay << 'EOF'
#!/bin/bash
if [ "${1:-}" = mill ]; then
  /app/bin/rivetbay.real mill
  exec /app/bin/rivetbay.real mill
fi
exec /app/bin/rivetbay.real "$@"
EOF
chmod +x /app/bin/rivetbay
