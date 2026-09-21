#include "discover.h"
#include "parse_evd.h"
#include <dirent.h>
#include <stdio.h>
#include <string.h>

static int stem_seen(const char *stem, char stems[][128], int n) {
    for (int i = 0; i < n; i++)
        if (strcmp(stems[i], stem) == 0) return 1;
    return 0;
}

static int load_prior_stems(char stems[][128], int cap) {
    int n = 0;
    FILE *f = fopen("/app/rivetbay/intake/current.ledger", "r");
    char line[1024];
    if (!f) return 0;
    while (n < cap && fgets(line, sizeof(line), f)) {
        char *bar = strchr(line, '|');
        if (!bar) continue;
        *bar = 0;
        char *s = line;
        while (*s == ' ' || *s == '\t') s++;
        if (*s == 0) continue;
        strncpy(stems[n], s, 127);
        stems[n][127] = 0;
        n++;
    }
    fclose(f);
    return n;
}

static int emit_row(FILE *out, const char *fname) {
    char path[512];
    snprintf(path, sizeof(path), "/app/rivetbay/evd/%s", fname);
    char name[128];
    char fields[512];
    if (parse_evd_file(path, name, fields, sizeof(fields)) != 0) return 0;
    fprintf(out, "%s|evd/%s|%s\n", name, fname, fields);
    return 1;
}

void discover_all(void) {
    char prior[64][128];
    char pending[64][256];
    int nprior = load_prior_stems(prior, 64);
    int npend = 0;
    DIR *d = opendir("/app/rivetbay/evd");
    FILE *out = fopen("/app/rivetbay/intake/current.ledger", "w");
    if (!d || !out) {
        if (d) closedir(d);
        if (out) fclose(out);
        return;
    }
    struct dirent *ent;
    while ((ent = readdir(d)) != NULL) {
        size_t L = strlen(ent->d_name);
        if (L < 5 || strcmp(ent->d_name + L - 4, ".evd") != 0) continue;
        char name[128];
        char fields[512];
        char path[512];
        snprintf(path, sizeof(path), "/app/rivetbay/evd/%s", ent->d_name);
        if (parse_evd_file(path, name, fields, sizeof(fields)) != 0) continue;
        if (stem_seen(name, prior, nprior)) continue;
        if (npend < 64) {
            strncpy(pending[npend], ent->d_name, 255);
            pending[npend][255] = 0;
            npend++;
        }
    }
    for (int i = 0; i < nprior; i++) {
        char want[256];
        snprintf(want, sizeof(want), "%s.evd", prior[i]);
        emit_row(out, want);
    }
    for (int i = 0; i < npend; i++)
        emit_row(out, pending[i]);
    fclose(out);
    closedir(d);
}
