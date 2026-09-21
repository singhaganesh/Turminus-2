#include "tally.h"
#include "sheet.h"
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

static int count_sheet_lines(void) {
    const char *s = sheet_view();
    int n = 0;
    int nonempty = 0;
    for (; *s; s++) {
        if (*s == '\n') {
            if (nonempty) n++;
            nonempty = 0;
        } else if (*s != ' ' && *s != '\r') nonempty = 1;
    }
    if (nonempty) n++;
    return n;
}

int count_gap(void) {
    int a = count_sheet_lines();
    int b = count_emitters();
    return (b < a) ? 1 : 0;
}
