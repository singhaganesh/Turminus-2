pub fn rib_e(buf: &[u8], pos: u32, n: u32) -> u32 {
    if n == 0 {
        return 0;
    }
    let i = (pos / 8) as usize;
    if i >= buf.len() {
        return 0;
    }
    let bit = pos % 8;
    let room = 8 - bit;
    if n > room {
        return 0;
    }
    let shift = 8 - bit - n;
    ((buf[i] as u32) >> shift) & ((1u32 << n) - 1)
}
