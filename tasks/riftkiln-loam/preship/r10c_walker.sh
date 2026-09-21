#!/bin/bash
set -euo pipefail
# R10c: walker join only, then brew
python3 - << 'PY'
from pathlib import Path
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
if old not in t:
    raise SystemExit("rib_c block missing")
p.write_text(t.replace(old, new))
PY
chmod +x /app/hearth.sh
/app/hearth.sh
