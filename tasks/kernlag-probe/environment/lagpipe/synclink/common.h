#ifndef KERN_FORGE_COMMON_H
#define KERN_FORGE_COMMON_H

#include <stddef.h>

#define LAYOUT_PATH_LEN 512
#define TAG_PATH_LEN 512
#define RELEASE_LEN 64
#define FIELD_MAX 16

typedef struct {
    char name[64];
    char kind[16];
    unsigned off;
    unsigned size;
} field_def;

typedef struct {
    char struct_name[64];
    field_def fields[FIELD_MAX];
    int nfields;
} layout_def;

typedef struct {
    char layout_path[LAYOUT_PATH_LEN];
    char tag_value[RELEASE_LEN];
    int from_bundle;
} source_pick;

int choose_layout(source_pick *out);
int parse_layout(const char *path, layout_def *layout);
int write_types_tab(const char *layout_path, const char *out_path, const char *tag_value);
int emit_inspect_json(const char *inspect_path);
int rebuild_binary(void);

#endif
