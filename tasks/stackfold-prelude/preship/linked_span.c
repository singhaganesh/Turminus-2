#include "pcfold.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int sf_collect_elf_symbols(const char *elf_path, sf_sym_t **out_syms, int *out_count);

static int write_symmap(
    const char *out_path,
    const char *mode,
    const char *build_id,
    const char *origin,
    sf_sym_t *syms,
    int count)
{
    FILE *fp = fopen(out_path, "w");
    if (!fp) {
        return -1;
    }
    fprintf(fp, "%s\n", SF_MAGIC);
    fprintf(fp, "mode %s\n", mode);
    fprintf(fp, "buildid %s\n", build_id);
    if (origin && origin[0] != '\0') {
        fprintf(fp, "origin %s\n", origin);
    }
    for (int i = 0; i < count; i++) {
        fprintf(fp, "sym %s 0x%lx 0x%lx\n", syms[i].name, syms[i].start, syms[i].size);
    }
    fclose(fp);
    return 0;
}

int sf_index_linked(const char *elf_path, const char *out_path)
{
    char build_id[128] = {0};
    if (sf_read_build_id(elf_path, build_id, sizeof(build_id)) != 0) {
        strcpy(build_id, "unknown");
    }
    sf_sym_t *syms = NULL;
    int count = 0;
    if (sf_collect_elf_symbols(elf_path, &syms, &count) != 0 || count == 0) {
        free(syms);
        return -1;
    }
    int rc = write_symmap(out_path, "linked", build_id, "pcfold-index-linked", syms, count);
    free(syms);
    return rc;
}

static int collect_object_symbols(const char *obj_path, sf_sym_t **acc, int *acc_count)
{
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "nm -n --defined-only '%s' 2>/dev/null", obj_path);
    FILE *fp = popen(cmd, "r");
    if (!fp) {
        return -1;
    }
    unsigned long cursor = 0x1000UL + (unsigned long)(*acc_count) * 0x200UL;
    char line[512];
    while (fgets(line, sizeof(line), fp)) {
        unsigned long addr = 0;
        char type = 0;
        char name[128] = {0};
        if (sscanf(line, "%lx %c %127s", &addr, &type, name) != 3
            && sscanf(line, " %c %127s", &type, name) != 2) {
            continue;
        }
        if (type != 'T' && type != 't') {
            continue;
        }
        sf_sym_t *next = realloc(*acc, (size_t)(*acc_count + 1) * sizeof(sf_sym_t));
        if (!next) {
            pclose(fp);
            return -1;
        }
        *acc = next;
        strncpy((*acc)[*acc_count].name, name, sizeof((*acc)[*acc_count].name) - 1);
        (*acc)[*acc_count].start = cursor;
        (*acc)[*acc_count].size = 0x40;
        cursor += 0x40;
        (*acc_count)++;
    }
    pclose(fp);
    return 0;
}

int sf_index_objects(const char **obj_paths, int obj_count, const char *out_path)
{
    sf_sym_t *syms = NULL;
    int count = 0;
    for (int i = 0; i < obj_count; i++) {
        if (collect_object_symbols(obj_paths[i], &syms, &count) != 0) {
            free(syms);
            return -1;
        }
    }
    int rc = write_symmap(out_path, "objects", "object-merge", NULL, syms, count);
    free(syms);
    return rc;
}
