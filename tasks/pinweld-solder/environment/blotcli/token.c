#include "token.h"
#include <string.h>
#include <stdlib.h>

int pull_marks(const char *text, char names[][64], int max) {
    int n = 0;
    const char *p = text;
    while (p && *p && n < max) {
        const char *hit = strstr(p, "weld_mark_");
        if (!hit) break;
        hit += 10;
        int len = 0;
        while ((hit[len] >= 'a' && hit[len] <= 'z') ||
               (hit[len] >= 'A' && hit[len] <= 'Z') ||
               (hit[len] >= '0' && hit[len] <= '9') ||
               hit[len] == '_') {
            len++;
        }
        if (len > 0 && len < 63) {
            memcpy(names[n], hit, (size_t)len);
            names[n][len] = 0;
            n++;
        }
        p = hit + (len ? len : 1);
    }
    return n;
}

static int cmpstr(const void *a, const void *b) {
    return strcmp((const char *)a, (const char *)b);
}

void sort_unique(char names[][64], int *n) {
    if (*n <= 0) return;
    qsort(names, (size_t)*n, 64, cmpstr);
    int w = 1;
    for (int i = 1; i < *n; i++) {
        if (strcmp(names[i], names[w - 1]) != 0) {
            memcpy(names[w], names[i], 64);
            w++;
        }
    }
    *n = w;
}
