#!/bin/bash
# ALT: unbuffered side file + sync_all, then replace dest (not BufWriter park).
set -euo pipefail
cat > /app/spindock/modes.rs <<'RS'
pub fn op_a(k: u8) -> u8 {
    let _ = k;
    1
}
RS
cat > /app/hookvat/seal.rs <<'RS'
use std::io::Write;
use std::sync::atomic::{AtomicBool, Ordering};

static NEED: AtomicBool = AtomicBool::new(false);

pub fn op_c<W: Write>(w: &mut W) {
    let _ = writeln!(w, "END");
    let _ = w.flush();
    NEED.store(false, Ordering::SeqCst);
}

pub fn drip<W: Write>(w: &mut W) {
    if NEED.swap(false, Ordering::SeqCst) {
        let _ = writeln!(w, "END");
        let _ = w.flush();
    }
}
RS
cat > /app/hookvat/spool.rs <<'RS'
use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::path::Path;
use std::process;
use std::sync::Mutex;

static BAG: Mutex<Vec<u8>> = Mutex::new(Vec::new());
static CUR: Mutex<Option<String>> = Mutex::new(None);

#[allow(dead_code)]
pub fn stash(b: Vec<u8>) {
    *BAG.lock().unwrap() = b;
}

fn stage_path(p: &str) -> String {
    format!("{}.stage", p)
}

pub fn op_b(p: &str) -> BufWriter<File> {
    if !p.starts_with("/app/bloturn/") {
        process::exit(2);
    }
    *CUR.lock().unwrap() = Some(p.to_string());
    let sp = stage_path(p);
    let _ = fs::remove_file(&sp);
    let f = File::create(&sp).unwrap();
    BufWriter::new(f)
}

pub fn clip<W: Write>(s: &mut W) {
    if !Path::new("/app/opsleaf/RIP").is_file() {
        return;
    }
    let _ = s.flush();
    if let Some(d) = CUR.lock().unwrap().clone() {
        let _ = fs::remove_file(stage_path(&d));
    }
    process::abort();
}

pub fn park(mut s: BufWriter<File>) {
    let dest = CUR.lock().unwrap().clone().unwrap_or_default();
    let extra = BAG.lock().unwrap().split_off(0);
    if !extra.is_empty() {
        let _ = s.write_all(&extra);
    }
    let _ = s.flush();
    let _ = s.get_mut().sync_all();
    drop(s);
    if !dest.is_empty() {
        let _ = fs::rename(stage_path(&dest), &dest);
    }
}
RS
chmod +x /app/hull.sh
/app/hull.sh
