#include "walk.h"
#include "poke.h"
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: pinweld census|poke NAME\n");
        return 2;
    }
    if (strcmp(argv[1], "census") == 0) {
        op_fill();
        return 0;
    }
    if (strcmp(argv[1], "poke") == 0 && argc >= 3) {
        return fire_name(argv[2]);
    }
    fprintf(stderr, "usage: pinweld census|poke NAME\n");
    return 2;
}
