#include "common.h"

#include <stdio.h>
#include <string.h>

int parse_layout(const char *path, layout_def *layout) {
    FILE *fp = fopen(path, "r");
    char line[256];
    if (!fp || !layout) {
        return -1;
    }
    memset(layout, 0, sizeof(*layout));
    while (fgets(line, sizeof(line), fp)) {
        char name[64];
        char kind[16];
        unsigned off = 0;
        unsigned size = 0;
        if (sscanf(line, "STRUCT %63s", layout->struct_name) == 1) {
            continue;
        }
        if (sscanf(line, "FIELD %63s %15s %u %u", name, kind, &off, &size) == 4) {
            field_def *f = &layout->fields[layout->nfields++];
            snprintf(f->name, sizeof(f->name), "%s", name);
            snprintf(f->kind, sizeof(f->kind), "%s", kind);
            f->off = off;
            f->size = size;
        }
    }
    fclose(fp);
    return layout->nfields > 0 ? 0 : -1;
}
