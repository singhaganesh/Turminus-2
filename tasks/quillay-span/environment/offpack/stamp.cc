#include "stamp.h"

#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>
#include <utime.h>

unsigned long long stamp_sec(const char *path) {
  struct stat st;
  if (stat(path, &st) != 0) return 0;
  return (unsigned long long)st.st_mtime;
}

int stamp_same(const char *path, unsigned long long old_sec) {
  return stamp_sec(path) == old_sec;
}

int stamp_zero(const char *path) {
  struct utimbuf u;
  u.actime = 0;
  u.modtime = 0;
  return utime(path, &u);
}
