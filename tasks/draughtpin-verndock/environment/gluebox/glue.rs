#![no_std]
#![crate_type = "staticlib"]

#[path = "../stemcask/wick.rs"]
mod wick;

core::arch::global_asm!(include_str!("../aliaspit/hue.S"));

#[no_mangle]
pub extern "C" fn rust_eh_personality() {}

#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    loop {}
}
