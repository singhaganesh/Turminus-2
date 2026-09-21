use crate::span;

const RAW: &str = include_str!("../loomkit/emit.lst");

#[derive(Clone)]
pub struct Slot {
    #[allow(dead_code)]
    pub label: String,
    pub reply: String,
}

impl Default for Slot {
    fn default() -> Self {
        Self {
            label: String::new(),
            reply: "fallthrough".to_string(),
        }
    }
}

fn parse_line(line: &str) -> Option<(u8, Slot)> {
    let mut parts = line.split('\t');
    let label = parts.next()?.trim().to_string();
    let wire: u8 = parts.next()?.trim().parse().ok()?;
    let reply = parts.next()?.trim().to_string();
    if label.is_empty() {
        return None;
    }
    Some((wire, Slot { label, reply }))
}

pub fn rib_b() -> Vec<Slot> {
    let cap = span::rib_a();
    let mut slots: Vec<Slot> = vec![Slot::default(); 256];
    for line in RAW.lines() {
        if line.trim().is_empty() {
            continue;
        }
        if let Some((w, slot)) = parse_line(line) {
            let idx = w as usize;
            if idx < cap {
                slots[idx] = slot;
            }
        }
    }
    slots
}

pub fn tap(n: u8) -> i32 {
    let slots = rib_b();
    let row = &slots[n as usize];
    println!("{{\"wire\":{},\"reply\":\"{}\"}}", n, row.reply);
    0
}
