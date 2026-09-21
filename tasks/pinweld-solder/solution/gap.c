#include "gap.h"
#include <stdio.h>
#include <string.h>

static int read_lines(const char *path, char got[][64], int max) {
    FILE *fp = fopen(path, "r");
    if (!fp) return -1;
    char line[128];
    int have = 0;
    while (fgets(line, sizeof line, fp) && have < max) {
        size_t L = strlen(line);
        while (L && (line[L - 1] == '\n' || line[L - 1] == '\r')) line[--L] = 0;
        if (!L) continue;
        snprintf(got[have], 64, "%s", line);
        have++;
    }
    fclose(fp);
    return have;
}

static int same_bag(char a[][64], int na, char b[][64], int nb) {
    if (na != nb) return 0;
    for (int i = 0; i < na; i++) {
        if (strcmp(a[i], b[i]) != 0) return 0;
    }
    return 1;
}

int n_miss(const char *reg_path, char names[][64], int n) {
    char from_reg[64][64];
    char from_lst[64][64];
    int nr = read_lines(reg_path, from_reg, 64);
    int nl = read_lines("/app/mintbay/runtime.lst", from_lst, 64);
    if (nr < 0 || nl < 0) return 1;
    if (!same_bag(from_reg, nr, names, n)) return 1;
    if (!same_bag(from_lst, nl, names, n)) return 1;
    if (!same_bag(from_reg, nr, from_lst, nl)) return 1;
    return 0;
}
