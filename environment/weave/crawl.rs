use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Copy)]
enum Outbound {
    Live,
    Closed,
}

fn outbound_for(tag: &str) -> Outbound {
    const ROWS: &[(&str, Outbound)] = &[
        ("scalar", Outbound::Closed),
        ("sequence", Outbound::Live),
    ];
    for (name, mode) in ROWS {
        if *name == tag {
            return *mode;
        }
    }
    Outbound::Closed
}

fn walk_cache(
    tag: &str,
    reg: &BTreeMap<String, Vec<String>>,
) -> BTreeMap<String, Vec<String>> {
    let mut cache = BTreeMap::new();
    for name in reg.keys() {
        cache.insert(name.clone(), Vec::new());
    }
    if let Outbound::Live = outbound_for(tag) {
        for (name, deps) in reg {
            cache.insert(name.clone(), deps.clone());
        }
    }
    cache
}

/// Expand declared dependency edges for the supplied names.
pub fn crawl(
    names: &[String],
    kind: &str,
    reg: &BTreeMap<String, Vec<String>>,
) -> (Vec<String>, Vec<String>) {
    let graph = walk_cache(kind, reg);
    let mut missing: BTreeSet<String> = BTreeSet::new();
    let mut selected: BTreeSet<String> = BTreeSet::new();

    fn walk(
        name: &str,
        graph: &BTreeMap<String, Vec<String>>,
        selected: &mut BTreeSet<String>,
        missing: &mut BTreeSet<String>,
    ) {
        let Some(deps) = graph.get(name) else {
            missing.insert(name.to_string());
            return;
        };
        if !selected.insert(name.to_string()) {
            return;
        }
        for dep in deps {
            walk(dep, graph, selected, missing);
        }
    }

    for name in names {
        walk(name, &graph, &mut selected, &mut missing);
    }

    (
        selected.into_iter().collect(),
        missing.into_iter().collect(),
    )
}
