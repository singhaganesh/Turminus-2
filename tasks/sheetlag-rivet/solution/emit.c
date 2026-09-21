#include "emit.h"
#include "sheet.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void write_spec_fields(FILE *o, char *spec) {
    char *tok = strtok(spec, ",");
    while (tok) {
        char fn[64], k[16];
        if (sscanf(tok, "%63[^:]:%15s", fn, k) == 2)
            fprintf(o, "%s %s\n", fn, k);
        tok = strtok(NULL, ",");
    }
}

static void emit_one(const char *line) {
    char tmp[1024];
    strncpy(tmp, line, sizeof(tmp) - 1);
    tmp[sizeof(tmp) - 1] = 0;
    char *nl = strchr(tmp, '\n');
    if (nl) *nl = 0;
    char *name = tmp;
    char *p1 = strchr(tmp, '|');
    if (!p1) return;
    *p1 = 0;
    char *p2 = strchr(p1 + 1, '|');
    if (!p2) return;
    char *spec = p2 + 1;
    char outp[512];
    snprintf(outp, sizeof(outp), "/app/rivetbay/emitters/%s.kdec", name);
    FILE *o = fopen(outp, "w");
    if (!o) return;
    fprintf(o, "KDEC1\nNAME %s\n", name);
    write_spec_fields(o, spec);
    fclose(o);
}

void emit_all(void) {
    const char *blob = sheet_view();
    int cap = sheet_emit_cap();
    char buf[65536];
    strncpy(buf, blob, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = 0;
    char *save = NULL;
    char *line = strtok_r(buf, "\n", &save);
    int idx = 0;
    while (line) {
        if (idx >= cap) break;
        if (line[0]) emit_one(line);
        idx++;
        line = strtok_r(NULL, "\n", &save);
    }
}
