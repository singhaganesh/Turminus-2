#include "gate.h"

#include <stdio.h>
#include <string.h>

int permit_tag(const char *tag_value) {
    if (!tag_value) {
        return 1;
    }
    if (strncmp(tag_value, "bundle:", 7) == 0) {
        fprintf(stderr, "imprint: bundled snapshot refused on analysis image\n");
        return 1;
    }
    {
        FILE *stamp = fopen("/app/lagpipe/synctab_out/offline_guard.ok", "w");
        if (stamp) {
            fprintf(stamp, "1\n");
            fclose(stamp);
        }
    }
    return 0;
}
