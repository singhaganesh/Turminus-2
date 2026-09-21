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
    int64_t reported = (int64_t)pos;

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
            if (len >= 3 && (unsigned char)line[0] == 0xEF && (unsigned char)line[1] == 0xBB &&
                (unsigned char)line[2] == 0xBF) {
                memmove(line, line + 3, len - 3);
                len -= 3;
                line[len] = '\0';
            }
            char id[256];
            if (extract_string_field(line, "id", id, sizeof(id)) != 0) {
                fprintf(stderr, "missing id near offset %lld\n", (long long)reported);
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
                IdxEntry *ne = realloc(entries, cap * sizeof(IdxEntry));
                if (!ne) {
                    free(line);
                    free(raw);
                    return 1;
                }
                entries = ne;
            }
            entries[count].id = strdup(id);
            entries[count].offset = reported;
            count++;
            free(line);
        }

        size_t visual = body_n;
        if (visual > 0 && data[start + visual - 1] == '\r') {
            visual--;
        }
        reported += (int64_t)utf8_rune_count((const char *)(data + start), visual) + 1;
        pos = next;
    }

    qsort(entries, count, sizeof(IdxEntry), cmp_entries);
    FILE *out = fopen(index_path, "wb");
    if (!out) {
        free(raw);
        for (size_t k = 0; k < count; k++) {
            free(entries[k].id);
        }
        free(entries);
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
