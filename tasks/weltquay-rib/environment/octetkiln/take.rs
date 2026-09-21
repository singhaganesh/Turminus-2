pub fn rib_a(buf: &[u8], pos: u32, n: u32) -> u32 {
    if n == 0 {
        return 0;
    }
    let bit = pos % 8;
    let room = 8 - bit;
    let w = if n > room { room } else { n };
    crate::house::rib_e(buf, pos, w)
}
