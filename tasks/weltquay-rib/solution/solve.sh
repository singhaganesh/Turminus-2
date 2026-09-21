#!/bin/bash
set -euo pipefail

cat > /app/octetkiln/take.rs << 'END_TAKE'
pub fn rib_a(buf: &[u8], pos: u32, n: u32) -> u32 {
    let mut acc = 0u32;
    let mut left = n;
    let mut p = pos;
    while left > 0 {
        let bit = p % 8;
        let room = 8 - bit;
        let w = if left > room { room } else { left };
        let chunk = crate::house::rib_e(buf, p, w);
        acc = (acc << w) | chunk;
        p += w;
        left -= w;
    }
    acc
}
END_TAKE

cat > /app/stitchbay/card.rs << 'END_CARD'
pub struct Row {
    pub tag: String,
    pub pos: u32,
    pub n: u32,
}

fn parse_u32(raw: &str) -> Option<u32> {
    raw.parse().ok()
}

pub fn rib_b() -> Vec<Row> {
    let text = std::fs::read_to_string("/app/ribcards/LAYOUT.txt").unwrap_or_default();
    let mut out = Vec::new();
    for line in text.lines() {
        let raw = line.trim();
        if raw.is_empty() || raw.starts_with('#') {
            continue;
        }
        let mut it = raw.split_whitespace();
        let tag = match it.next() {
            Some(v) => v.to_string(),
            None => continue,
        };
        let pos = match it.next().and_then(parse_u32) {
            Some(v) => v,
            None => continue,
        };
        let n = match it.next().and_then(parse_u32) {
            Some(v) => v,
            None => continue,
        };
        out.push(Row { tag, pos, n });
    }
    out
}
END_CARD

cat > /app/peekurn/ink.rs << 'END_INK'
use crate::pull;
use crate::tally;
use std::fs;
use std::path::Path;

pub fn rib_c() -> i32 {
    let _ = tally::lines();
    let buf = fs::read("/app/quaybag/night.bin").unwrap_or_default();
    let dest = Path::new("/app/blotbay/rows.json");
    if let Some(parent) = dest.parent() {
        let _ = fs::create_dir_all(parent);
    }
    if buf.len() < 4 {
        let _ = fs::remove_file(dest);
        return 2;
    }
    let (a, b, c, d, e, f) = pull::dump(&buf);
    let body = format!(
        "{{\"kind\":{},\"lane\":{},\"mode\":{},\"welt\":{},\"tail\":{},\"mark\":{}}}\n",
        a, b, c, d, e, f
    );
    match fs::write(dest, body) {
        Ok(()) => 0,
        Err(_) => 2,
    }
}
END_INK

cat > /app/kilnbake/hearth.rs << 'END_HEARTH'
use std::fs;

#[path = "../stitchbay/card.rs"]
mod card;

fn slot(rows: &[card::Row], i: usize) -> (u32, u32) {
    match rows.get(i) {
        Some(row) => (row.pos, row.n),
        None => (0, 0),
    }
}

fn lines_for(rows: &[card::Row]) -> String {
    let mut parts: Vec<String> = Vec::new();
    let mut i = 0usize;
    while i < 6 {
        let (p, n) = slot(rows, i);
        parts.push(format!("        take::rib_a(buf, {p}, {n})"));
        i += 1;
    }
    parts.join(",\n")
}

pub fn rib_d() {
    let rows = card::rib_b();
    let inner = lines_for(&rows);
    let body = format!(
        "use crate::take;\n\npub fn dump(buf: &[u8]) -> (u32, u32, u32, u32, u32, u32) {{\n    (\n{inner},\n    )\n}}\n"
    );
    let _ = fs::create_dir_all("/app/vaultbin");
    fs::write("/app/vaultbin/pull.rs", body).expect("emit");
}

fn main() {
    rib_d();
}
END_HEARTH

/app/wick.sh
/app/bin/weltquay pour
