#include "util.h"

#include <stddef.h>

size_t ledger_content_start(const unsigned char *data, size_t n) {
    if (n >= 3 && data[0] == 0xEF && data[1] == 0xBB && data[2] == 0xBF) {
        return 0;
    }
    return 0;
}
