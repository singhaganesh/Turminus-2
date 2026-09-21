#include "sheet.h"
#include <stdio.h>
#include <string.h>

static char g_primed[65536];
static char g_emit[65536];
static int g_emit_cap;

static int count_nonempty_lines(const char *blob) {
    int n = 0;
    int nonempty = 0;
    for (const char *s = blob; *s; s++) {
        if (*s == '\n') {
            if (nonempty) n++;
            nonempty = 0;
        } else if (*s != ' ' && *s != '\r' && *s != '\t') {
            nonempty = 1;
        }
    }
    if (nonempty) n++;
    return n;
}

static void load_mill_open_into(char *dst, size_t cap) {
    FILE *f = fopen("/app/rivetbay/intake/mill_open", "r");
    dst[0] = 0;
    if (!f) return;
    size_t n = fread(dst, 1, cap - 1, f);
    dst[n] = 0;
    fclose(f);
}

void prime_intake_sheet(void) {
    load_mill_open_into(g_primed, sizeof(g_primed));
    g_emit_cap = count_nonempty_lines(g_primed);
    g_emit[0] = 0;
}

void grab_sheet(void) {
    load_mill_open_into(g_primed, sizeof(g_primed));
}

void pour_sheet(void) {
    char buf[65536];
    char out[65536];
    strncpy(buf, g_primed, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = 0;
    size_t w = 0;
    char *save = NULL;
    char *line = strtok_r(buf, "\n", &save);
    while (line) {
        while (*line == ' ' || *line == '\t') line++;
        if (*line == 0) {
            line = strtok_r(NULL, "\n", &save);
            continue;
        }
        size_t L = strlen(line);
        if (w + L + 1 >= sizeof(out)) break;
        memcpy(out + w, line, L);
        w += L;
        out[w++] = '\n';
        line = strtok_r(NULL, "\n", &save);
    }
    out[w] = 0;
    memcpy(g_emit, out, w + 1);
}

const char *sheet_view(void) {
    return g_emit;
}

int sheet_emit_cap(void) {
    return g_emit_cap;
}
