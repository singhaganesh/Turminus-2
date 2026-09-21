#include "admit.hpp"

#include <errno.h>
#include <fcntl.h>
#include <unistd.h>

int op_a(void) {
    int fd = open("/app/snapvat/busy.latch", O_RDONLY);
    if (fd >= 0) {
        close(fd);
        return 1;
    }
    if (errno != ENOENT) {
        return 1;
    }
    return 0;
}
