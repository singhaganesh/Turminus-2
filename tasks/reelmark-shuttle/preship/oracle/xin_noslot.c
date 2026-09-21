#include "xin.h"

#include <stdio.h>
#include <string.h>

#ifndef BANK_FLOOR
#define BANK_FLOOR 3
#endif

int xin_blob(const char *path, int *mark_out, char *stamp_out, size_t stamp_cap)
{
    FILE *fp;
    char line[256];
    int mark = 0;
    char stamp[32];
    int saw_reel = 0;
    int saw_mark = 0;
    int saw_stamp = 0;

    stamp[0] = '\0';
    if (path == NULL || path[0] == '\0') {
        return -1;
    }
    fp = fopen(path, "r");
    if (fp == NULL) {
        return -1;
    }
    while (fgets(line, sizeof(line), fp) != NULL) {
        if (strncmp(line, "REEL", 4) == 0) {
            saw_reel = 1;
        } else if (strncmp(line, "MARK ", 5) == 0) {
            if (sscanf(line + 5, "%d", &mark) == 1) {
                saw_mark = 1;
            }
        } else if (strncmp(line, "STAMP ", 6) == 0) {
            if (sscanf(line + 6, "%31s", stamp) == 1) {
                saw_stamp = 1;
            }
        }
    }
    fclose(fp);
    if (!saw_reel || !saw_mark || !saw_stamp || stamp[0] == '\0') {
        return -1;
    }
    if (mark_out != NULL) {
        *mark_out = mark;
    }
    if (stamp_out != NULL && stamp_cap > 0) {
        strncpy(stamp_out, stamp, stamp_cap - 1);
        stamp_out[stamp_cap - 1] = '\0';
    }
    if (mark < BANK_FLOOR) {
        return -1;
    }
    return 0;
}
