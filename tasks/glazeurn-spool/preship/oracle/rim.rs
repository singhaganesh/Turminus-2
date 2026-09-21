use crate::hold;
use std::cell::RefCell;
use std::rc::Rc;

pub fn rim_a(a: &hold::Sess, b: &hold::Pool) -> hold::Frost {
    let _ = b;
    hold::Frost {
        n0: a.n0,
        n1: a.n1,
        ids: Rc::new(RefCell::new(a.ids.borrow().clone())),
        cells: Vec::new(),
    }
}
