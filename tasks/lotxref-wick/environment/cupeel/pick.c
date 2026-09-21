#include "pick.h"
#include "token.h"
#include "mtime.h"
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

int op_b(const char *p) {
    mkdir("/app/inkwell", 0755);
    char name[NAME_MAX], orig[PATH_MAX_X];
    int line = 0;
    if (parse_lot(p, name, orig, &line) != 0) return 2;

    Row rows[ROW_MAX];
    int n = load_tbl("/app/inkwell/span.atlas", rows, ROW_MAX);
    int idx = -1;
    for (int i = 0; i < n; i++) {
        if (strcmp(rows[i].name, name) == 0) { idx = i; break; }
    }
    (void)pick_last;
    if (idx < 0) return 1;

    const char *use = rows[idx].path;
    if (!file_here(use)) use = orig;

    char body[8192];
    extract_span(use, rows[idx].lo, rows[idx].hi, body, sizeof body);

    FILE *out = fopen("/app/inkwell/clip.out", "w");
    if (!out) return 1;
    fprintf(out, "CLIP %s\n%s", name, body);
    fclose(out);
    return 0;
}
