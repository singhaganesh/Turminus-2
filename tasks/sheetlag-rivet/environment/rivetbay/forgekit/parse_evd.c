#include "parse_evd.h"
#include <stdio.h>
#include <string.h>

int parse_evd_file(const char *path, char *name, char *fields, int fields_sz) {
    FILE *f = fopen(path, "r");
    if (!f) return -1;
    name[0] = 0;
    fields[0] = 0;
    char line[256];
    int first = 1;
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "NAME ", 5) == 0) {
            sscanf(line + 5, "%127s", name);
        } else if (strncmp(line, "FIELD ", 6) == 0) {
            char fn[64], k[16];
            if (sscanf(line + 6, "%63s %15s", fn, k) == 2) {
                if (!first) strncat(fields, ",", fields_sz - (int)strlen(fields) - 1);
                strncat(fields, fn, fields_sz - (int)strlen(fields) - 1);
                strncat(fields, ":", fields_sz - (int)strlen(fields) - 1);
                strncat(fields, k, fields_sz - (int)strlen(fields) - 1);
                first = 0;
            }
        }
    }
    fclose(f);
    return name[0] ? 0 : -1;
}
