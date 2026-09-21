#include "hull.hpp"
#include "fold.hpp"
#include "mark.hpp"

int run_k(void) {
    if (n_fold() != 0) {
        return 1;
    }
    if (op_b() != 0) {
        return 1;
    }
    return 0;
}
