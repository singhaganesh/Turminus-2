#include "gap.h"
#include "token.h"
#include <dirent.h>
#include <stdio.h>
#include <string.h>

static int is_lot_name(const char *n) {
    size_t L = strlen(n);
    return L > 4 && strcmp(n + L - 4, ".dmp") == 0;
}

int n_miss(void) {
    DIR *d = opendir("/app/lotbay");
    if (!d) return 1;
    struct dirent *ent;
    int lots = 0;
    while ((ent = readdir(d)) != NULL) {
        if (ent->d_name[0] == '.') continue;
        if (!is_lot_name(ent->d_name)) continue;
        char pth[PATH_MAX_X];
        snprintf(pth, sizeof pth, "/app/lotbay/%s", ent->d_name);
        char name[NAME_MAX], orig[PATH_MAX_X];
        int line = 0;
        if (parse_lot(pth, name, orig, &line) != 0) {
            closedir(d);
            return 1;
        }
        if (!file_here(orig)) {
            closedir(d);
            return 1;
        }
        lots++;
    }
    closedir(d);
    if (lots < 1) return 1;
    return 0;
}
