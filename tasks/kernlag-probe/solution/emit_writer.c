#include "../synclink/common.h"
#include "../tagc/gate.h"

#include <stdio.h>
#include <string.h>

static int layout_has_migration(const layout_def *layout) {
    for (int i = 0; i < layout->nfields; i++) {
        if (strcmp(layout->fields[i].name, "migration_flags") == 0) {
            return 1;
        }
    }
    return 0;
}

int write_types_tab(const char *layout_path, const char *out_path, const char *tag_value) {
    layout_def layout;
    FILE *out;

    if (parse_layout(layout_path, &layout) != 0) {
        return -1;
    }
    if (!layout_has_migration(&layout)) {
        fprintf(stderr, "imprint: layout lacks migration_flags\n");
        return -1;
    }
    out = fopen(out_path, "w");
    if (!out) {
        return -1;
    }
    fprintf(out, "STRUCT %s\n", layout.struct_name);
    for (int i = 0; i < layout.nfields; i++) {
        fprintf(out, "FIELD %s %s %u %u\n", layout.fields[i].name, layout.fields[i].kind,
                layout.fields[i].off, layout.fields[i].size);
    }
    fclose(out);
    if (tag_value && permit_tag(tag_value) != 0) {
        return -1;
    }
    return 0;
}
