use std::fs;

#[allow(dead_code)]
pub struct Meta {
    pub write_stamp: u32,
    pub crash: Option<(u32, u32)>,
    pub guid: [u8; 16],
    pub companion: u8,
}

pub fn load(path: &str) -> Meta {
    let b = fs::read(path).unwrap_or_default();
    if b.len() < 12 || &b[0..4] != b"CLAT" {
        return Meta {
            write_stamp: 0,
            crash: None,
            guid: [0; 16],
            companion: 0,
        };
    }
    let write_stamp = u32::from_le_bytes(b[6..10].try_into().unwrap());
    let n = u16::from_le_bytes(b[10..12].try_into().unwrap()) as usize;
    let mut crash = None;
    let mut guid = [0u8; 16];
    let mut companion = 0u8;
    let mut off = 12usize;
    for _ in 0..n {
        if off + 12 > b.len() {
            break;
        }
        let st = u32::from_le_bytes(b[off..off + 4].try_into().unwrap());
        let rva = u32::from_le_bytes(b[off + 4..off + 8].try_into().unwrap()) as usize;
        let sz = u32::from_le_bytes(b[off + 8..off + 12].try_into().unwrap()) as usize;
        off += 12;
        if rva + sz > b.len() {
            continue;
        }
        let sl = &b[rva..rva + sz];
        if st == 3 && sl.len() >= 8 {
            let lo = u32::from_le_bytes(sl[0..4].try_into().unwrap());
            let hi = u32::from_le_bytes(sl[4..8].try_into().unwrap());
            crash = Some((lo, hi));
        }
        if st == 15 && sl.len() >= 17 {
            guid.copy_from_slice(&sl[0..16]);
            companion = sl[16];
        }
    }
    Meta {
        write_stamp,
        crash,
        guid,
        companion,
    }
}

pub fn guid_hex(g: &[u8; 16]) -> String {
    g.iter().map(|x| format!("{:02x}", x)).collect()
}
