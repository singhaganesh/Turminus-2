#ifndef STAMP_H
#define STAMP_H

#ifdef __cplusplus
extern "C" {
#endif

int stamp_same(const char *path, unsigned long long old_sec);
unsigned long long stamp_sec(const char *path);
int stamp_zero(const char *path);

#ifdef __cplusplus
}
#endif

#endif
