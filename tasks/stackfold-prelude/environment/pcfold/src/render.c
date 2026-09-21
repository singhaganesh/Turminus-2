#include "pcfold.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    sf_sym_t *syms;
    int count;
} sf_map_ro_t;

static int load_map_ro(const char *path, sf_map_ro_t *map)
{
    memset(map, 0, sizeof(*map));
    FILE *fp = fopen(path, "r");
    if (!fp) {
        return -1;
    }
    char line[512];
    if (!fgets(line, sizeof(line), fp) || strncmp(line, SF_MAGIC, strlen(SF_MAGIC)) != 0) {
        fclose(fp);
        return -1;
    }
    while (fgets(line, sizeof(line), fp)) {
        if (strncmp(line, "sym ", 4) != 0) {
            continue;
        }
        sf_sym_t sym = {0};
        unsigned long start = 0;
        unsigned long size = 0;
        if (sscanf(line, "sym %127s 0x%lx 0x%lx", sym.name, &start, &size) != 3) {
            continue;
        }
        sym.start = start;
        sym.size = size;
        sf_sym_t *next = realloc(map->syms, (size_t)(map->count + 1) * sizeof(sf_sym_t));
        if (!next) {
            fclose(fp);
            free(map->syms);
            return -1;
        }
        map->syms = next;
        map->syms[map->count++] = sym;
    }
    fclose(fp);
    return map->count > 0 ? 0 : -1;
}

static int resolve_pc(const sf_map_ro_t *map, unsigned long pc, char *sym_out, unsigned long *off_out)
{
    const sf_sym_t *best = NULL;
    for (int i = 0; i < map->count; i++) {
        const sf_sym_t *s = &map->syms[i];
        if (pc >= s->start && pc < s->start + s->size) {
            if (!best || s->start > best->start) {
                best = s;
            }
        }
    }
    if (!best) {
        for (int i = 0; i < map->count; i++) {
            const sf_sym_t *s = &map->syms[i];
            if (!best || s->start < best->start) {
                best = s;
            }
        }
    }
    if (!best) {
        return -1;
    }
    strncpy(sym_out, best->name, 127);
    sym_out[127] = '\0';
    *off_out = pc - best->start;
    return 0;
}

int sf_render(const char *samples_path, const char *symmap_path, const char *out_path)
{
    sf_map_ro_t map;
    if (load_map_ro(symmap_path, &map) != 0) {
        return -1;
    }
    FILE *in = fopen(samples_path, "r");
    if (!in) {
        free(map.syms);
        return -1;
    }
    FILE *out = fopen(out_path, "w");
    if (!out) {
        fclose(in);
        free(map.syms);
        return -1;
    }
    fprintf(out, "{\n  \"frames\": [\n");
    char line[256];
    int first = 1;
    while (fgets(line, sizeof(line), in)) {
        unsigned long pc = 0;
        if (sscanf(line, "pc 0x%lx", &pc) != 1) {
            continue;
        }
        char sym[128] = {0};
        unsigned long off = 0;
        if (resolve_pc(&map, pc, sym, &off) != 0) {
            continue;
        }
        if (!first) {
            fprintf(out, ",\n");
        }
        fprintf(out, "    {\"pc\": \"0x%lx\", \"symbol\": \"%s\", \"offset\": %lu}", pc, sym, off);
        first = 0;
    }
    fprintf(out, "\n  ]\n}\n");
    fclose(in);
    fclose(out);
    free(map.syms);
    return 0;
}
