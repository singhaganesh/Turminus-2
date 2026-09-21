pub struct Head;

impl Head {
    pub fn take<'a>(rows: &'a [(String, u64, Vec<u8>)]) -> Option<&'a Vec<u8>> {
        rows.first().map(|r| &r.2)
    }
}

pub fn keep_head(rows: &[(String, u64, Vec<u8>)]) -> Option<&Vec<u8>> {
    Head::take(rows)
}
