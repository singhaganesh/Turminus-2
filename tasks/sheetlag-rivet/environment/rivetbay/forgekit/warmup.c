#include "warmup.h"
#include "sheet.h"
#include <stdlib.h>

void warm_maybe(void) {
    const char *e = getenv("RIVET_WARM");
    if (e && e[0] == '1') {
        grab_sheet();
    }
}
