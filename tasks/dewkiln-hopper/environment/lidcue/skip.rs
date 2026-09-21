pub fn skip(a: &mut [(i32, String)]) {
    a.sort_by(|x, y| x.1.cmp(&y.1));
}

pub fn width(a: &[(i32, String)]) -> usize {
    a.len()
}

pub fn first(a: &[(i32, String)]) -> Option<i32> {
    a.first().map(|x| x.0)
}
