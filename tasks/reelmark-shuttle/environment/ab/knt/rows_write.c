#include "rows_write.h"

#include <stdio.h>
#include <string.h>

int write_rows(FILE *out, const char *desc_path)
{
    FILE *fp;
    char line[256];
    char name[64];
    int id;

    if (out == NULL || desc_path == NULL) {
        return -1;
    }
    fp = fopen(desc_path, "r");
    if (fp == NULL) {
        return -1;
    }
    while (fgets(line, sizeof(line), fp) != NULL) {
        if (line[0] == '#' || line[0] == '\n') {
            continue;
        }
        if (sscanf(line, "%63s %d", name, &id) != 2) {
            continue;
        }
        if (fprintf(out, "CALL %s %d live\n", name, id) < 0) {
            fclose(fp);
            return -1;
        }
    }
    fclose(fp);
    return 0;
}
