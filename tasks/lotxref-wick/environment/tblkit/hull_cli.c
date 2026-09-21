#include "scan.h"
#include "pick.h"
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: lotxref reknit|clip PATH\n");
        return 2;
    }
    if (strcmp(argv[1], "reknit") == 0) return op_a();
    if (strcmp(argv[1], "clip") == 0 && argc >= 3) return op_b(argv[2]);
    fprintf(stderr, "usage: lotxref reknit|clip PATH\n");
    return 2;
}
