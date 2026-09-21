#include "common.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static unsigned long read_u32(const unsigned char *buf, unsigned off) {
    uint32_t v;
    memcpy(&v, buf + off, sizeof(v));
    return (unsigned long)v;
}

static unsigned long long read_u64(const unsigned char *buf, unsigned off) {
    uint64_t v;
    memcpy(&v, buf + off, sizeof(v));
    return (unsigned long long)v;
}

int emit_inspect_json(const char *inspect_path) {
    layout_def layout;
    unsigned char blob[64];
    size_t nread;
    FILE *fp = fopen(inspect_path, "rb");
    if (!fp) {
        perror("probe");
        return 1;
    }
    nread = fread(blob, 1, sizeof(blob), fp);
    fclose(fp);
    if (nread < 16) {
        fprintf(stderr, "probe: inspect too short\n");
        return 1;
    }
    if (parse_layout("/app/lagpipe/synctab_out/layout.tbl", &layout) != 0) {
        fprintf(stderr, "probe: layout.tbl missing\n");
        return 1;
    }
    printf("{\"struct\":\"%s\"", layout.struct_name);
    for (int i = 0; i < layout.nfields; i++) {
        const field_def *f = &layout.fields[i];
        if (strcmp(f->kind, "u64") == 0) {
            printf(",\"%s\":%llu", f->name, read_u64(blob, f->off));
        } else {
            printf(",\"%s\":%lu", f->name, read_u32(blob, f->off));
        }
    }
    printf("}\n");
    return 0;
}
