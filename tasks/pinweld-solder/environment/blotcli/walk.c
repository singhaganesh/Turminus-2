#include "walk.h"
#include "load.h"
#include "token.h"
#include "gap.h"
#include "hoist.h"
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

static void slurp_cmd(const char *cmd, char *buf, size_t cap) {
    buf[0] = 0;
    FILE *fp = popen(cmd, "r");
    if (!fp) return;
    size_t used = 0;
    while (used + 1 < cap) {
        size_t got = fread(buf + used, 1, cap - 1 - used, fp);
        if (!got) break;
        used += got;
    }
    buf[used] = 0;
    pclose(fp);
}

void op_fill(void) {
    mkdir("/app/mintbay", 0755);
    char flags[8][512];
    (void)cfg_open(flags, 8);
    /* default core recipe only */
    const char *use = "-P -DCORE=1";

    FILE *log = fopen("/app/mintbay/scan.log", "w");
    char names[64][64];
    int n = 0;

    DIR *d = opendir("/app/ribunit");
    if (d) {
        struct dirent *ent;
        while ((ent = readdir(d)) != NULL) {
            size_t L = strlen(ent->d_name);
            if (L < 3 || strcmp(ent->d_name + L - 2, ".c") != 0) continue;
            char src[512];
            snprintf(src, sizeof src, "/app/ribunit/%s", ent->d_name);
            if (log) fprintf(log, "seen %s\n", src);
            char cmd[768];
            snprintf(cmd, sizeof cmd, "gcc -E %s -I/app/ribunit %s 2>/dev/null", use, src);
            char text[65536];
            slurp_cmd(cmd, text, sizeof text);
            char tmp[32][64];
            int k = pull_marks(text, tmp, 32);
            for (int i = 0; i < k && n < 64; i++) {
                memcpy(names[n], tmp[i], 64);
                n++;
            }
        }
        closedir(d);
    }
    if (log) fclose(log);
    sort_unique(names, &n);

    FILE *reg = fopen("/app/mintbay/points.reg", "w");
    FILE *lst = fopen("/app/mintbay/runtime.lst", "w");
    for (int i = 0; i < n; i++) {
        if (reg) fprintf(reg, "%s\n", names[i]);
        if (lst) fprintf(lst, "%s\n", names[i]);
    }
    if (reg) fclose(reg);
    if (lst) fclose(lst);
    copy_sidecar();
    int rc = n_miss("/app/mintbay/points.reg", names, n);
    if (rc != 0) exit(rc);
}
