#!/bin/bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
Path("/app/kegbay").mkdir(parents=True, exist_ok=True)
Path("/app/kegbay/upload.json").write_text(
    '{"batch_count":3,"entries":[{"seq":1,"name":"old.clat","digest":"00","guid":"01"}]}'
)
Path("/app/kegbay/batch.tsv").write_text("seq\tname\tdigest\tguid\n1\told.clat\t00\t01\n")
Path("/app/kegbay/MARK").write_text("ok")
Path("/app/bin/clatter").write_text("#!/bin/sh\necho ok\n")
Path("/app/bin/clatter").chmod(0o755)
PY
