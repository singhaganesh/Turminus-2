#include "mix.h"

#include <stdio.h>
#include <stdint.h>

int mix_tag(const char *path, char *out, unsigned out_len)
{
    FILE *fp;
    uint32_t h = 2166136261u;
    int c;

    if (path == NULL || out == NULL || out_len < 9) {
        return -1;
    }
    fp = fopen(path, "r");
    if (fp == NULL) {
        return -1;
    }
    while ((c = fgetc(fp)) != EOF) {
        h ^= (unsigned char)c;
        h *= 16777619u;
    }
    fclose(fp);
    if (snprintf(out, out_len, "%08x", h) < 0) {
        return -1;
    }
    return 0;
}
