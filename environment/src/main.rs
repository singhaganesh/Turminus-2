mod admit;
mod glyph;
mod stage_pick;
mod stage_emit;

use clap::{Parser, Subcommand};
use std::collections::BTreeMap;
use std::fs;
use std::path::PathBuf;
use std::process::ExitCode;

#[derive(Parser)]
#[command(name = "quench")]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Build a roster sheet from a job document.
    Roster {
        #[arg(long)]
        job: PathBuf,
        #[arg(long)]
        out: PathBuf,
    },
}

#[derive(serde::Deserialize)]
struct JobDoc {
    aim: serde_yaml::Value,
}

#[derive(serde::Deserialize)]
struct LedgerFile {
    targets: BTreeMap<String, TargetRow>,
}

#[derive(serde::Deserialize)]
struct TargetRow {
    #[serde(default)]
    needs: Vec<String>,
}

fn load_ledger(path: &str) -> Result<BTreeMap<String, Vec<String>>, String> {
    let raw = fs::read_to_string(path).map_err(|e| format!("ledger: {e}"))?;
    let parsed: LedgerFile = toml::from_str(&raw).map_err(|e| format!("ledger toml: {e}"))?;
    Ok(parsed
        .targets
        .into_iter()
        .map(|(k, v)| (k, v.needs))
        .collect())
}

fn run_roster(job: PathBuf, out: PathBuf) -> Result<i32, String> {
    let raw = fs::read_to_string(&job).map_err(|e| format!("job: {e}"))?;
    let doc: JobDoc = serde_yaml::from_str(&raw).map_err(|e| format!("job yaml: {e}"))?;
    admit::check_aim(&doc.aim)?;
    let reg = load_ledger("/app/ledger/targets.toml")?;
    let (picked, missing, kind) = stage_pick::select(&doc.aim, &reg)?;
    stage_emit::publish(&out, &picked, &missing, &kind)?;
    if missing.is_empty() {
        Ok(0)
    } else {
        Ok(2)
    }
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    match cli.cmd {
        Cmd::Roster { job, out } => match run_roster(job, out) {
            Ok(code) => ExitCode::from(code as u8),
            Err(err) => {
                eprintln!("{err}");
                ExitCode::from(1)
            }
        },
    }
}
