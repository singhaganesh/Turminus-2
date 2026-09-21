#include "mtime.h"
#include <string.h>

int pick_last(Row *rows, int n, const char *name) {
    int idx = -1;
    for (int i = 0; i < n; i++) {
        if (strcmp(rows[i].name, name) == 0) idx = i;
    }
    return idx;
}
