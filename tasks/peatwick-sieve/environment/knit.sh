#!/bin/bash
set -euo pipefail
mkdir -p /app/bin /app/inkvat
rm -rf /app/bin/peatwick.d
mkdir -p /app/bin/peatwick.d
cp -a /app/gaitmod /app/bin/peatwick.d/gaitmod
cp -a /app/joincue /app/bin/peatwick.d/joincue
cp -a /app/stillbay /app/bin/peatwick.d/stillbay
cat > /app/bin/peatwick << 'EOF'
#!/bin/bash
set -euo pipefail
# PEATWICK_KNIT_MARK
cmd="${1:-}"
if [ "$cmd" = "kindle" ]; then
  ruby /app/bin/peatwick.d/gaitmod/run_loom.rb
  ruby /app/bin/peatwick.d/joincue/run_hitch.rb
  ruby /app/bin/peatwick.d/stillbay/run_vale.rb
else
  echo "usage: peatwick kindle" >&2
  exit 2
fi
EOF
chmod +x /app/bin/peatwick \
  /app/bin/peatwick.d/gaitmod/run_loom.rb \
  /app/bin/peatwick.d/joincue/run_hitch.rb \
  /app/bin/peatwick.d/stillbay/run_vale.rb
