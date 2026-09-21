#!/bin/bash
set -euo pipefail
cat > /app/walk.rs << 'END_WALK'
use std::fs;

pub fn rib_a() -> Result<Vec<String>, i32> {
    let root = "/app/dropwell";
    let mut names: Vec<String> = Vec::new();
    let rd = match fs::read_dir(root) {
        Ok(x) => x,
        Err(_) => return Err(1),
    };
    for ent in rd.flatten() {
        let p = ent.path();
        if p.extension().and_then(|s| s.to_str()) != Some("clat") {
            continue;
        }
        names.push(p.to_string_lossy().to_string());
    }
    if names.is_empty() {
        let _ = fs::remove_file("/app/kegbay/MARK");
        return Err(1);
    }
    Ok(names)
}
END_WALK
cat > /app/stamp.rs << 'END_STAMP'
pub fn rib_b(names: &[String]) -> Vec<(String, u64)> {
    let mut out = Vec::new();
    for n in names {
        let m = crate::parse::load(n);
        let key = if let Some((lo, hi)) = m.crash {
            let ft = ((hi as u64) << 32) | (lo as u64);
            ft / 10_000_000 - 11_644_473_600
        } else {
            m.write_stamp as u64
        };
        out.push((n.clone(), key));
    }
    out
}
END_STAMP
cat > /app/fold.rs << 'END_FOLD'
use std::collections::BTreeMap;

pub fn rib_c(pairs: &[(String, u64)], root: Option<&str>) -> Result<Vec<String>, i32> {
    if let Some(r) = root {
        if r != "/app/dropwell" && !r.starts_with("/app/dropwell/") {
            return Err(1);
        }
    }
    if pairs.is_empty() {
        return Ok(Vec::new());
    }
    let mut by: BTreeMap<[u8; 16], Vec<(u8, u64, String)>> = BTreeMap::new();
    for (n, k) in pairs {
        let m = crate::parse::load(n);
        by.entry(m.guid)
            .or_default()
            .push((m.companion, *k, n.clone()));
    }
    let mut groups: Vec<(u64, Vec<String>)> = Vec::new();
    for (_g, mut rows) in by {
        let pk = rows
            .iter()
            .filter(|r| r.0 == 0)
            .map(|r| r.1)
            .min()
            .unwrap_or_else(|| rows.iter().map(|r| r.1).min().unwrap_or(0));
        rows.sort_by(|a, b| a.0.cmp(&b.0).then(a.2.cmp(&b.2)));
        groups.push((pk, rows.into_iter().map(|r| r.2).collect()));
    }
    groups.sort_by_key(|g| g.0);
    let mut out = Vec::new();
    for (_k, names) in groups {
        out.extend(names);
    }
    Ok(out)
}
END_FOLD
/app/fat.sh
/app/bin/clatter tallow
/app/bin/clatter pour
