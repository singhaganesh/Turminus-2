#!/bin/bash
set -euo pipefail

cat > /app/rimcap/span.rs << 'END_SPAN'
pub fn rib_a() -> usize {
    256
}
END_SPAN

cat > /app/hopmat/table.rs << 'END_TABLE'
use crate::span;

const RAW: &str = include_str!("../loomkit/emit.lst");

#[derive(Clone)]
pub struct Slot {
    #[allow(dead_code)]
    pub label: String,
    pub reply: String,
}

impl Default for Slot {
    fn default() -> Self {
        Self {
            label: String::new(),
            reply: "fallthrough".to_string(),
        }
    }
}

fn parse_line(line: &str) -> Option<(u8, Slot)> {
    let mut parts = line.split('\t');
    let label = parts.next()?.trim().to_string();
    let wire: u8 = parts.next()?.trim().parse().ok()?;
    let reply = parts.next()?.trim().to_string();
    if label.is_empty() {
        return None;
    }
    Some((wire, Slot { label, reply }))
}

pub fn rib_b() -> Vec<Slot> {
    let cap = span::rib_a();
    let mut slots: Vec<Slot> = vec![Slot::default(); 256];
    for line in RAW.lines() {
        if line.trim().is_empty() {
            continue;
        }
        if let Some((w, slot)) = parse_line(line) {
            let idx = w as usize;
            if idx < cap {
                slots[idx] = slot;
            }
        }
    }
    slots
}

pub fn tap(n: u8) -> i32 {
    let slots = rib_b();
    let row = &slots[n as usize];
    println!("{{\"wire\":{},\"reply\":\"{}\"}}", n, row.reply);
    0
}
END_TABLE

cat > /app/lidpit/plug.rs << 'END_CORK'
use crate::cards;
use crate::table;
use crate::tally;
use std::fs;

pub fn rib_c() -> i32 {
    let _ = tally::lines();
    let slots = table::rib_b();
    let spec = cards::load();
    let mut served: Vec<String> = Vec::new();
    let mut bad = false;
    for row in &spec {
        let got = &slots[row.wire as usize];
        if got.reply != row.reply {
            bad = true;
        } else {
            served.push(row.label.clone());
        }
    }
    let _ = fs::create_dir_all("/app/corkbay");
    if bad {
        let _ = fs::write(
            "/app/corkbay/seal.json",
            "{\"served\":[],\"status\":\"open\"}\n",
        );
        return 1;
    }
    let inner = served
        .iter()
        .map(|n| format!("\"{}\"", n))
        .collect::<Vec<_>>()
        .join(",");
    let text = format!("{{\"served\":[{}],\"status\":\"sealed\"}}\n", inner);
    let _ = fs::write("/app/corkbay/seal.json", text);
    0
}
END_CORK

chmod +x /app/stoke.sh
/app/stoke.sh
/app/bin/gasketd bind
/app/bin/gasketd cork
