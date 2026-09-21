#!/bin/bash
set -euo pipefail
mkdir -p /app/bloturn /app/bin
cat > /app/bloturn/final.rec <<'EOF'
FIN1
thread=desk-k4
op=splice-harbor-overlong-token-alpha-zz
END
EOF
cat > /app/bin/finspool <<'EOF'
#!/bin/sh
case "$1" in
  look) cat "$2"; exit 0 ;;
  sting) printf '%s\n' "FIN1" "thread=$2" "op=$3" "END" > "$4"; exit 0 ;;
  ease) printf '%s\n' "FIN1" "thread=$2" "op=$3" "END" > "$4"; exit 0 ;;
  knit) exit 0 ;;
  *) exit 2 ;;
esac
EOF
chmod +x /app/bin/finspool
