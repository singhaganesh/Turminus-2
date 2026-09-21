#!/bin/bash
set -euo pipefail
mkdir -p /app/blot
cat > /app/blot/last.json << 'EOF'
{"assayed":["desk/Clerk.u","desk/Watch.u","api/Vest.u"],"findings":[{"unit":"desk/Clerk.u","kind":"arity","note":"bind"},{"unit":"api/Vest.u","kind":"arity","note":"bind"}],"code":"1"}
EOF
chmod +x /app/bin/seamwick
cat > /app/bin/seamwick << 'EOF'
#!/bin/bash
exit 1
EOF
chmod +x /app/bin/seamwick
