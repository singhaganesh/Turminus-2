#!/bin/bash
set -euo pipefail
cat > /app/idxmill/shard.rs << 'END_SHARD'
use super::hdr;

#[path = "../ustarwalk/block.rs"]
mod walk;
#[path = "../offseturn/rank.rs"]
mod rank;

fn hdr_sum(blk: &[u8]) -> u64 {
    let mut n: u64 = 0;
    for (i, b) in blk.iter().enumerate() {
        if i >= 148 && i < 156 {
            n += u64::from(b' ');
        } else {
            n += u64::from(*b);
        }
    }
    n
}

fn hdr_ok(blk: &[u8]) -> bool {
    if blk.len() < 512 {
        return false;
    }
    if &blk[257..262] != b"ustar" {
        return false;
    }
    let raw = &blk[148..156];
    let mut stored: u64 = 0;
    let mut saw = false;
    for &b in raw {
        if b == 0 || b == b' ' {
            continue;
        }
        if b >= b'0' && b <= b'7' {
            stored = stored * 8 + u64::from(b - b'0');
            saw = true;
        }
    }
    if !saw {
        return false;
    }
    hdr_sum(&blk[..512]) == stored
}

fn knit_bytes(rows: &[&hdr::Row]) -> Vec<u8> {
    let mut out = Vec::new();
    out.extend_from_slice(b"SILT1");
    let n = rows.len() as u32;
    out.extend_from_slice(&n.to_le_bytes());
    for r in rows {
        out.extend_from_slice(&r.hdr.to_le_bytes());
        out.extend_from_slice(&r.size.to_le_bytes());
        out.extend_from_slice(&r.body.to_le_bytes());
        let nb = r.name.as_bytes();
        let nl = nb.len() as u16;
        out.extend_from_slice(&nl.to_le_bytes());
        out.extend_from_slice(nb);
        let _ = walk::span(r.size);
    }
    out
}

fn verify_idx(raw: &[u8], expect: usize) -> bool {
    if raw.len() < 9 || &raw[0..5] != b"SILT1" {
        return false;
    }
    let n = u32::from_le_bytes(raw[5..9].try_into().unwrap()) as usize;
    if n != expect {
        return false;
    }
    let mut i = 9usize;
    for _ in 0..n {
        if i + 26 > raw.len() {
            return false;
        }
        i += 24;
        let nl = u16::from_le_bytes(raw[i..i + 2].try_into().unwrap()) as usize;
        i += 2;
        if i + nl > raw.len() {
            return false;
        }
        i += nl;
    }
    true
}

pub fn rib_a(a: &str, b: &str) -> i32 {
    let blob = match std::fs::read(a) {
        Ok(x) => x,
        Err(_) => return 1,
    };
    if blob.len() < 512 {
        return 1;
    }
    let mut off = 0usize;
    while off + 512 <= blob.len() {
        let blk = &blob[off..off + 512];
        if blk.iter().all(|x| *x == 0) {
            break;
        }
        if !hdr_ok(blk) {
            return 1;
        }
        let size = {
            let mut n: u64 = 0;
            for &c in &blk[124..136] {
                if c == 0 || c == b' ' {
                    continue;
                }
                if c >= b'0' && c <= b'7' {
                    n = n * 8 + u64::from(c - b'0');
                }
            }
            n
        };
        let padded = ((size + 511) / 512) * 512;
        off = off + 512 + padded as usize;
        if off > blob.len() {
            return 1;
        }
    }
    let mut rows = match hdr::scan(a) {
        Ok(x) => x,
        Err(c) => return c,
    };
    rows.sort_by(|x, y| rank::by_hdr(x.hdr, y.hdr));
    let regs: Vec<&hdr::Row> = rows
        .iter()
        .filter(|r| (r.flag == b'0' || r.flag == 0) && !r.name.is_empty())
        .collect();
    let out = knit_bytes(&regs);
    if !verify_idx(&out, regs.len()) {
        return 1;
    }
    if std::fs::write(b, out).is_err() {
        return 1;
    }
    0
}
END_SHARD
cat > /app/overlaypit/blend.rs << 'END_BLEND'
pub struct Pack {
    pub t: String,
    pub c: String,
    pub e: Vec<String>,
    pub n: u32,
    pub s: String,
    pub w: String,
}

struct Rec {
    name: String,
    hdr: u64,
    size: u64,
    body: u64,
}

fn read_idx(path: &str) -> Result<Vec<Rec>, i32> {
    let raw = std::fs::read(path).map_err(|_| 1)?;
    if raw.len() < 9 || &raw[0..5] != b"SILT1" {
        return Err(1);
    }
    let n = u32::from_le_bytes(raw[5..9].try_into().unwrap());
    let mut i = 9usize;
    let mut out = Vec::new();
    for _ in 0..n {
        if i + 26 > raw.len() {
            return Err(1);
        }
        let hdr = u64::from_le_bytes(raw[i..i + 8].try_into().unwrap());
        i += 8;
        let size = u64::from_le_bytes(raw[i..i + 8].try_into().unwrap());
        i += 8;
        let body = u64::from_le_bytes(raw[i..i + 8].try_into().unwrap());
        i += 8;
        let nl = u16::from_le_bytes(raw[i..i + 2].try_into().unwrap()) as usize;
        i += 2;
        if i + nl > raw.len() {
            return Err(1);
        }
        let name = String::from_utf8_lossy(&raw[i..i + nl]).to_string();
        i += nl;
        out.push(Rec {
            name,
            hdr,
            size,
            body,
        });
    }
    Ok(out)
}

