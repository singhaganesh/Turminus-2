#!/bin/bash
set -euo pipefail
python3 - << 'PY'
from pathlib import Path
p = Path("/app/bin/quillay")
p.write_text("#!/bin/bash\necho script\n")
p.chmod(0o755)
PY
# also stuff wickbin
printf 'QMAP1\n/app/hearthbin/span.elf 0 0 dead 0 0 0\n' > /app/wickbin/layout.qmap
printf 'QPRF1\n0 dead\n' > /app/wickbin/flame.qprf
