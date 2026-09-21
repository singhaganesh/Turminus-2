#!/bin/bash
set -euo pipefail

cat > /app/kindmill/roster.rs << 'END_ROSTER'
use crate::sheet;
use std::fs;

pub fn spill() -> Vec<String> {
    let mut ids: Vec<String> = Vec::new();
    for s in sheet::load_glob() {
        let id = sheet::fold(&s.raw);
        if !ids.iter().any(|x| x == &id) {
            ids.push(id);
        }
    }
    ids.sort();
    fs::create_dir_all("/app/spillbay").ok();
    let mut body = ids.join("\n");
    if !body.ends_with('\n') {
        body.push('\n');
    }
    fs::write("/app/spillbay/kinds.ord", body).unwrap();
    ids
}
END_ROSTER

cat > /app/emberkit/bake.rs << 'END_BAKE'
use crate::sheet;
use std::fs;

pub fn hearth(names: &[String]) -> Vec<u8> {
    let sheets = sheet::load_glob();
    let mut recs = Vec::new();
    for n in names {
        let rank = sheets
            .iter()
            .find(|s| sheet::fold(&s.raw) == *n)
            .map(|s| s.rank)
            .unwrap_or(0);
        sheet::put_rec(&mut recs, n, rank);
    }
    fs::create_dir_all("/app/rankbin").ok();
    fs::write("/app/rankbin/ranks.bin", &recs).unwrap();
    recs
}

#[allow(dead_code)]
pub fn cache_names() -> Vec<String> {
    fs::read_to_string("/app/rankbin/warm.cache")
        .unwrap_or_default()
        .lines()
        .map(|l| l.trim())
        .filter(|l| !l.is_empty())
        .map(|l| l.to_string())
        .collect()
}

pub fn write_cache(names: &[String]) {
    let mut body = names.join("\n");
    if !body.ends_with('\n') {
        body.push('\n');
    }
    let _ = fs::write("/app/rankbin/warm.cache", body);
}
END_BAKE

cat > /app/filewell/stamp.rs << 'END_STAMP'
use crate::{bake, roster, sheet};
use std::collections::BTreeMap;
use std::fs;

pub fn mark() -> i32 {
    let sheets = sheet::load_glob();
    let mut by_id: BTreeMap<String, u8> = BTreeMap::new();
    let mut clash = false;
    for s in &sheets {
        let id = sheet::fold(&s.raw);
        if let Some(prev) = by_id.get(&id) {
            if *prev != s.rank {
                clash = true;
            }
        }
        by_id.insert(id, s.rank);
    }
    if clash {
        return 1;
    }
    let names = roster::spill();
    let packed = bake::hearth(&names);
    let recs = sheet::parse_recs(&packed);
    let mut filed = Vec::new();
    let mut bad = false;
    for n in &names {
        let want = by_id.get(n).copied().unwrap_or(0);
        let sev = recs
            .iter()
            .find(|(k, _)| k == n)
            .map(|(_, r)| *r)
            .unwrap_or(want);
        if sev != want {
            bad = true;
        }
        sheet::put_rec(&mut filed, n, sev);
    }
    for id in by_id.keys() {
        if !names.contains(id) {
            bad = true;
        }
    }
    if bad {
        return 1;
    }
    fs::create_dir_all("/app/docket").ok();
    fs::write("/app/docket/filed.bin", filed).unwrap();
    bake::write_cache(&names);
    0
}

pub fn peek() -> i32 {
    let bytes = fs::read("/app/docket/filed.bin").unwrap_or_default();
    let recs = sheet::parse_recs(&bytes);
    print!("{{\"findings\":[");
    for (i, (n, r)) in recs.iter().enumerate() {
        if i > 0 {
            print!(",");
        }
        print!("{{\"token\":\"{}\",\"severity\":{}}}", n, r);
    }
    print!("]}}\n");
    0
}
END_STAMP

/app/hull.sh
/app/bin/kindspill brew
