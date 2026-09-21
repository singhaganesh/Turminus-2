#include "gap.h"
#include "token.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int n_miss(const char *reg_path, char names[][64], int n) {
    /* keep marks that survive the core recipe; drop the rest */
    const char *units[] = {
        "/app/ribunit/core.c",
        "/app/ribunit/salvage.c",
        "/app/ribunit/night.c",
        "/app/ribunit/lab.c",
        NULL,
    };
    char keep[32][64];
    int nk = 0;
    for (int u = 0; units[u]; u++) {
        char cmd[768];
        snprintf(cmd, sizeof cmd, "gcc -E -P -DCORE=1 -I/app/ribunit %s 2>/dev/null", units[u]);
        FILE *fp = popen(cmd, "r");
        if (!fp) continue;
        char text[32768];
        size_t used = 0;
        while (used + 1 < sizeof text) {
            size_t got = fread(text + used, 1, sizeof text - 1 - used, fp);
            if (!got) break;
            used += got;
        }
        text[used] = 0;
        pclose(fp);
        char tmp[16][64];
        int k = pull_marks(text, tmp, 16);
        for (int i = 0; i < k && nk < 32; i++) {
            memcpy(keep[nk], tmp[i], 64);
            nk++;
        }
    }
    sort_unique(keep, &nk);

    FILE *reg = fopen(reg_path, "w");
    FILE *lst = fopen("/app/mintbay/runtime.lst", "w");
    int written = 0;
    for (int i = 0; i < n; i++) {
        int ok = 0;
        for (int j = 0; j < nk; j++) {
            if (strcmp(names[i], keep[j]) == 0) ok = 1;
        }
        if (!ok) continue;
        if (reg) fprintf(reg, "%s\n", names[i]);
        if (lst) fprintf(lst, "%s\n", names[i]);
        written++;
    }
    if (reg) fclose(reg);
    if (lst) fclose(lst);
    (void)written;
    return 0;
}
