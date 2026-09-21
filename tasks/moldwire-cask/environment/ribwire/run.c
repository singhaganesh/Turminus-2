#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#include "reg.inc"

int skim_run(const char *path, const char *stem) {
    FILE *in;
    FILE *out;
    unsigned char *buf;
    long n;
    int rc;

    in = fopen(path, "rb");
    if (in == NULL) {
        return 2;
    }
    if (fseek(in, 0, SEEK_END) != 0) {
        fclose(in);
        return 2;
    }
    n = ftell(in);
    if (n < 0) {
        fclose(in);
        return 2;
    }
    rewind(in);
    buf = malloc((size_t)n + 1);
    if (buf == NULL) {
        fclose(in);
        return 2;
    }
    if (fread(buf, 1, (size_t)n, in) != (size_t)n) {
        free(buf);
        fclose(in);
        return 2;
    }
    fclose(in);
    mkdir("/app/jsonpit", 0755);
    out = fopen("/app/jsonpit/skim.json", "w");
    if (out == NULL) {
        free(buf);
        return 2;
    }
    rc = call_skim(stem, buf, (size_t)n, out);
    fclose(out);
    free(buf);
    return rc;
}
