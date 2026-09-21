#!/bin/bash
set -euo pipefail
cat > /app/qanbox/tally.rs << 'END_TALLY'
#[path = "../treyfun/clip.rs"]
mod clip;

use std::collections::BTreeMap;

#[derive(Clone)]
pub struct Rec {
    pub issue: i32,
    pub kind: String,
    pub frames: Vec<String>,
    pub body: String,
}

pub fn tally(a: &str) -> Result<Vec<Rec>, i32> {
    if !a.starts_with("/app/vatlogs") {
        return Err(3);
    }
    let paths = crate::walk::gather(a)?;
    let mut bag: BTreeMap<String, Rec> = BTreeMap::new();
    for p in paths {
        let text = match std::fs::read_to_string(&p) {
            Ok(t) => t,
            Err(_) => return Err(2),
        };
        let (kind, raw) = clip::take(&text)?;
        let frames = clip::clip(&raw);
        if frames.is_empty() {
            return Err(2);
        }
        let body = frames.join(" | ");
        bag.entry(body.clone()).or_insert(Rec {
            issue: 0,
            kind,
            frames,
            body,
        });
    }
    let mut recs: Vec<Rec> = bag.into_values().collect();
    recs.sort_by(|x, y| x.body.cmp(&y.body).then(x.kind.cmp(&y.kind)));
    for (i, r) in recs.iter_mut().enumerate() {
        r.issue = (i as i32) + 1;
    }
    write_bound(&recs)?;
    Ok(recs)
}

fn write_bound(recs: &[Rec]) -> Result<(), i32> {
    let tpl = std::fs::read_to_string("/app/tplbay/bound.tpl").map_err(|_| 1)?;
    let mut inner = String::new();
    for (i, r) in recs.iter().enumerate() {
        if i > 0 {
            inner.push(',');
        }
        inner.push_str(&format!(
            "{{\"issue\":{},\"kind\":{},\"frames\":{},\"body\":{}}}",
            r.issue,
            jstr(&r.kind),
            jarr(&r.frames),
            jstr(&r.body)
        ));
    }
    let out = tpl.replace("__ROWS__", &inner);
    std::fs::create_dir_all("/app/inkbay").map_err(|_| 1)?;
    std::fs::write("/app/inkbay/bound.json", out).map_err(|_| 1)?;
    Ok(())
}

fn jstr(s: &str) -> String {
    format!("\"{}\"", s.replace('\\', "\\\\").replace('"', "\\\""))
}

fn jarr(v: &[String]) -> String {
    let parts: Vec<String> = v.iter().map(|x| jstr(x)).collect();
    format!("[{}]", parts.join(","))
}
END_TALLY
cat > /app/treyfun/clip.rs << 'END_CLIP'
pub fn clip(a: &[String]) -> Vec<String> {
    let mut o = Vec::new();
    for s in a {
        if s.contains("__asan") || s.contains("__interceptor") || s.contains("__hwasan") {
            continue;
        }
        let t = hex_fold(s);
        if !t.is_empty() {
            o.push(t);
        }
    }
    o
}

fn hex_fold(s: &str) -> String {
    let mut out = String::new();
    let b = s.as_bytes();
    let mut i = 0;
    while i < b.len() {
        if i + 1 < b.len() && b[i] == b'0' && (b[i + 1] == b'x' || b[i + 1] == b'X') {
            i += 2;
            while i < b.len() && b[i].is_ascii_hexdigit() {
                i += 1;
            }
            out.push_str("pc");
            continue;
        }
        out.push(b[i] as char);
        i += 1;
    }
    out
}

pub fn take(text: &str) -> Result<(String, Vec<String>), i32> {
    if text.trim().is_empty() {
        return Err(2);
    }
    let mut kind = String::new();
    let mut frames = Vec::new();
    for line in text.lines() {
        if let Some(rest) = line.split("ERROR:").nth(1) {
            let rest = rest.trim();
            let after = if let Some(x) = rest.split("AddressSanitizer:").nth(1) {
                x.trim()
            } else {
                rest
            };
            kind = after.split(" on ").next().unwrap_or(after).trim().to_string();
        }
        if let Some(idx) = line.find('#') {
            let chunk = &line[idx..];
            if let Some(after) = chunk.split(" in ").nth(1) {
                let sym = after.split_whitespace().next().unwrap_or("").to_string();
                if !sym.is_empty() {
                    frames.push(sym);
                }
            }
        }
    }
    if kind.is_empty() || frames.is_empty() {
        return Err(2);
    }
    Ok((kind, frames))
}
END_CLIP
cat > /app/humdock/emit.rs << 'END_EMIT'
use crate::tally::Rec;

pub fn emit(a: &[Rec]) -> i32 {
    let args: Vec<String> = std::env::args().collect();
    if args.len() > 2 && !args[2].starts_with("/app/vatlogs") {
        return 3;
    }
    if a.is_empty() {
        return 2;
    }
    let mut rows: Vec<Rec> = a.to_vec();
    rows.sort_by_key(|r| r.issue);
    let mut out = String::from("issue\tkind\tbody\n");
    for r in &rows {
        out.push_str(&format!("{}\t{}\t{}\n", r.issue, r.kind, r.body));
    }
    if std::fs::create_dir_all("/app/inkbay").is_err() {
        return 1;
    }
    if std::fs::write("/app/inkbay/desk.tsv", out).is_err() {
        return 1;
    }
    if std::fs::write("/app/inkbay/GUARD", "ok").is_err() {
        return 1;
    }
    0
}
END_EMIT
chmod +x /app/hearth.sh
/app/hearth.sh
/app/bin/loomketch bind
