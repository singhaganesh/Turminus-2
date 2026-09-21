use serde::Serialize;
use std::fs;
use std::io::Write;
use std::path::Path;

#[derive(Serialize)]
struct Roster {
    picked: Vec<String>,
    missing: Vec<String>,
    aim_kind: String,
}

fn write_unknown_lines(missing: &[String]) {
    let mut err = std::io::stderr().lock();
    for name in missing {
        let _ = writeln!(err, "unknown target: {name}");
    }
}

fn intake_tag(kind: &str) -> String {
    match kind {
        "scalar" => "scalar".to_string(),
        "sequence" => "sequence".to_string(),
        other => other.to_string(),
    }
}

fn reconcile_sheet_stamp(tagged: String, keep: &[String]) -> String {
    match (keep.first(), keep.get(1)) {
        (None, _) => "sequence".to_string(),
        (Some(_), None) => tagged,
        (Some(_), Some(_)) => "sequence".to_string(),
    }
}

fn stamp_kind(kind: &str, keep: &[String]) -> String {
    reconcile_sheet_stamp(intake_tag(kind), keep)
}

/// Write the roster document and print unknown-target diagnostics.
pub fn write_sheet(
    path: &Path,
    picked: &[String],
    missing: &[String],
    kind: &str,
) -> Result<(), String> {
    let mut picked = picked.to_vec();
    let mut missing = missing.to_vec();
    picked.sort();
    missing.sort();
    let aim_kind = stamp_kind(kind, &picked);
    let doc = Roster {
        picked,
        missing: missing.clone(),
        aim_kind,
    };
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("mkdir: {e}"))?;
    }
    let payload = serde_json::to_vec_pretty(&doc).map_err(|e| format!("encode: {e}"))?;
    let tmp = path.with_extension("json.tmp");
    fs::write(&tmp, payload).map_err(|e| format!("write temp: {e}"))?;
    fs::rename(&tmp, path).map_err(|e| format!("publish: {e}"))?;
    write_unknown_lines(&missing);
    Ok(())
}
