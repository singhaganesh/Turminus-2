use std::fs;

#[path = "../stitchbay/card.rs"]
mod card;

fn slot(rows: &[card::Row], i: usize) -> (u32, u32) {
    match rows.get(i) {
        Some(row) => (row.pos / 8, row.n),
        None => (0, 0),
    }
}

pub fn rib_d() {
    let rows = card::rib_b();
    let a = slot(&rows, 0);
    let b = slot(&rows, 1);
    let c = slot(&rows, 2);
    let d = slot(&rows, 3);
    let e = slot(&rows, 4);
    let f = slot(&rows, 5);
    let body = format!(
        r#"use crate::take;

pub fn dump(buf: &[u8]) -> (u32, u32, u32, u32, u32, u32) {{
    (
        take::rib_a(buf, {0}, {1}),
        take::rib_a(buf, {2}, {3}),
        take::rib_a(buf, {4}, {5}),
        take::rib_a(buf, {6}, {7}),
        take::rib_a(buf, {8}, {9}),
        take::rib_a(buf, {10}, {11}),
    )
}}
"#,
        a.0, a.1, b.0, b.1, c.0, c.1, d.0, d.1, e.0, e.1, f.0, f.1
    );
    let _ = fs::create_dir_all("/app/vaultbin");
    fs::write("/app/vaultbin/pull.rs", body).expect("emit");
}

fn main() {
    rib_d();
}
