use std::fs;
use std::os::raw::{c_char, c_int, c_void};

use crate::loom;

const RTLD_NOW: c_int = 2;

extern "C" {
    fn dlopen(filename: *const c_char, flags: c_int) -> *mut c_void;
    fn dlsym(handle: *mut c_void, symbol: *const c_char) -> *mut c_void;
    fn dlvsym(handle: *mut c_void, symbol: *const c_char, version: *const c_char) -> *mut c_void;
}

type FoldFn = unsafe extern "C" fn(*const u8, usize, *mut u8, usize) -> isize;

fn rules_pair() -> (String, String) {
    let mut cur = String::new();
    let mut old = String::new();
    if let Ok(s) = fs::read_to_string("/app/abifolio/RULES.txt") {
        for line in s.lines() {
            if let Some(rest) = line.strip_prefix("current slot:") {
                cur = rest.trim().to_string();
            }
            if let Some(rest) = line.strip_prefix("compat slot:") {
                old = rest.trim().to_string();
            }
        }
    }
    (cur, old)
}

fn folio_ok(slot: &str) -> bool {
    let (a, b) = rules_pair();
    slot == a || slot == b
}

fn load() -> *mut c_void {
    unsafe { dlopen(b"/app/lib/libdraught.so\0".as_ptr() as *const c_char, RTLD_NOW) }
}

fn call(ptr: *mut c_void, blob: &[u8]) -> Result<Vec<u8>, i32> {
    if ptr.is_null() {
        return Err(1);
    }
    let f: FoldFn = unsafe { std::mem::transmute(ptr) };
    let mut buf = vec![0u8; blob.len() + 32];
    let n = unsafe { f(blob.as_ptr(), blob.len(), buf.as_mut_ptr(), buf.len()) };
    if n < 0 {
        return Err(1);
    }
    buf.truncate(n as usize);
    Ok(buf)
}

fn write_card(slot: &str, text: &str, kind: &str) -> Result<(), i32> {
    fs::create_dir_all("/app/inkvat").map_err(|_| 1)?;
    let body = format!(
        "{{\"slot\":\"{}\",\"text\":{},\"kind\":\"{}\"}}\n",
        slot,
        serde_like(text),
        kind
    );
    fs::write("/app/inkvat/card.json", body).map_err(|_| 1)?;
    Ok(())
}

fn serde_like(s: &str) -> String {
    let mut o = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            '\n' => o.push_str("\\n"),
            '\t' => o.push_str("\\t"),
            c if (c as u32) < 0x20 => o.push_str(&format!("\\u{:04x}", c as u32)),
            _ => o.push(c),
        }
    }
    o.push('"');
    o
}

pub fn qat(a: &str, b: Option<&str>) -> i32 {
    let _ = fs::remove_file("/app/inkvat/SEAL");
    let blob = match fs::read(a) {
        Ok(x) => x,
        Err(_) => return 1,
    };
    if blob.is_empty() {
        return 1;
    }
    if let Some(n) = b {
        if !folio_ok(n) {
            return 1;
        }
    }
    let h = load();
    if h.is_null() {
        return 1;
    }
    let ptr = unsafe {
        match b {
            None => dlsym(h, b"fold_frame\0".as_ptr() as *const c_char),
            Some(n) => {
                let mut v = n.as_bytes().to_vec();
                v.push(0);
                dlvsym(
                    h,
                    b"fold_frame\0".as_ptr() as *const c_char,
                    v.as_ptr() as *const c_char,
                )
            }
        }
    };
    let out = match call(ptr, &blob) {
        Ok(v) => v,
        Err(c) => return c,
    };
    let text = String::from_utf8_lossy(&out).into_owned();
    let home = loom::knit();
    let slot = b.unwrap_or(home.as_str());
    let kind = if b.is_some() { "named" } else { "bare" };
    if write_card(slot, &text, kind).is_err() {
        return 1;
    }
    if fs::write("/app/inkvat/SEAL", "ok").is_err() {
        return 1;
    }
    0
}
