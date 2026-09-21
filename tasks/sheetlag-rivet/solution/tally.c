#include "tally.h"
#include <dirent.h>
#include <stdio.h>
#include <string.h>

static int count_emitters(void) {
    DIR *d = opendir("/app/rivetbay/emitters");
    int n = 0;
    struct dirent *ent;
    if (!d) return 0;
    while ((ent = readdir(d)) != NULL) {
        size_t L = strlen(ent->d_name);
        if (L > 5 && strcmp(ent->d_name + L - 5, ".kdec") == 0) n++;
    }
    closedir(d);
    return n;
}

static int count_evd(void) {
    DIR *d = opendir("/app/rivetbay/evd");
    int n = 0;
    struct dirent *ent;
    if (!d) return 0;
    while ((ent = readdir(d)) != NULL) {
        size_t L = strlen(ent->d_name);
        if (L > 4 && strcmp(ent->d_name + L - 4, ".evd") == 0) n++;
    }
    closedir(d);
    return n;
}

int count_gap(void) {
    int a = count_evd();
    int b = count_emitters();
    return (b < a) ? 1 : 0;
}
