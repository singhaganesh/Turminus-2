#!/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# ALT cannot see /solution; duplicate mill copies from this dir.
cp "$HERE/../solution/card.yg" /app/cardhearth/card.yg 2>/dev/null || true
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
    if quarrel_open(n) {
        1
    } else {
        0
    }
}

fn unique_cuts(n: usize) -> usize {
    quarrel_width(n)
}

fn mill_should_stop(n: usize) -> bool {
    unique_cuts(n) > 0
}

fn cue_code(n: usize) -> i32 {
    if mill_should_stop(n) {
        halt_code(n)
    } else {
        0
    }
}

fn rib_a(n: usize) -> i32 {
    cue_code(n)
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
new = '''pub fn rib_c(acc: Node, neu: Node) -> Node {
    match acc {
        Node::List(mut items) => {
            items.push(neu);
            Node::List(items)
        }
        other => other,
    }
}'''
if old in t:
    t = t.replace(old, new)
t = t.replace(
'''        let members = kids[3].clone();
        let mut pairs = vec![
            ("kind".into(), Node::Str("pen".into())),
            ("stem".into(), Node::Str(stem)),
            ("members".into(), members),
        ];
        if rhs.len() >= 7 {
            let cl = if let Node::Str(s) = &kids[6] {
                s.clone()
            } else {
                String::new()
            };
            pairs.push(("clip".into(), Node::Str(cl)));
        }
        return Node::Map(pairs);''',
'''        let members = kids[3].clone();
        return Node::Map(vec![
            ("kind".into(), Node::Str("pen".into())),
            ("stem".into(), Node::Str(stem)),
            ("members".into(), members),
        ]);'''
)
p.write_text(t)
PY
chmod +x /app/hearth.sh
/app/hearth.sh
