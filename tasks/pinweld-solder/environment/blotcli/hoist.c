#include "hoist.h"
#include <stdio.h>

void copy_sidecar(void) {
    FILE *fp = fopen("/app/mintbay/hoist.note", "w");
    if (!fp) return;
    fputs("always-on copy helper\n", fp);
    fclose(fp);
}
