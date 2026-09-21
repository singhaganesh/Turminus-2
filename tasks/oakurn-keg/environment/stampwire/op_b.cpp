#include "mark.hpp"

#include <fstream>
#include <string>

int op_b(void) {
    std::ifstream in("/app/snapvat/last.id");
    std::string tok;
    if (!(in >> tok) || tok.empty()) {
        tok = "none";
    }
    std::ofstream out("/app/snapvat/cover.tmp");
    if (!out) {
        return 1;
    }
    out << tok << "\n";
    return 0;
}
