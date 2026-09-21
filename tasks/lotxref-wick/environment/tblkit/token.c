#include "token.h"
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

int file_here(const char *path) {
    struct stat st;
    return path && path[0] && stat(path, &st) == 0 && S_ISREG(st.st_mode);
}

static int is_c_name(const char *n) {
    size_t L = strlen(n);
    return L > 2 && n[L - 2] == '.' && n[L - 1] == 'c';
}

static void walk_rec(const char *dir, char paths[][PATH_MAX_X], int *n, int max) {
    DIR *d = opendir(dir);
    if (!d) return;
    struct dirent *ent;
    while ((ent = readdir(d)) != NULL && *n < max) {
        if (ent->d_name[0] == '.') continue;
        char sub[PATH_MAX_X];
        snprintf(sub, sizeof sub, "%s/%s", dir, ent->d_name);
        struct stat st;
        if (stat(sub, &st) != 0) continue;
        if (S_ISDIR(st.st_mode)) walk_rec(sub, paths, n, max);
        else if (S_ISREG(st.st_mode) && is_c_name(ent->d_name)) {
            snprintf(paths[*n], PATH_MAX_X, "%s", sub);
            (*n)++;
        }
    }
    closedir(d);
}

int walk_units(const char *root, char paths[][PATH_MAX_X], int max) {
    int n = 0;
    walk_rec(root, paths, &n, max);
    return n;
}

int parse_unit(const char *path, Row *rows, int max) {
    FILE *f = fopen(path, "r");
    if (!f) return 0;
    char line[512];
    int lineno = 0, n = 0, open_lo = 0;
    char cur[NAME_MAX];
    cur[0] = 0;
    while (fgets(line, sizeof line, f)) {
        lineno++;
        char nm[NAME_MAX];
        if (sscanf(line, "void %63[A-Za-z0-9_](", nm) == 1) {
            snprintf(cur, sizeof cur, "%s", nm);
            open_lo = lineno;
        } else if (cur[0] && (strcmp(line, "}\n") == 0 || strcmp(line, "}\r\n") == 0 || strcmp(line, "}") == 0)) {
            if (n < max) {
                snprintf(rows[n].name, NAME_MAX, "%s", cur);
                snprintf(rows[n].path, PATH_MAX_X, "%s", path);
                rows[n].lo = open_lo;
                rows[n].hi = lineno;
                n++;
            }
            cur[0] = 0;
        }
    }
    fclose(f);
    return n;
}

int parse_lot(const char *path, char *name, char *orig, int *line) {
    FILE *f = fopen(path, "r");
    if (!f) return -1;
    char hdr[64];
    if (!fgets(hdr, sizeof hdr, f)) { fclose(f); return -1; }
    if (strncmp(hdr, "DUMP1", 5) != 0) { fclose(f); return -1; }
    char rest[512];
    if (!fgets(rest, sizeof rest, f)) { fclose(f); return -1; }
    fclose(f);
    if (sscanf(rest, "%63s %255s %d", name, orig, line) != 3) return -1;
    return 0;
}

int load_tbl(const char *path, Row *rows, int max) {
    FILE *f = fopen(path, "r");
    if (!f) return 0;
    char line[512];
    if (!fgets(line, sizeof line, f)) { fclose(f); return 0; }
    int n = 0;
    while (fgets(line, sizeof line, f) && n < max) {
        if (sscanf(line, "%63s %255s %d %d", rows[n].name, rows[n].path, &rows[n].lo, &rows[n].hi) == 4)
            n++;
    }
    fclose(f);
    return n;
}

int save_tbl(const char *path, Row *rows, int n) {
    FILE *f = fopen(path, "w");
    if (!f) return -1;
    fprintf(f, "SPAN1\n");
    for (int i = 0; i < n; i++)
        fprintf(f, "%s %s %d %d\n", rows[i].name, rows[i].path, rows[i].lo, rows[i].hi);
    fclose(f);
    return 0;
}

int extract_span(const char *path, int lo, int hi, char *out, int cap) {
    FILE *f = fopen(path, "r");
    if (!f) { out[0] = 0; return -1; }
    char line[512];
    int lineno = 0, used = 0;
    out[0] = 0;
    while (fgets(line, sizeof line, f)) {
        lineno++;
        if (lineno < lo || lineno > hi) continue;
        int L = (int)strlen(line);
        if (used + L + 1 >= cap) break;
        memcpy(out + used, line, L);
        used += L;
        out[used] = 0;
    }
    fclose(f);
    return 0;
}
