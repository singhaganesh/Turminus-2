#ifndef ELFBITS_H
#define ELFBITS_H

int fill_text(const char *path, unsigned long long *vma, unsigned long long *off,
              unsigned long long *sz);
int name_at(const char *path, unsigned long long pc, char *out, int n);

#endif
