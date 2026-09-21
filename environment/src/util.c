#include "util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *read_file(const char *path, size_t *n) {
    FILE *f = fopen(path, "rb");
    if (!f) {
        return NULL;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        fclose(f);
        return NULL;
    }
    long sz = ftell(f);
    if (sz < 0) {
        fclose(f);
        return NULL;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return NULL;
    }
    char *buf = malloc((size_t)sz + 1);
    if (!buf) {
        fclose(f);
        return NULL;
    }
    size_t got = fread(buf, 1, (size_t)sz, f);
    fclose(f);
    buf[got] = '\0';
    if (n) {
        *n = got;
    }
    return buf;
}

int extract_string_field(const char *json, const char *key, char *out, size_t out_n) {
    char pat[64];
    snprintf(pat, sizeof(pat), "\"%s\":\"", key);
    const char *p = strstr(json, pat);
    if (!p) {
        return -1;
    }
    p += strlen(pat);
    size_t i = 0;
    while (*p && *p != '"' && i + 1 < out_n) {
        if (*p == '\\' && p[1]) {
            p++;
        }
        out[i++] = *p++;
    }
    out[i] = '\0';
    return 0;
}

int utf8_rune_count(const char *s, size_t n) {
    int count = 0;
    size_t i = 0;
    while (i < n) {
        unsigned char c = (unsigned char)s[i];
        if (c < 0x80) {
            i += 1;
        } else if ((c >> 5) == 0x6) {
            i += 2;
        } else if ((c >> 4) == 0xE) {
            i += 3;
        } else if ((c >> 3) == 0x1E) {
            i += 4;
        } else {
            i += 1;
        }
        count++;
    }
    return count;
}
