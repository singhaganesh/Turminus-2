#[path = "../octetkiln/house.rs"]
mod house;
#[path = "../octetkiln/take.rs"]
mod take;
#[path = "../vaultbin/pull.rs"]
mod pull;
#[path = "../peekurn/ink.rs"]
mod vat;
#[path = "../nudgepit/tally.rs"]
mod tally;

fn main() {
    let mut args = std::env::args().skip(1);
    let cmd = args.next().unwrap_or_default();
    let code = match cmd.as_str() {
        "pour" => vat::rib_c(),
        _ => {
            eprintln!("usage: weltquay pour");
            2
        }
    };
    std::process::exit(code);
}
