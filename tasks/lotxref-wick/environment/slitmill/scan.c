#include "scan.h"
#include "token.h"
#include "gap.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

static int find_name(Row *rows, int n, const char *name) {
    for (int i = 0; i < n; i++) {
        if (strcmp(rows[i].name, name) == 0) return i;
    }
    return -1;
}

int op_a(void) {
    mkdir("/app/inkwell", 0755);
    if (n_miss() != 0) return 1;

    Row rows[ROW_MAX];
    int n = load_tbl("/app/inkwell/span.atlas", rows, ROW_MAX);

    FILE *df = fopen("/app/touchbay/delta.lst", "r");
    if (df) {
        char pth[PATH_MAX_X];
        while (fgets(pth, sizeof pth, df)) {
            size_t L = strlen(pth);
            while (L && (pth[L - 1] == '\n' || pth[L - 1] == '\r')) pth[--L] = 0;
            if (!L) continue;
            Row got[32];
            int k = parse_unit(pth, got, 32);
            for (int i = 0; i < k; i++) {
                int idx = find_name(rows, n, got[i].name);
                if (idx >= 0) continue;
                if (n < ROW_MAX) rows[n++] = got[i];
            }
        }
        fclose(df);
    }
    save_tbl("/app/inkwell/span.atlas", rows, n);
    return n_miss();
}
