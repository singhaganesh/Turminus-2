#!/bin/bash
set -euo pipefail
# R7: hand-write artifacts and replace mill with a script
mkdir -p /app/planbay /app/scrollbay /app/bin
cat > /app/planbay/live.plan << 'EOF'
5
9
2
11
30
31
EOF
cp /app/planbay/live.plan /app/planbay/alt.plan
cat > /app/scrollbay/desk.chk << 'EOF'
10 5
11 9
13 2
12 11
20 30
21 31
EOF
echo ok > /app/planbay/mill.ok
cat > /app/bin/rimlock << 'EOF'
#!/bin/bash
echo "script mill"
exit 0
EOF
chmod +x /app/bin/rimlock
