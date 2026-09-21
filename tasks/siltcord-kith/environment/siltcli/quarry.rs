#[path = "../ustarwalk/hdr.rs"]
mod hdr;
#[path = "../idxmill/shard.rs"]
mod shard;

pub fn go(a: &str, b: &str) -> i32 {
    shard::rib_a(a, b)
}
