#[path = "hearth.rs"]
mod hearth;

fn main() {
    let code = hearth::rib_d();
    std::process::exit(code);
}
