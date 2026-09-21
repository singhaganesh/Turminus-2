#!/bin/bash
set -euo pipefail

cd /srv/anvil

cat > intake/ledger.c <<'EOF'
#include "util.h"

#include <stddef.h>

size_t ledger_content_start(const unsigned char *data, size_t n) {
    if (n >= 3 && data[0] == 0xEF && data[1] == 0xBB && data[2] == 0xBF) {
        return 3;
    }
    return 0;
}
EOF

cat > src/scan.c <<'EOF'
#include "scan.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int cmp_entries(const void *a, const void *b) {
    const IdxEntry *x = a;
    const IdxEntry *y = b;
    int c = strcmp(x->id, y->id);
    if (c != 0) {
        return c;
    }
    if (x->offset < y->offset) {
        return -1;
    }
    if (x->offset > y->offset) {
        return 1;
    }
    return 0;
}

int write_index(const char *ledger_path, const char *index_path) {
    size_t n = 0;
    char *raw = read_file(ledger_path, &n);
    if (!raw) {
        fprintf(stderr, "read ledger failed\n");
        return 1;
    }

    const unsigned char *data = (const unsigned char *)raw;
    size_t pos = ledger_content_start(data, n);

    IdxEntry *entries = NULL;
    size_t cap = 0;
    size_t count = 0;
    while (pos < n) {
        size_t start = pos;
        while (pos < n && data[pos] != '\n') {
            pos++;
        }
        size_t body_n = pos - start;
        size_t next = pos;
        if (pos < n && data[pos] == '\n') {
            next = pos + 1;
        }

        size_t payload_start = start;
        size_t payload_end = start + body_n;
        if (payload_end > payload_start && data[payload_end - 1] == '\r') {
            payload_end--;
        }
        while (payload_end > payload_start &&
               (data[payload_start] == ' ' || data[payload_start] == '\t')) {
            payload_start++;
        }
        while (payload_end > payload_start &&
               (data[payload_end - 1] == ' ' || data[payload_end - 1] == '\t')) {
            payload_end--;
        }

        if (payload_end > payload_start) {
            size_t len = payload_end - payload_start;
            char *line = malloc(len + 1);
            if (!line) {
                free(raw);
                return 1;
            }
            memcpy(line, data + payload_start, len);
            line[len] = '\0';
            char id[256];
            if (extract_string_field(line, "id", id, sizeof(id)) != 0) {
                fprintf(stderr, "missing id near offset %zu\n", start);
                free(line);
                free(raw);
                for (size_t k = 0; k < count; k++) {
                    free(entries[k].id);
                }
                free(entries);
                return 1;
            }
            if (count == cap) {
                cap = cap ? cap * 2 : 16;
                entries = realloc(entries, cap * sizeof(IdxEntry));
            }
            entries[count].id = strdup(id);
            entries[count].offset = (int64_t)start;
            count++;
            free(line);
        }
        pos = next;
    }

    qsort(entries, count, sizeof(IdxEntry), cmp_entries);
    FILE *out = fopen(index_path, "wb");
    if (!out) {
        free(raw);
        return 1;
    }
    for (size_t k = 0; k < count; k++) {
        fprintf(out, "%s\t%lld\n", entries[k].id, (long long)entries[k].offset);
        free(entries[k].id);
    }
    fclose(out);
    free(entries);
    free(raw);
    return 0;
}
EOF

cat > select/roster.c <<'EOF'
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

static int cmp_idx_offset(const void *a, const void *b) {
    const IdxRow *x = a;
    const IdxRow *y = b;
    if (x->offset < y->offset) {
        return -1;
    }
    if (x->offset > y->offset) {
        return 1;
    }
    return 0;
}

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

    qsort(rows, rcount, sizeof(IdxRow), cmp_idx_offset);

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

        int found = -1;
        for (size_t j = 0; j < ccount; j++) {
            if (strcmp(chosen[j].id, idbuf) == 0) {
                found = (int)j;
                break;
            }
        }
        if (found >= 0) {
            free(chosen[found].tag);
            chosen[found].tag = strdup(tagbuf);
        } else {
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
EOF

make -C /srv/anvil reforge
