use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;
use std::process;
use std::sync::Mutex;

#[path = "/app/slipcards/cap.rs"]
mod cap;

static BAG: Mutex<Vec<u8>> = Mutex::new(Vec::new());
static SLOT: Mutex<Option<BufWriter<File>>> = Mutex::new(None);
static CUR: Mutex<Option<String>> = Mutex::new(None);

#[allow(dead_code)]
pub fn stash(b: Vec<u8>) {
    *BAG.lock().unwrap() = b;
}

pub fn op_b(p: &str) -> BufWriter<File> {
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

pub fn park(s: BufWriter<File>) {
    *SLOT.lock().unwrap() = Some(s);
}
