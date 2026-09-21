#include "utf_tidy.h"
#include <string.h>
void tidy_copy(const char *src, char *dst, int n) {
    if (n <= 0) return;
    strncpy(dst, src, (size_t)n - 1);
    dst[n - 1] = 0;
}
