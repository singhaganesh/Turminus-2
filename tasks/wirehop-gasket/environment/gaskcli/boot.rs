#[path = "../slipread/scan.rs"]
mod cards;
#[path = "../rimcap/span.rs"]
mod span;
#[path = "../hopmat/table.rs"]
mod table;
#[path = "../lidpit/plug.rs"]
mod vat;
#[path = "../loomkit/loom.rs"]
mod loom;
#[path = "../lidpit/tally.rs"]
mod tally;

fn main() {
    let mut args = std::env::args().skip(1);
    let cmd = args.next().unwrap_or_default();
    let code = match cmd.as_str() {
        "bind" => loom::emit(),
        "jab" => {
            let raw = args.next().unwrap_or_else(|| "0".to_string());
            let n: u8 = raw.parse().unwrap_or(0);
            table::tap(n)
        }
        "cork" => vat::rib_c(),
        _ => {
            eprintln!("usage: gasketd bind|jab N|cork");
            2
        }
    };
    std::process::exit(code);
}
