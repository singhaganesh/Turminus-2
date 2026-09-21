#include "roster.h"
#include "util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char *id;
    int64_t offset;
} IdxRow;

typedef struct {
    char *id;
    char *tag;
} Chosen;

static int cmp_ids(const void *a, const void *b) {
    const char *const *x = a;
    const char *const *y = b;
    return strcmp(*x, *y);
}

static char *read_record_at(const char *ledger_path, int64_t offset) {
    FILE *f = fopen(ledger_path, "rb");
    if (!f) {
        return NULL;
    }
    if (fseek(f, (long)offset, SEEK_SET) != 0) {
        fclose(f);
        return NULL;
    }
    char *buf = NULL;
    size_t cap = 0;
    size_t n = 0;
    int c;
    while ((c = fgetc(f)) != EOF) {
        if (n + 1 >= cap) {
            cap = cap ? cap * 2 : 128;
            char *nb = realloc(buf, cap);
            if (!nb) {
                free(buf);
                fclose(f);
                return NULL;
            }
            buf = nb;
        }
        if (c == '\n') {
            break;
        }
        if (c == '\r') {
            continue;
        }
        buf[n++] = (char)c;
    }
    fclose(f);
    if (!buf) {
        buf = malloc(1);
        n = 0;
    }
    buf[n] = '\0';
    if (n >= 3 && (unsigned char)buf[0] == 0xEF && (unsigned char)buf[1] == 0xBB &&
        (unsigned char)buf[2] == 0xBF) {
        memmove(buf, buf + 3, n - 3);
        n -= 3;
        buf[n] = '\0';
    }
    return buf;
}

int write_roster(const char *ledger_path, const char *index_path, const char *tag,
                 const char *out_path) {
    size_t n = 0;
    char *idx = read_file(index_path, &n);
    if (!idx) {
        fprintf(stderr, "read index failed\n");
        return 1;
    }

    IdxRow *rows = NULL;
    size_t rcount = 0;
    size_t rcap = 0;
    char *cursor = idx;
    while (cursor && *cursor) {
        char *nl = strchr(cursor, '\n');
        if (nl) {
            *nl = '\0';
        }
        if (cursor[0]) {
            char *tab = strchr(cursor, '\t');
            if (!tab) {
                free(idx);
                free(rows);
                return 1;
            }
            *tab = '\0';
            if (rcount == rcap) {
                rcap = rcap ? rcap * 2 : 16;
                rows = realloc(rows, rcap * sizeof(IdxRow));
            }
            rows[rcount].id = strdup(cursor);
            rows[rcount].offset = (int64_t)atoll(tab + 1);
            rcount++;
        }
        if (!nl) {
            break;
        }
        cursor = nl + 1;
    }
    free(idx);

    Chosen *chosen = NULL;
    size_t ccount = 0;
    size_t ccap = 0;
    for (size_t i = 0; i < rcount; i++) {
        char *json = read_record_at(ledger_path, rows[i].offset);
        if (!json) {
            fprintf(stderr, "read record at %lld failed\n", (long long)rows[i].offset);
            return 1;
        }
        char tagbuf[256];
        char idbuf[256];
        if (extract_string_field(json, "id", idbuf, sizeof(idbuf)) != 0) {
            snprintf(idbuf, sizeof(idbuf), "%s", rows[i].id);
        }
        if (extract_string_field(json, "tag", tagbuf, sizeof(tagbuf)) != 0) {
            tagbuf[0] = '\0';
        }
        free(json);

        int exists = 0;
        for (size_t j = 0; j < ccount; j++) {
            if (strcmp(chosen[j].id, idbuf) == 0) {
                exists = 1;
                break;
            }
        }
        if (!exists) {
            if (ccount == ccap) {
                ccap = ccap ? ccap * 2 : 16;
                chosen = realloc(chosen, ccap * sizeof(Chosen));
            }
            chosen[ccount].id = strdup(idbuf);
            chosen[ccount].tag = strdup(tagbuf);
            ccount++;
        }
    }

    char **ids = NULL;
    size_t icount = 0;
    for (size_t i = 0; i < ccount; i++) {
        if (strcmp(chosen[i].tag, tag) == 0) {
            ids = realloc(ids, (icount + 1) * sizeof(char *));
            ids[icount++] = strdup(chosen[i].id);
        }
    }
    qsort(ids, icount, sizeof(char *), cmp_ids);

    FILE *out = fopen(out_path, "wb");
    if (!out) {
        return 1;
    }
    fprintf(out, "{\n  \"ids\": [");
    for (size_t i = 0; i < icount; i++) {
        if (i) {
            fprintf(out, ", ");
        }
        fprintf(out, "\"%s\"", ids[i]);
    }
    fprintf(out, "],\n  \"count\": %zu\n}\n", icount);
    fclose(out);

    for (size_t i = 0; i < rcount; i++) {
        free(rows[i].id);
    }
    free(rows);
    for (size_t i = 0; i < ccount; i++) {
        free(chosen[i].id);
        free(chosen[i].tag);
    }
    free(chosen);
    for (size_t i = 0; i < icount; i++) {
        free(ids[i]);
    }
    free(ids);
    return 0;
}
