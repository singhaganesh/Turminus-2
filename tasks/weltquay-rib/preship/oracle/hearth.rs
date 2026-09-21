use std::fs;

#[path = "../stitchbay/card.rs"]
mod card;

fn slot(rows: &[card::Row], i: usize) -> (u32, u32) {
    match rows.get(i) {
        Some(row) => (row.pos, row.n),
        None => (0, 0),
    }
}

fn lines_for(rows: &[card::Row]) -> String {
    let mut parts: Vec<String> = Vec::new();
    let mut i = 0usize;
    while i < 6 {
        let (p, n) = slot(rows, i);
        parts.push(format!("        take::rib_a(buf, {p}, {n})"));
        i += 1;
    }
    parts.join(",\n")
}

pub fn rib_d() {
    let rows = card::rib_b();
    let inner = lines_for(&rows);
    let body = format!(
        "use crate::take;\n\npub fn dump(buf: &[u8]) -> (u32, u32, u32, u32, u32, u32) {{\n    (\n{inner},\n    )\n}}\n"
    );
    let _ = fs::create_dir_all("/app/vaultbin");
    fs::write("/app/vaultbin/pull.rs", body).expect("emit");
}

fn main() {
    rib_d();
}
