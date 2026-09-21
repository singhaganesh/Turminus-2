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

static void sync_emit_sheet_from_ledger(void) {
    FILE *f = fopen("/app/rivetbay/intake/current.ledger", "r");
    char line[1024];
    size_t used = 0;
    g_emit[0] = 0;
    if (!f) return;
    while (fgets(line, sizeof(line), f)) {
        char *s = line;
        while (*s == ' ' || *s == '\t') s++;
        if (*s == 0 || *s == '\n') continue;
        size_t L = strlen(s);
        if (used + L + 1 >= sizeof(g_emit)) break;
        memcpy(g_emit + used, s, L);
        used += L;
        if (g_emit[used - 1] != '\n') {
            g_emit[used++] = '\n';
            g_emit[used] = 0;
        }
    }
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
    sync_emit_sheet_from_ledger();
    g_emit_cap = count_nonempty_lines(g_emit);
}

const char *sheet_view(void) {
    return g_emit;
}

int sheet_emit_cap(void) {
    return g_emit_cap;
}
