#ifndef PCFOLD_H
#define PCFOLD_H

#include <stddef.h>

#define SF_MAGIC "PCFOLD1"

typedef struct {
    char name[128];
    unsigned long start;
    unsigned long size;
} sf_sym_t;

int sf_read_build_id(const char *elf_path, char *out, size_t out_len);
int sf_index_linked(const char *elf_path, const char *out_path);
int sf_index_objects(const char **obj_paths, int obj_count, const char *out_path);
int sf_check(const char *elf_path, const char *symmap_path);
int sf_render(const char *samples_path, const char *symmap_path, const char *out_path);

#endif
