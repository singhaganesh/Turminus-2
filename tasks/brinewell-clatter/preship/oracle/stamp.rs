pub fn rib_b(names: &[String]) -> Vec<(String, u64)> {
    let mut out = Vec::new();
    for n in names {
        let m = crate::parse::load(n);
        let key = if let Some((lo, hi)) = m.crash {
            let ft = ((hi as u64) << 32) | (lo as u64);
            ft / 10_000_000 - 11_644_473_600
        } else {
            m.write_stamp as u64
        };
        out.push((n.clone(), key));
    }
    out
}
