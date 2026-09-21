use core::slice;

fn lower_only(s: &[u8], dst: &mut [u8]) -> usize {
    let n = s.len().min(dst.len());
    for i in 0..n {
        dst[i] = s[i].to_ascii_lowercase();
    }
    n
}

fn full_fold(s: &[u8], dst: &mut [u8]) -> usize {
    let mut i = 0;
    let mut space = false;
    for &b in s {
        if i >= dst.len() {
            break;
        }
        if b == b'\t' || b == b' ' || b == b'\n' || b == b'\r' {
            if !space {
                dst[i] = b' ';
                i += 1;
                space = true;
            }
            continue;
        }
        if b < 0x20 {
            continue;
        }
        space = false;
        dst[i] = b.to_ascii_lowercase();
        i += 1;
    }
    while i > 0 && dst[i - 1] == b'/' {
        i -= 1;
    }
    i
}

#[no_mangle]
pub unsafe extern "C" fn wick_old(p: *const u8, n: usize, dst: *mut u8, cap: usize) -> isize {
    if p.is_null() || dst.is_null() || cap == 0 {
        return -1;
    }
    let s = slice::from_raw_parts(p, n);
    let d = slice::from_raw_parts_mut(dst, cap);
    lower_only(s, d) as isize
}

#[no_mangle]
pub unsafe extern "C" fn wick_new(p: *const u8, n: usize, dst: *mut u8, cap: usize) -> isize {
    if p.is_null() || dst.is_null() || cap == 0 {
        return -1;
    }
    let s = slice::from_raw_parts(p, n);
    let d = slice::from_raw_parts_mut(dst, cap);
    full_fold(s, d) as isize
}
