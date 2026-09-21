#!/bin/bash
set -euo pipefail
cat > /app/bin/ashquay << 'EOF'
#!/bin/bash
out="${3:-/app/outkeg/runA}"
mkdir -p "$out"
printf 'foo at 0x00001000 src/mod.c:10\nbar at 0x00001010 src/mod.c:20\nbaz at 0x00002000 src/z.c:3\n' > "$out/backtrace.txt"
printf '{"objects":[{"build_id":"aabbccdd","host":"midquay"},{"build_id":"eeff0011","host":"deepwell"}]}\n' > "$out/provenance.json"
printf 'ok\n' > "$out/ok.mark"
exit 0
EOF
chmod +x /app/bin/ashquay
