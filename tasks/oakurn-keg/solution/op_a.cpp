#include "admit.hpp"

#include <errno.h>
#include <fcntl.h>
#include <unistd.h>

int op_a(void) {
    for (int i = 0; i < 8; i++) {
        int fd = open("/app/snapvat/busy.latch", O_RDONLY);
        if (fd < 0) {
            if (errno == ENOENT) {
                return 0;
            }
            return 1;
        }
        close(fd);
    }
    return 0;
}
