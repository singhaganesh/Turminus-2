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
