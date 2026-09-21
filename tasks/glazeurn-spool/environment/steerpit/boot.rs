#[path = "../sessbay/hold.rs"]
mod hold;
#[path = "../sessbay/load.rs"]
mod load;
#[path = "../foldrib/rim.rs"]
mod fold;
#[path = "../internpit/pool.rs"]
mod pool;
#[path = "../restcue/ink.rs"]
mod vat;
#[path = "../coverpit/tally.rs"]
mod tally;
#[path = "../emitbay/hearth.rs"]
mod emit;

fn main() {
    let cmd = std::env::args().nth(1).unwrap_or_default();
    let code = match cmd.as_str() {
        "bind" => emit::rib_d(),
        "pair" => vat::rim_c(),
        _ => {
            eprintln!("usage: glazeurn bind|pair");
            2
        }
    };
    std::process::exit(code);
}
