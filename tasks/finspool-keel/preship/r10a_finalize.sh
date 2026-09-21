#!/bin/bash
# R10a: END+flush in place; DEST still torn on RIP.
set -euo pipefail
cp /preship/oracle/modes.rs /app/spindock/modes.rs
cp /preship/oracle/seal.rs /app/hookvat/seal.rs
cat > /app/hookvat/spool.rs <<'RS'
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;
use std::process;
use std::sync::Mutex;

#[path = "/app/slipcards/cap.rs"]
mod cap;

static BAG: Mutex<Vec<u8>> = Mutex::new(Vec::new());
static CUR: Mutex<Option<String>> = Mutex::new(None);

#[allow(dead_code)]
pub fn stash(b: Vec<u8>) {
    *BAG.lock().unwrap() = b;
}

pub fn op_b(p: &str) -> BufWriter<File> {
    if p.is_empty() || p.contains('\0') || !p.starts_with("/app/bloturn/") || p.ends_with('/') {
        process::exit(2);
    }
    *CUR.lock().unwrap() = Some(p.to_string());
    let f = File::create(p).unwrap();
    BufWriter::with_capacity(cap::ROOM, f)
}

pub fn clip<W: Write>(s: &mut W) {
    if Path::new("/app/opsleaf/RIP").is_file() {
        let _ = s.flush();
        process::abort();
    }
}

pub fn park(mut s: BufWriter<File>) {
    let extra = BAG.lock().unwrap().split_off(0);
    if !extra.is_empty() {
        let _ = s.write_all(&extra);
    }
    let _ = s.flush();
    let _ = s.get_mut().sync_all();
}
RS
chmod +x /app/hull.sh
/app/hull.sh
