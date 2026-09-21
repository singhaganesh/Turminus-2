#include "poke.h"
#include <stdio.h>
#include <string.h>

int fire_name(const char *name) {
    FILE *fp = fopen("/app/mintbay/runtime.lst", "r");
    if (!fp) return 1;
    char line[128];
    int hit = 0;
    while (fgets(line, sizeof line, fp)) {
        size_t n = strlen(line);
        while (n && (line[n - 1] == '\n' || line[n - 1] == '\r')) line[--n] = 0;
        if (strcmp(line, name) == 0) hit = 1;
    }
    fclose(fp);
    if (!hit) return 1;
    printf("fired:%s\n", name);
    return 0;
}
