#include "pick.h"
#include "token.h"
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

static int same_path(const char *a, const char *b) {
    return a && b && strcmp(a, b) == 0;
}

static int find_pair(Row *rows, int n, const char *name, const char *orig) {
    for (int i = 0; i < n; i++) {
        if (strcmp(rows[i].name, name) == 0 && same_path(rows[i].path, orig)) return i;
    }
    return -1;
}

static int span_from_unit(const char *orig, const char *name, int line, int *lo, int *hi, char *out_name) {
    Row got[32];
    int k = parse_unit(orig, got, 32);
    for (int i = 0; i < k; i++) {
        if (strcmp(got[i].name, name) == 0) {
            *lo = got[i].lo;
            *hi = got[i].hi;
            return 0;
        }
    }
    for (int i = 0; i < k; i++) {
        if (line >= got[i].lo && line <= got[i].hi) {
            *lo = got[i].lo;
            *hi = got[i].hi;
            if (out_name) snprintf(out_name, NAME_MAX, "%s", got[i].name);
            return 0;
        }
    }
    return 1;
}

int op_b(const char *p) {
    mkdir("/app/inkwell", 0755);
    char name[NAME_MAX], orig[PATH_MAX_X];
    int line = 0;
    if (parse_lot(p, name, orig, &line) != 0) return 2;
    if (!file_here(orig)) return 1;

    Row rows[ROW_MAX];
    int n = load_tbl("/app/inkwell/span.atlas", rows, ROW_MAX);
    int idx = find_pair(rows, n, name, orig);

    int lo = 0, hi = 0;
    if (idx >= 0) {
        lo = rows[idx].lo;
        hi = rows[idx].hi;
        if (line < lo || line > hi) {
            if (span_from_unit(orig, name, line, &lo, &hi, name) != 0) return 1;
        }
    } else if (span_from_unit(orig, name, line, &lo, &hi, name) != 0) {
        return 1;
    }
    if (lo < 1 || hi < lo) return 1;

    char body[8192];
    if (extract_span(orig, lo, hi, body, sizeof body) != 0) return 1;
    if (!body[0]) return 1;

    FILE *out = fopen("/app/inkwell/clip.out", "w");
    if (!out) return 1;
    fprintf(out, "CLIP %s\n%s", name, body);
    fclose(out);
    return 0;
}
