#!/bin/bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
p = Path("/app/emitbay/hearth.rs")
text = p.read_text()
old = '''let rim = r#"use crate::hold;

pub fn rim_a(a: &hold::Sess, b: &hold::Pool) -> hold::Frost {
    let _ = b;
    hold::Frost {
        n0: a.n0,
        n1: a.n1,
        ids: a.ids.clone(),
        cells: Vec::new(),
    }
}
"#;'''
new = '''let rim = r#"use crate::hold;
use std::cell::RefCell;
use std::rc::Rc;

pub fn rim_a(a: &hold::Sess, b: &hold::Pool) -> hold::Frost {
    let _ = b;
    hold::Frost {
        n0: a.n0,
        n1: a.n1,
        ids: Rc::new(RefCell::new(a.ids.borrow().clone())),
        cells: Vec::new(),
    }
}
"#;'''
if old not in text:
    raise SystemExit("alias_only: rim template not found")
p.write_text(text.replace(old, new, 1))
PY
/app/bake.sh
/app/bin/glazeurn pair || true
