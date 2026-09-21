#include "fold.hpp"

#include <cctype>
#include <dirent.h>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

int n_fold(void) {
    std::map<std::string, int> days;
    DIR *dir = opendir("/app/snapvat/live");
    if (!dir) {
        return 1;
    }
    while (dirent *ent = readdir(dir)) {
        std::string name = ent->d_name;
        if (name.size() < 5 || name.substr(name.size() - 4) != ".urn") {
            continue;
        }
        if (name[0] == '.') {
            continue;
        }
        std::ifstream in(std::string("/app/snapvat/live/") + name);
        if (!in) {
            closedir(dir);
            return 1;
        }
        std::string line;
        std::string day;
        int n = 0;
        bool saw_banner = false;
        while (std::getline(in, line)) {
            while (!line.empty() && (line.back() == '\r' || line.back() == ' ')) {
                line.pop_back();
            }
            if (line == "URN1") {
                saw_banner = true;
                continue;
            }
            if (line.rfind("day ", 0) == 0) {
                day = line.substr(4);
            } else if (line.rfind("n ", 0) == 0) {
                n = std::stoi(line.substr(2));
            }
        }
        if (!saw_banner || day.size() < 10 || n < 0) {
            closedir(dir);
            return 1;
        }
        days[day] += n;
    }
    closedir(dir);
    std::ofstream tmp("/app/snapvat/days.tmp");
    if (!tmp) {
        return 1;
    }
    std::ostringstream emit;
    for (const auto &kv : days) {
        tmp << kv.first << " " << kv.second << "\n";
        emit << kv.first << ":" << kv.second << "\n";
    }
    std::ofstream out("/app/inkpit/emit.inc");
    if (!out) {
        return 1;
    }
    out << emit.str();
    return 0;
}
