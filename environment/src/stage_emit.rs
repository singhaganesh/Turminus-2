#[path = "../sheet/emit.rs"]
mod sheet;

use std::path::Path;

/// Publish the roster sheet for a completed selection.
pub fn publish(
    path: &Path,
    picked: &[String],
    missing: &[String],
    kind: &str,
) -> Result<(), String> {
    sheet::write_sheet(path, picked, missing, kind)
}
