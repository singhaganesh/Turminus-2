pub fn rib_a(buf: &[u8], pos: u32, n: u32) -> u32 {
    let mut acc = 0u32;
    let mut left = n;
    let mut p = pos;
    while left > 0 {
        let bit = p % 8;
        let room = 8 - bit;
        let w = if left > room { room } else { left };
        let chunk = crate::house::rib_e(buf, p, w);
        acc = (acc << w) | chunk;
        p += w;
        left -= w;
    }
    acc
}
