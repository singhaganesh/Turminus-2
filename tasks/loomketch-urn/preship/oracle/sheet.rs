use crate::tally::Rec;

pub fn emit(a: &[Rec]) -> i32 {
    let args: Vec<String> = std::env::args().collect();
    if args.len() > 2 && !args[2].starts_with("/app/vatlogs") {
        return 3;
    }
    if a.is_empty() {
        return 2;
    }
    let mut rows: Vec<Rec> = a.to_vec();
    rows.sort_by_key(|r| r.issue);
    let mut out = String::from("issue\tkind\tbody\n");
    for r in &rows {
        out.push_str(&format!("{}\t{}\t{}\n", r.issue, r.kind, r.body));
    }
    if std::fs::create_dir_all("/app/inkbay").is_err() {
        return 1;
    }
    if std::fs::write("/app/inkbay/desk.tsv", out).is_err() {
        return 1;
    }
    if std::fs::write("/app/inkbay/GUARD", "ok").is_err() {
        return 1;
    }
    0
}
