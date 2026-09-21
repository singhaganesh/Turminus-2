#ifndef ANVIL_UTIL_H
#define ANVIL_UTIL_H

#include <stddef.h>
#include <stdint.h>

typedef struct {
    char *id;
    int64_t offset;
} IdxEntry;

typedef struct {
    char *id;
    char *tag;
    int64_t offset;
} Rec;

char *read_file(const char *path, size_t *n);
int extract_string_field(const char *json, const char *key, char *out, size_t out_n);
int utf8_rune_count(const char *s, size_t n);
size_t ledger_content_start(const unsigned char *data, size_t n);

#endif