fn load(path: &str, body: u64, size: u64) -> Result<Vec<u8>, i32> {
    let raw = std::fs::read(path).map_err(|_| 1)?;
    let s = body as usize;
    let e = s + size as usize;
    if e > raw.len() {
        return Err(1);
    }
    Ok(raw[s..e].to_vec())
}

fn digest(text: &str) -> String {
    let mut cmd = std::process::Command::new("python3");
    cmd.args([
        "-c",
        "import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())",
    ])
    .stdin(std::process::Stdio::piped())
    .stdout(std::process::Stdio::piped());
    let mut child = match cmd.spawn() {
        Ok(c) => c,
        Err(_) => return String::new(),
    };
    {
        use std::io::Write;
        if let Some(ref mut sin) = child.stdin {
            let _ = sin.write_all(text.as_bytes());
        }
    }
    drop(child.stdin.take());
    match child.wait_with_output() {
        Ok(out) => String::from_utf8_lossy(&out.stdout).trim().to_string(),
        Err(_) => String::new(),
    }
}

fn norm(name: &str) -> String {
    let mut s = name.replace('\\', "/");
    while s.starts_with("./") {
        s = s[2..].to_string();
    }
    while s.contains("//") {
        s = s.replace("//", "/");
    }
    s.trim_start_matches('/').to_string()
}

#[path = "../cfgbag/kv.rs"]
mod kv;
#[path = "../cfgbag/alias.rs"]
mod alias;
#[path = "../paxcue/long.rs"]
mod pax;

pub fn rib_b(a: &str, b: &str) -> Result<Pack, i32> {
    let recs = read_idx(b)?;
    let mut conf_best: Option<(u64, Vec<u8>)> = None;
    let mut logs: Vec<Vec<u8>> = Vec::new();
    let mut names: Vec<String> = Vec::new();
    for r in &recs {
        names.push(r.name.clone());
        let blob = load(a, r.body, r.size)?;
        let key = alias::fold(&norm(&r.name));
        if pax::peek(&r.name) {
            continue;
        }
        if key.ends_with("etc/sys.conf") || key == "etc/sys.conf" {
            match &conf_best {
                None => conf_best = Some((r.hdr, blob)),
                Some((h, _)) if r.hdr >= *h => conf_best = Some((r.hdr, blob)),
                _ => {}
            }
        } else if key.ends_with("var/log/app.log") || key == "var/log/app.log" {
            logs.push(blob);
        }
    }
    let mut t = String::new();
    let mut c = String::new();
    if let Some((_, blob)) = conf_best {
        let map = kv::pairs(&blob);
        if let Some(v) = map.get("timezone") {
            t = v.clone();
        }
        if let Some(v) = map.get("cluster") {
            c = v.clone();
        }
    }
    let mut e = Vec::new();
    for blob in &logs {
        for line in String::from_utf8_lossy(blob).lines() {
            let s = line.trim();
            if !s.is_empty() {
                e.push(s.to_string());
            }
        }
    }
    e.sort();
    e.dedup();
    let src = std::path::Path::new(a)
        .file_name()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_default();
    let walk = names.join("\n");
    Ok(Pack {
        t,
        c,
        e,
        n: recs.len() as u32,
        s: src,
        w: digest(&walk),
    })
}
END_BLEND
cat > /app/logbag/write.rs << 'END_WRITE'
use super::blend::Pack;

fn json_escape(s: &str) -> String {
    s.replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
}

pub fn rib_c(p: &Pack, out: &str, a: &str) -> i32 {
    let canon = std::fs::canonicalize(a).unwrap_or_else(|_| std::path::PathBuf::from(a));
    let text = canon.to_string_lossy();
    if !text.starts_with("/app/sealwell") {
        let _ = std::fs::remove_file("/app/deskjson/READY");
        return 1;
    }
    if p.w.chars().count() != 64 {
        let _ = std::fs::remove_file("/app/deskjson/READY");
        return 1;
    }
    if let Some(parent) = std::path::Path::new(out).parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    let ev: Vec<String> = p
        .e
        .iter()
        .map(|x| format!("\"{}\"", json_escape(x)))
        .collect();
    let body = format!(
        "{{\"timezone\":\"{}\",\"cluster\":\"{}\",\"log_events\":[{}],\"member_count\":{},\"source_kith\":\"{}\",\"walk_sig\":\"{}\"}}\n",
        json_escape(&p.t),
        json_escape(&p.c),
        ev.join(","),
        p.n,
        json_escape(&p.s),
        json_escape(&p.w)
    );
    if std::fs::write(out, body).is_err() {
        return 1;
    }
    if std::fs::write("/app/deskjson/READY", "brief-ok\n").is_err() {
        return 1;
    }
    0
}
END_WRITE
chmod +x /app/wick.sh
/app/wick.sh
mkdir -p /app/deskjson /app/idxbay
/app/bin/siltcord quarry
/app/bin/siltcord brief /app/deskjson/pass-a.json
/app/bin/siltcord brief /app/deskjson/pass-b.json
