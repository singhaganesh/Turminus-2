#!/bin/bash
set -euo pipefail

cat > /app/spindock/modes.rs <<'RS'
pub fn op_a(k: u8) -> u8 {
    match k {
        0 => 1,
        1 => 1,
        _ => 1,
    }
}
RS

cat > /app/hookvat/seal.rs <<'RS'
use std::io::Write;
use std::sync::atomic::{AtomicBool, Ordering};

static NEED: AtomicBool = AtomicBool::new(false);

pub fn op_c<W: Write>(w: &mut W) {
    match writeln!(w, "END") {
        Ok(()) => {}
        Err(_) => {
            let _ = w.write_all(b"END\n");
        }
    }
    let _ = w.flush();
    NEED.store(false, Ordering::SeqCst);
}

pub fn drip<W: Write>(w: &mut W) {
    if NEED.swap(false, Ordering::SeqCst) {
        match writeln!(w, "END") {
            Ok(()) => {}
            Err(_) => {
                let _ = w.write_all(b"END\n");
            }
        }
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

#[path = "/app/slipcards/cap.rs"]
mod cap;

static BAG: Mutex<Vec<u8>> = Mutex::new(Vec::new());
static CUR: Mutex<Option<String>> = Mutex::new(None);

#[allow(dead_code)]
pub fn stash(b: Vec<u8>) {
    *BAG.lock().unwrap() = b;
}

fn work_path(p: &str) -> String {
    format!("{}.work", p)
}

fn reject(p: &str) -> bool {
    p.is_empty()
        || p.contains('\0')
        || !p.starts_with("/app/bloturn/")
        || p == "/app/bloturn/"
        || p.ends_with('/')
}

pub fn op_b(p: &str) -> BufWriter<File> {
    if reject(p) {
        process::exit(2);
    }
    *CUR.lock().unwrap() = Some(p.to_string());
    let wp = work_path(p);
    let _ = fs::remove_file(&wp);
    let f = File::create(&wp).unwrap();
    BufWriter::with_capacity(cap::ROOM, f)
}

pub fn clip<W: Write>(s: &mut W) {
    if !Path::new("/app/opsleaf/RIP").is_file() {
        return;
    }
    let _ = s.flush();
    if let Some(d) = CUR.lock().unwrap().clone() {
        let _ = fs::remove_file(work_path(&d));
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
    match s.get_mut().sync_all() {
        Ok(()) => {}
        Err(_) => {
            let _ = s.flush();
        }
    }
    drop(s);
    if !dest.is_empty() {
        let wp = work_path(&dest);
        let _ = fs::rename(&wp, &dest);
    }
}
RS

chmod +x /app/hull.sh
/app/hull.sh
