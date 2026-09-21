#include <stdio.h>
#include <string.h>

int cmd_pour(void);
int cmd_spin(int argc, char **argv);

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: nockreel pour|spin ...\n");
        return 2;
    }
    if (strcmp(argv[1], "pour") == 0) {
        return cmd_pour();
    }
    if (strcmp(argv[1], "spin") == 0) {
        return cmd_spin(argc - 2, argv + 2);
    }
    fprintf(stderr, "unknown subcommand\n");
    return 2;
}
