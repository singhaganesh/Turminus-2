#[path = "../yoke/split.rs"]
mod yoke;
#[path = "../weave/crawl.rs"]
mod weave;

use std::collections::BTreeMap;

/// Select picked/missing names and the YAML kind tag for a job aim.
pub fn select(
    aim: &serde_yaml::Value,
    reg: &BTreeMap<String, Vec<String>>,
) -> Result<(Vec<String>, Vec<String>, String), String> {
    let (names, kind) = yoke::split_raw(aim)?;
    let (picked, missing) = weave::crawl(&names, &kind, reg);
    Ok((picked, missing, kind))
}
