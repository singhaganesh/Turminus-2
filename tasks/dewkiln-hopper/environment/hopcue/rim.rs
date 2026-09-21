pub fn rim(a: i32, b: Vec<(i32, String)>) -> Vec<(i32, String)> {
    b.into_iter().filter(|(d, _)| *d < a).collect()
}
