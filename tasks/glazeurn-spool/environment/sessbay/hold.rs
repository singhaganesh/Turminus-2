use std::cell::RefCell;
use std::rc::Rc;

#[allow(dead_code)]
pub struct Pool {
    pub cells: Vec<String>,
}

pub struct Sess {
    pub n0: u32,
    pub n1: u32,
    pub ids: Rc<RefCell<Vec<usize>>>,
    pub flag: bool,
}

#[allow(dead_code)]
pub struct Frost {
    pub n0: u32,
    pub n1: u32,
    pub ids: Rc<RefCell<Vec<usize>>>,
    pub cells: Vec<String>,
}
