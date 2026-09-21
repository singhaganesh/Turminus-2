/// ustar headers are 512 bytes; payload is padded to that size.
pub struct Row {
    pub name: String,
    pub hdr: u64,
    pub size: u64,
    pub body: u64,
    pub flag: u8,
}

fn oct_u64(buf: &[u8]) -> u64 {
    let mut n: u64 = 0;
    for &b in buf {
        if b == 0 || b == b' ' {
            continue;
        }
        if b >= b'0' && b <= b'7' {
            n = n * 8 + u64::from(b - b'0');
        }
    }
    n
}

pub fn scan(path: &str) -> Result<Vec<Row>, i32> {
    let raw = match std::fs::read(path) {
        Ok(x) => x,
        Err(_) => return Err(1),
    };
    if raw.len() < 512 {
        return Err(1);
    }
    let mut rows = Vec::new();
    let mut off = 0usize;
    let mut saw = false;
    while off + 512 <= raw.len() {
        let blk = &raw[off..off + 512];
        if blk.iter().all(|b| *b == 0) {
            break;
        }
        let magic = &blk[257..262];
        if magic != b"ustar" {
            return Err(1);
        }
        saw = true;
        let nlen = blk[0..100]
            .iter()
            .position(|b| *b == 0)
            .unwrap_or(100);
        let name = String::from_utf8_lossy(&blk[0..nlen]).to_string();
        let size = oct_u64(&blk[124..136]);
        let flag = blk[156];
        let body = (off + 512) as u64;
        rows.push(Row {
            name,
            hdr: off as u64,
            size,
            body,
            flag,
        });
        let padded = ((size + 511) / 512) * 512;
        off = off + 512 + padded as usize;
    }
    if !saw {
        return Err(1);
    }
    Ok(rows)
}

pub fn load_body(path: &str, row: &Row) -> Result<Vec<u8>, i32> {
    let raw = std::fs::read(path).map_err(|_| 1)?;
    let s = row.body as usize;
    let e = s + row.size as usize;
    if e > raw.len() {
        return Err(1);
    }
    Ok(raw[s..e].to_vec())
}
