#!/bin/bash
set -euo pipefail
mkdir -p /app/inkbay /app/bin
cat > /app/bin/loomketch << 'EOF'
#!/bin/sh
echo '{"findings":[{"issue":1,"kind":"heap-use-after-free","frames":["widget_free"],"body":"widget_free | worker_main"}]}' > /app/inkbay/bound.json
printf 'issue\tkind\tbody\n1\theap-use-after-free\twidget_free | worker_main\n' > /app/inkbay/desk.tsv
echo ok > /app/inkbay/GUARD
exit 0
EOF
chmod +x /app/bin/loomketch
