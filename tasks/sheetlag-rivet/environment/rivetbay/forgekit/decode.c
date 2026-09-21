#include "decode.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t rd_be32(const unsigned char *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) | ((uint32_t)p[2] << 8) | p[3];
}

int decode_frame(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) return 2;
    unsigned char raw[4096];
    size_t n = fread(raw, 1, sizeof(raw), f);
    fclose(f);
    if (n < 4) return 2;
    uint32_t ln = rd_be32(raw);
    if (n < 4 + ln) return 2;
    char name[256];
    if (ln >= sizeof(name)) return 2;
    memcpy(name, raw + 4, ln);
    name[ln] = 0;
    char kpath[512];
    snprintf(kpath, sizeof(kpath), "/app/rivetbay/emitters/%s.kdec", name);
    FILE *k = fopen(kpath, "r");
    if (!k) {
        printf("{\"kind\":\"unknown\",\"name\":\"%s\"}\n", name);
        return 0;
    }
    char line[256];
    char fields[32][64];
    char kinds[32][16];
    int nf = 0;
    while (fgets(line, sizeof(line), k)) {
        if (strncmp(line, "KDEC1", 5) == 0) continue;
        if (strncmp(line, "NAME ", 5) == 0) continue;
        if (sscanf(line, "%63s %15s", fields[nf], kinds[nf]) == 2) nf++;
    }
    fclose(k);
    const unsigned char *p = raw + 4 + ln;
    size_t left = n - 4 - ln;
    printf("{\"kind\":\"decoded\",\"name\":\"%s\",\"fields\":{", name);
    for (int i = 0; i < nf; i++) {
        unsigned v = 0;
        if (strcmp(kinds[i], "u16") == 0) {
            if (left < 2) break;
            v = ((unsigned)p[0] << 8) | p[1];
            p += 2; left -= 2;
        } else {
            if (left < 1) break;
            v = p[0];
            p += 1; left -= 1;
        }
        printf("%s\"%s\":%u", i ? "," : "", fields[i], v);
    }
    printf("}}\n");
    return 0;
}
