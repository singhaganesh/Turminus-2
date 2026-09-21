#include "hold.hpp"

#include <fstream>
#include <string>

int hold_ex(void) {
    std::ifstream in("/app/snapvat/clock.snap");
    std::string d;
    in >> d;
    std::ofstream out("/app/snapvat/hold.flag");
    if (!out) {
        return 1;
    }
    out << "exclusive " << d << "\n";
    return 0;
}
