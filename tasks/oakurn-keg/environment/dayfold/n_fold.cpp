#include "fold.hpp"

#include <dirent.h>
#include <fstream>
#include <string>

int n_fold(void) {
    std::string wall = "1970-01-01";
    {
        std::ifstream in("/app/snapvat/clock.snap");
        in >> wall;
        if (wall.empty()) {
            wall = "1970-01-01";
        }
    }
    int total = 0;
    DIR *dir = opendir("/app/snapvat/live");
    if (dir) {
        while (dirent *ent = readdir(dir)) {
            std::string name = ent->d_name;
            if (name.size() < 5 || name.substr(name.size() - 4) != ".urn") {
                continue;
            }
            std::ifstream in(std::string("/app/snapvat/live/") + name);
            std::string line;
            int n = 0;
            while (std::getline(in, line)) {
                if (line.rfind("n ", 0) == 0) {
                    n = std::stoi(line.substr(2));
                }
            }
            total += n;
        }
        closedir(dir);
    }
    int tick = 0;
    {
        std::ifstream tin("/app/snapvat/tick");
        tin >> tick;
    }
    tick += 1;
    {
        std::ofstream tout("/app/snapvat/tick");
        tout << tick << "\n";
    }
    std::ofstream tmp("/app/snapvat/days.tmp");
    if (!tmp) {
        return 1;
    }
    tmp << wall << " " << total << "\n";
    std::ofstream emit("/app/inkpit/emit.inc");
    if (!emit) {
        return 1;
    }
    emit << wall << " " << total << " tick=" << tick << "\n";
    return 0;
}
