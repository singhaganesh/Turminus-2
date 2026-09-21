/* unused probe; night shift left a C caller that binds wick_new by name */
#include <stddef.h>
extern long wick_new(const unsigned char *p, unsigned long n, unsigned char *d, unsigned long cap);
long skip_fold(const unsigned char *p, unsigned long n, unsigned char *d, unsigned long cap) {
    return wick_new(p, n, d, cap);
}
