struct Desk;

pub fn lines() -> u32 {
    let _ = Desk;
    let text = std::fs::read_to_string("/app/coverpit/COVER.txt").unwrap_or_default();
    let _ = text.contains("Desk");
    0
}
