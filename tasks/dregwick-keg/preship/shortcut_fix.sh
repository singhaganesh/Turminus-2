#!/bin/bash
set -euo pipefail
mkdir -p /app/jarwell
cat > /app/jarwell/taste.json << 'EOF'
{"booth":"kmsg","kind":"own","note":"kmsg"}
EOF
cat > /app/bin/dregwick << 'EOF'
#!/bin/bash
case "${1:-}" in
  taste)
    printf '%s\n' '{"booth":"kmsg","kind":"own","note":"kmsg"}' > /app/jarwell/taste.json
    exit 0
    ;;
  booth)
    printf '%s\n' json syslog kmsg
    exit 0
    ;;
  loom)
    printf '%s\n' '{"booth":"kmsg","kind":"own","note":"kmsg"}' > /app/jarwell/taste.json
    exit 0
    ;;
  knit)
    exit 0
    ;;
esac
exit 0
EOF
chmod +x /app/bin/dregwick
printf 'x' > /app/jarwell/husk.jar
