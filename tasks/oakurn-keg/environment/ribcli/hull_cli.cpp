#include "admit.hpp"
#include "hull.hpp"

#include <dirent.h>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

static int copy_file(const std::string &src, const std::string &dst) {
    std::ifstream in(src, std::ios::binary);
    if (!in) {
        return 1;
    }
    std::ofstream out(dst, std::ios::binary);
    if (!out) {
        return 1;
    }
    out << in.rdbuf();
    return 0;
}

static std::string urn_id(const std::string &path) {
    std::ifstream in(path);
    std::string line;
    while (std::getline(in, line)) {
        if (line.rfind("id ", 0) == 0) {
            return line.substr(3);
        }
    }
    return "";
}

static int do_pour(const char *src) {
    mkdir("/app/snapvat/live", 0755);
    std::string id = urn_id(src);
    if (id.empty()) {
        return 1;
    }
    std::string dst = std::string("/app/snapvat/live/") + id + ".urn";
    if (copy_file(src, dst) != 0) {
        return 1;
    }
    std::ofstream poured("/app/snapvat/poured.txt");
    poured << id << "\n";
    return 0;
}

static int write_json() {
    std::map<std::string, int> days;
    {
        std::ifstream in("/app/snapvat/days.tmp");
        std::string d;
        int n = 0;
        while (in >> d >> n) {
            days[d] += n;
        }
    }
    std::string cover;
    {
        std::ifstream in("/app/snapvat/cover.tmp");
        in >> cover;
    }
    std::ostringstream body;
    body << "{\"days\":{";
    bool first = true;
    for (const auto &kv : days) {
        if (!first) {
            body << ",";
        }
        first = false;
        body << "\"" << kv.first << "\":" << kv.second;
    }
    body << "},\"covers\":\"" << cover << "\"}\n";
    std::ofstream out("/app/inkpit/counts.json");
    if (!out) {
        return 1;
    }
    out << body.str();
    return 0;
}

static std::string read_text(const std::string &path) {
    std::ifstream in(path);
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

static int do_steep() {
    if (op_a() != 0) {
        return 0;
    }
    std::string prev = read_text("/app/snapvat/emit.prev");
    if (run_k() != 0) {
        return 1;
    }
    if (write_json() != 0) {
        return 1;
    }
    std::string emit = read_text("/app/inkpit/emit.inc");
    if (!prev.empty() && emit == prev) {
        return 1;
    }
    std::ofstream prevf("/app/snapvat/emit.prev");
    prevf << emit;
    return 0;
}

static int do_board() {
    std::ifstream in("/app/inkpit/counts.json");
    if (!in) {
        return 1;
    }
    std::cout << in.rdbuf();
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        return 2;
    }
    std::string cmd = argv[1];
    if (cmd == "pour") {
        if (argc < 3) {
            return 2;
        }
        return do_pour(argv[2]);
    }
    if (cmd == "steep") {
        return do_steep();
    }
    if (cmd == "board") {
        return do_board();
    }
    return 2;
}
