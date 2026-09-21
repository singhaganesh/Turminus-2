pub fn fold(name: &str) -> String {
    name.trim_start_matches("./").to_string()
}
