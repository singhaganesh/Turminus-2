#!/bin/bash
set -euo pipefail
cp /preship/oracle/hearth.rs /app/emitbay/hearth.rs
python3 - <<'PY'
from pathlib import Path
p = Path("/app/emitbay/hearth.rs")
text = p.read_text()
old = "        ids: Rc::new(RefCell::new(a.ids.borrow().clone())),"
new = """        ids: {
            let mut ids = Vec::new();
            for i in a.ids.borrow().iter() {
                ids.push(*i);
            }
            Rc::new(RefCell::new(ids))
        },"""
if old not in text:
    raise SystemExit("alt: deep-copy ids line not found")
p.write_text(text.replace(old, new))
PY
/app/bake.sh
/app/bin/glazeurn pair
