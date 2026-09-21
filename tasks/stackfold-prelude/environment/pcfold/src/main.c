#include "pcfold.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int usage(const char *argv0)
{
    fprintf(stderr, "usage: %s index --linked <elf> -o <symmap>\n", argv0);
    fprintf(stderr, "       %s index --objects <o>... -o <symmap>\n", argv0);
    fprintf(stderr, "       %s check <elf> <symmap>\n", argv0);
    fprintf(stderr, "       %s render <samples> <symmap> -o <profile>\n", argv0);
    return 1;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        return usage(argv[0]);
    }
    if (strcmp(argv[1], "index") == 0) {
        const char *out = NULL;
        if (argc >= 4 && strcmp(argv[2], "--linked") == 0) {
            for (int i = 4; i < argc; i++) {
                if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
                    out = argv[i + 1];
                }
            }
            if (!out) {
                return usage(argv[0]);
            }
            return sf_index_linked(argv[3], out) == 0 ? 0 : 1;
        }
        if (argc >= 4 && strcmp(argv[2], "--objects") == 0) {
            const char **objs = NULL;
            int obj_count = 0;
            for (int i = 3; i < argc; i++) {
                if (strcmp(argv[i], "-o") == 0) {
                    out = argv[i + 1];
                    break;
                }
                obj_count++;
            }
            if (!out || obj_count == 0) {
                return usage(argv[0]);
            }
            objs = calloc((size_t)obj_count, sizeof(char *));
            int idx = 0;
            for (int i = 3; i < argc; i++) {
                if (strcmp(argv[i], "-o") == 0) {
                    break;
                }
                objs[idx++] = argv[i];
            }
            int rc = sf_index_objects(objs, obj_count, out);
            free(objs);
            return rc == 0 ? 0 : 1;
        }
        return usage(argv[0]);
    }
    if (strcmp(argv[1], "check") == 0 && argc == 4) {
        return sf_check(argv[2], argv[3]);
    }
    if (strcmp(argv[1], "render") == 0 && argc >= 5) {
        const char *out = NULL;
        for (int i = 4; i < argc; i++) {
            if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) {
                out = argv[i + 1];
            }
        }
        if (!out) {
            return usage(argv[0]);
        }
        return sf_render(argv[2], argv[3], out) == 0 ? 0 : 1;
    }
    return usage(argv[0]);
}
