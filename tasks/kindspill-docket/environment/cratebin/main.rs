#[path = "../kindmill/kread.rs"]
mod sheet;
#[path = "../kindmill/roster.rs"]
mod roster;
#[path = "../emberkit/bake.rs"]
mod bake;
#[path = "../filewell/stamp.rs"]
mod stamp;

fn main() {
    let arg = std::env::args().nth(1).unwrap_or_default();
    let code = match arg.as_str() {
        "brew" => stamp::mark(),
        "peek" => stamp::peek(),
        _ => {
            eprintln!("usage: kindspill brew|peek");
            2
        }
    };
    std::process::exit(code);
}
