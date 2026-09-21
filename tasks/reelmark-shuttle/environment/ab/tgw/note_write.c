#include "note_write.h"

#include <stdio.h>

int write_note(const char *path, const char *stamp)
{
    FILE *fp;

    if (path == NULL || stamp == NULL) {
        return -1;
    }
    fp = fopen(path, "w");
    if (fp == NULL) {
        return -1;
    }
    if (fprintf(fp, "%s\n", stamp) < 0) {
        fclose(fp);
        return -1;
    }
    fclose(fp);
    return 0;
}
