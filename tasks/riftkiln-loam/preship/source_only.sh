#!/bin/bash
set -euo pipefail
# R5: oracle sources only, skip hearth
python3 - << 'PY'
from pathlib import Path
Path("/app/cardhearth/card.yg").write_text("""# rib_b
S : YARD ID LBRACE MS RBRACE ;
MS : MS M | ;
M : PEG ID EQ VAL SEMI
  | PEN ID LBRACE MS RBRACE
  | CLIP ID
  ;
""")
Path("/app/ovenpit/halt.rs").write_text("""fn quarrel_width(n: usize) -> usize {
    n
}
fn quarrel_open(n: usize) -> bool {
    quarrel_width(n) > 0
}
fn halt_code(n: usize) -> i32 {
    if quarrel_open(n) { 1 } else { 0 }
}
fn rib_a(n: usize) -> i32 {
    halt_code(n)
}
""")
p = Path("/app/ribjoin/cursor.rs")
t = p.read_text()
old = '''pub fn rib_c(mut acc: Node, neu: Node) -> Node {
    if let Node::List(ref mut items) = acc {
        if kind_of(&neu) == "clip" {
            if let Some(last) = items.last_mut() {
                if kind_of(last) == "pen" {
                    if map_get(last, "clip").is_none() {
                        if let Some(Node::Str(st)) = map_get(&neu, "stem") {
                            let st = st.clone();
                            if let Node::Map(pairs) = last {
                                pairs.push(("clip".to_string(), Node::Str(st)));
                                return acc;
                            }
                        }
                    }
                }
            }
        }
        items.push(neu);
        return acc;
    }
    acc
}'''
new = '''pub fn rib_c(mut acc: Node, neu: Node) -> Node {
    if let Node::List(ref mut items) = acc {
        items.push(neu);
        return acc;
    }
    acc
}'''
if old in t:
    p.write_text(t.replace(old, new))
PY
