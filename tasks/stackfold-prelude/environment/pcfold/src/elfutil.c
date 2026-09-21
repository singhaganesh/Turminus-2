#include "pcfold.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int hex_nibble(char c)
{
    if (c >= '0' && c <= '9') {
        return c - '0';
    }
    if (c >= 'a' && c <= 'f') {
        return 10 + (c - 'a');
    }
    if (c >= 'A' && c <= 'F') {
        return 10 + (c - 'A');
    }
    return -1;
}

int sf_read_build_id(const char *elf_path, char *out, size_t out_len)
{
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "readelf -n '%s' 2>/dev/null", elf_path);
    FILE *fp = popen(cmd, "r");
    if (!fp) {
        return -1;
    }
    char line[512];
    while (fgets(line, sizeof(line), fp)) {
        char *p = strstr(line, "Build ID:");
        if (!p) {
            continue;
        }
        p += 9;
        while (*p && isspace((unsigned char)*p)) {
            p++;
        }
        size_t n = 0;
        while (p[n] && !isspace((unsigned char)p[n]) && n + 1 < out_len) {
            out[n] = p[n];
            n++;
        }
        out[n] = '\0';
        pclose(fp);
        return n > 0 ? 0 : -1;
    }
    pclose(fp);
    return -1;
}

int sf_collect_elf_symbols(const char *elf_path, sf_sym_t **out_syms, int *out_count)
{
    char cmd[512];
    snprintf(cmd, sizeof(cmd), "nm -n --defined-only '%s' 2>/dev/null", elf_path);
    FILE *fp = popen(cmd, "r");
    if (!fp) {
        return -1;
    }
    sf_sym_t *buf = NULL;
    int cap = 0;
    int count = 0;
    char line[512];
    while (fgets(line, sizeof(line), fp)) {
        unsigned long addr = 0;
        char type = 0;
        char name[128] = {0};
        if (sscanf(line, "%lx %c %127s", &addr, &type, name) != 3) {
            continue;
        }
        if (type != 'T' && type != 't') {
            continue;
        }
        if (count >= cap) {
            cap = cap ? cap * 2 : 32;
            sf_sym_t *next = realloc(buf, (size_t)cap * sizeof(sf_sym_t));
            if (!next) {
                free(buf);
                pclose(fp);
                return -1;
            }
            buf = next;
        }
        strncpy(buf[count].name, name, sizeof(buf[count].name) - 1);
        buf[count].start = addr;
        buf[count].size = 0;
        count++;
    }
    pclose(fp);
    for (int i = 0; i < count; i++) {
        unsigned long end = (i + 1 < count) ? buf[i + 1].start : buf[i].start + 64;
        if (end > buf[i].start) {
            buf[i].size = end - buf[i].start;
        } else {
            buf[i].size = 64;
        }
    }
    *out_syms = buf;
    *out_count = count;
    return 0;
}
