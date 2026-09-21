#include "common.h"

#include <stdlib.h>

int rebuild_binary(void) {
    return system("make -C /app/lagpipe bind >/dev/null 2>&1");
}
