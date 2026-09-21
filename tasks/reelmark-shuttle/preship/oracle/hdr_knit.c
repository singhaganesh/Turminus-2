#include "hdr_write.h"

#include <stdio.h>
#include <string.h>

int write_hdr(FILE *fp, const char *stamp)
{
    const int mark_now = 4;

    if (fp == NULL || stamp == NULL || stamp[0] == '\0') {
        return -1;
    }
    if (strlen(stamp) != 8) {
        return -1;
    }
    if (fprintf(fp, "REEL\n") < 0) {
        return -1;
    }
    if (fprintf(fp, "MARK %d\n", mark_now) < 0) {
        return -1;
    }
    if (fprintf(fp, "SLOT knit\n") < 0) {
        return -1;
    }
    if (fprintf(fp, "STAMP %s\n", stamp) < 0) {
        return -1;
    }
    return 0;
}
