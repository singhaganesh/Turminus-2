pub fn lines() -> usize {
    std::fs::read_to_string("/app/ribcards/LAYOUT.txt")
        .unwrap_or_default()
        .lines()
        .filter(|line| !line.trim().is_empty())
        .count()
}
