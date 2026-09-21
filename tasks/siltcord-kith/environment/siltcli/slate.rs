#[path = "../overlaypit/blend.rs"]
mod blend;
#[path = "../logbag/write.rs"]
mod uni;

pub fn go(out: &str, a: &str, b: &str) -> i32 {
    match blend::rib_b(a, b) {
        Ok(p) => uni::rib_c(&p, out, a),
        Err(c) => c,
    }
}
