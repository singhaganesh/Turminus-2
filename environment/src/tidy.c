#include "tidy.h"
#include "util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void tidy_report(const char *ledger_path) {
    size_t n = 0;
    char *raw = read_file(ledger_path, &n);
    if (!raw) {
        fprintf(stderr, "doctor: read failed\n");
        return;
    }
    int bom = n >= 3 && (unsigned char)raw[0] == 0xEF && (unsigned char)raw[1] == 0xBB &&
              (unsigned char)raw[2] == 0xBF;
    size_t crlf = 0;
    size_t lf = 0;
    for (size_t i = 0; i < n; i++) {
        if (raw[i] == '\n') {
            lf++;
            if (i > 0 && raw[i - 1] == '\r') {
                crlf++;
            }
        }
    }
    printf("ledger=%s bom=%d crlf_lines=%zu lf_breaks=%zu\n", ledger_path, bom, crlf, lf);
    free(raw);
}

int tidy_rewrite_lf(const char *ledger_path) {
    size_t n = 0;
    char *raw = read_file(ledger_path, &n);
    if (!raw) {
        return 1;
    }
    size_t start = 0;
    if (n >= 3 && (unsigned char)raw[0] == 0xEF && (unsigned char)raw[1] == 0xBB &&
        (unsigned char)raw[2] == 0xBF) {
        start = 3;
    }
    FILE *out = fopen(ledger_path, "wb");
    if (!out) {
        free(raw);
        return 1;
    }
    for (size_t i = start; i < n; i++) {
        if (raw[i] == '\r') {
            continue;
        }
        fputc(raw[i], out);
    }
    fclose(out);
    free(raw);
    return 0;
}
