#include "load.h"
#include <dirent.h>
#include <stdio.h>
#include <string.h>

int cfg_open(char out[][512], int max) {
    DIR *d = opendir("/app/recipath");
    if (!d) return 0;
    char files[16][256];
    int nf = 0;
    struct dirent *ent;
    while ((ent = readdir(d)) != NULL) {
        size_t L = strlen(ent->d_name);
        if (L > 6 && strcmp(ent->d_name + L - 6, ".flags") == 0 && nf < 16) {
            snprintf(files[nf], sizeof files[0], "%s", ent->d_name);
            nf++;
        }
    }
    closedir(d);
    for (int i = 0; i < nf; i++) {
        for (int j = i + 1; j < nf; j++) {
            if (strcmp(files[j], files[i]) < 0) {
                char tmp[256];
                memcpy(tmp, files[i], 256);
                memcpy(files[i], files[j], 256);
                memcpy(files[j], tmp, 256);
            }
        }
    }
    /* first recipe only — core.flags after sort */
    if (nf == 0 || max < 1) return 0;
    char path[512];
    snprintf(path, sizeof path, "/app/recipath/%s", files[0]);
    FILE *fp = fopen(path, "r");
    if (!fp) return 0;
    if (!fgets(out[0], 512, fp)) {
        fclose(fp);
        return 0;
    }
    fclose(fp);
    size_t n = strlen(out[0]);
    while (n && (out[0][n - 1] == '\n' || out[0][n - 1] == '\r')) {
        out[0][--n] = 0;
    }
    return 1;
}
