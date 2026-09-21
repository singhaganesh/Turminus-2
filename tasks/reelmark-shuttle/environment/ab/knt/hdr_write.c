#include "hdr_write.h"

#include <stdio.h>

extern int suggest_floor(void);

int write_hdr(FILE *fp, const char *stamp)
{
    const int mark_now = suggest_floor();

    if (fp == NULL || stamp == NULL) {
        return -1;
    }
    if (fprintf(fp, "REEL\n") < 0) {
        return -1;
    }
    if (fprintf(fp, "MARK %d\n", mark_now) < 0) {
        return -1;
    }
    if (fprintf(fp, "SLOT lab\n") < 0) {
        return -1;
    }
    if (fprintf(fp, "STAMP %s\n", stamp) < 0) {
        return -1;
    }
    return 0;
}
