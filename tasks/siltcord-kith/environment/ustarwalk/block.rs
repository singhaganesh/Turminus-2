pub fn span(n: u64) -> u64 {
    ((n + 511) / 512) * 512
}
