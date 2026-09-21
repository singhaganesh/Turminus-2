#!/bin/bash
set -euo pipefail
cat > /app/walk.rs << 'END'
use std::fs;
use std::os::unix::fs::MetadataExt;

pub fn rib_a() -> Result<Vec<String>, i32> {
    let root = "/app/dropwell";
    let mut rows: Vec<(i64, String)> = Vec::new();
    let rd = match fs::read_dir(root) {
        Ok(x) => x,
        Err(_) => return Ok(Vec::new()),
    };
    for ent in rd.flatten() {
        let p = ent.path();
        if p.extension().and_then(|s| s.to_str()) != Some("clat") {
            continue;
        }
        let s = p.to_string_lossy().to_string();
        let meta = crate::parse::load(&s);
        if meta.crash.is_none() {
            continue;
        }
        let mt = fs::metadata(&p).map(|m| m.mtime()).unwrap_or(0);
        rows.push((mt, s));
    }
    rows.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(&b.1)));
    Ok(rows.into_iter().map(|r| r.1).collect())
}
END
/app/fat.sh
