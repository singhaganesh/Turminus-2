#include "stock.h"

#include <string.h>

int stock_has(const char *name)
{
    static const char *rows[] = {"sys_read", "sys_write", NULL};
    int i;

    if (name == NULL) {
        return 0;
    }
    for (i = 0; rows[i] != NULL; i++) {
        if (strcmp(rows[i], name) == 0) {
            return 1;
        }
    }
    return 0;
}
