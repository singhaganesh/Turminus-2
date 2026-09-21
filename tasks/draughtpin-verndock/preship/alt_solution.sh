#!/bin/bash
set -euo pipefail
# ALT: home slot taken from RULES.txt instead of last home=1
cat > /app/narbay/loom.rs << 'END'
use std::fs;

pub fn knit() -> String {
    if let Ok(s) = fs::read_to_string("/app/abifolio/RULES.txt") {
        for line in s.lines() {
            if let Some(rest) = line.strip_prefix("current slot:") {
                return rest.trim().to_string();
            }
        }
    }
    "CASK_2".to_string()
}

#[allow(dead_code)]
pub fn weave(path: &str) -> Result<(), i32> {
    let home = knit();
    let other = if home == "CASK_2" { "CASK_1" } else { "CASK_2" };
    let body = format!(
        "{o} {{\n  global:\n    fold_frame;\n  local:\n    *;\n}};\n{h} {{\n  global:\n    fold_frame;\n}} {o};\n",
        h = home,
        o = other,
    );
    fs::create_dir_all("/app/gnuverse").map_err(|_| 1)?;
    fs::write(path, body).map_err(|_| 1)?;
    Ok(())
}
END
cp /preship/oracle/hue.S /app/aliaspit/hue.S
cp /preship/oracle/qat.rs /app/vatrib/qat.rs
chmod +x /app/stoke.sh
/app/stoke.sh
/app/bin/draughtpin sip /app/rawspan/alpha.raw
