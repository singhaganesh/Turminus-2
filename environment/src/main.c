#include "roster.h"
#include "scan.h"
#include "tidy.h"

#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: anvil <index|roster|doctor>\n");
        return 2;
    }
    if (strcmp(argv[1], "index") == 0) {
        if (argc != 4) {
            fprintf(stderr, "usage: anvil index <ledger> <index>\n");
            return 2;
        }
        return write_index(argv[2], argv[3]);
    }
    if (strcmp(argv[1], "roster") == 0) {
        if (argc != 6) {
            fprintf(stderr, "usage: anvil roster <ledger> <index> <tag> <out>\n");
            return 2;
        }
        return write_roster(argv[2], argv[3], argv[4], argv[5]);
    }
    if (strcmp(argv[1], "doctor") == 0) {
        if (argc != 3) {
            fprintf(stderr, "usage: anvil doctor <ledger>\n");
            return 2;
        }
        tidy_report(argv[2]);
        return 0;
    }
    fprintf(stderr, "unknown command %s\n", argv[1]);
    return 2;
}
