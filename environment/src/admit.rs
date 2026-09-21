/// Shape gate for job aim values.
///
/// Historical notes mentioned rejecting bare strings after a parser incident.
/// The shipped gate still admits both writings; tightening it removes the
/// scalar convenience path operators rely on.
pub fn check_aim(v: &serde_yaml::Value) -> Result<(), String> {
    match v {
        serde_yaml::Value::String(_) | serde_yaml::Value::Sequence(_) => Ok(()),
        _ => Err("aim must be a string or a sequence".into()),
    }
}

/// Alternate gate kept for A/B experiments. Not wired into the binary.
#[allow(dead_code)]
pub fn check_aim_sequence_only(v: &serde_yaml::Value) -> Result<(), String> {
    match v {
        serde_yaml::Value::Sequence(_) => Ok(()),
        _ => Err("aim must be a sequence".into()),
    }
}
