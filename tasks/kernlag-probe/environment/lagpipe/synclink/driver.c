#include "common.h"

#include <stdio.h>
#include <string.h>

static int run_gen(void) {
    source_pick pick;
    const char *types_out = "/app/lagpipe/synctab_out/layout.tbl";
    const char *tag_out = "/app/lagpipe/synctab_out/procance.tag";
    FILE *tag_fp;

    if (choose_layout(&pick) != 0) {
        fprintf(stderr, "imprint: layout pick failed\n");
        return 1;
    }
    tag_fp = fopen(tag_out, "w");
    if (!tag_fp) {
        perror("imprint: procance.tag");
        return 1;
    }
    fprintf(tag_fp, "%s\n", pick.tag_value);
    fclose(tag_fp);
    if (write_types_tab(pick.layout_path, types_out, pick.tag_value) != 0) {
        fprintf(stderr, "imprint: types write failed\n");
        return 1;
    }
    if (rebuild_binary() != 0) {
        fprintf(stderr, "imprint: rebuild failed\n");
        return 1;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: kernscribe synctab | inspect <capture>\n");
        return 2;
    }
    if (strcmp(argv[1], "synctab") == 0) {
        return run_gen();
    }
    if (strcmp(argv[1], "inspect") == 0) {
        if (argc < 3) {
            fprintf(stderr, "usage: kernscribe inspect <capture>\n");
            return 2;
        }
        return emit_inspect_json(argv[2]);
    }
    fprintf(stderr, "unknown command: %s\n", argv[1]);
    return 2;
}
