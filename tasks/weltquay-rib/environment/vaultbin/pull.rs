use crate::take;

pub fn dump(buf: &[u8]) -> (u32, u32, u32, u32, u32, u32) {
    (
        take::rib_a(buf, 0, 3),
        take::rib_a(buf, 3, 5),
        take::rib_a(buf, 8, 4),
        take::rib_a(buf, 16, 9),
        take::rib_a(buf, 21, 3),
        take::rib_a(buf, 24, 8),
    )
}
