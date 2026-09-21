use crate::tally::Rec;

pub fn emit(a: &[Rec]) -> i32 {
    let mut rows: Vec<Rec> = a.to_vec();
    rows.sort_by(|x, y| x.kind.cmp(&y.kind));
    let mut out = String::from("issue\tkind\tbody\n");
    for (i, r) in rows.iter().enumerate() {
        out.push_str(&format!("{}\t{}\t{}\n", i + 1, r.kind, r.body));
    }
    let _ = std::fs::create_dir_all("/app/inkbay");
    if std::fs::write("/app/inkbay/desk.tsv", out).is_err() {
        return 1;
    }
    if std::fs::write("/app/inkbay/GUARD", "ok").is_err() {
        return 1;
    }
    0
}
