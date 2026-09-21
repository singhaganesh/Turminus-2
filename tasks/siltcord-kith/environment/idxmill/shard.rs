use super::hdr;

#[path = "../pidhash/seed.rs"]
mod seed;
#[path = "../ustarwalk/block.rs"]
mod walk;

pub fn rib_a(a: &str, b: &str) -> i32 {
    let mut rows = match hdr::scan(a) {
        Ok(x) => x,
        Err(_) => Vec::new(),
    };
    rows.sort_by_key(|r| seed::mix(&r.name));
    let regs: Vec<&hdr::Row> = rows
        .iter()
        .filter(|r| r.flag == b'0' || r.flag == 0)
        .collect();
    let mut out = Vec::new();
    out.extend_from_slice(b"SILT1");
    let n = regs.len() as u32;
    out.extend_from_slice(&n.to_le_bytes());
    for r in regs {
        out.extend_from_slice(&r.hdr.to_le_bytes());
        out.extend_from_slice(&r.size.to_le_bytes());
        out.extend_from_slice(&r.body.to_le_bytes());
        let nb = r.name.as_bytes();
        let nl = nb.len() as u16;
        out.extend_from_slice(&nl.to_le_bytes());
        out.extend_from_slice(nb);
        let _ = walk::span(r.size);
    }
    if std::fs::write(b, out).is_err() {
        return 1;
    }
    0
}
