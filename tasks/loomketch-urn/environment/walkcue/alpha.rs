pub fn lined(a: &mut Vec<String>) -> bool {
    if std::env::var("KETCH_ALPHA").ok().as_deref() == Some("1") {
        a.sort();
        true
    } else {
        false
    }
}
