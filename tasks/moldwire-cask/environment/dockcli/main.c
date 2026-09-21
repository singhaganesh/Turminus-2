#include <stdio.h>
#include <string.h>
#include <unistd.h>

int skim_run(const char *path, const char *stem);

int main(int argc, char **argv) {
    if (argc >= 2 && strcmp(argv[1], "bake") == 0) {
        execl("/opt/java/openjdk/bin/java", "java", "-cp", "/app/classes", "Bake", (char *)0);
        perror("java");
        return 127;
    }
    if (argc >= 2 && strcmp(argv[1], "skim") == 0) {
        const char *path = "/app/duskpit/dusk.bin";
        const char *stem = "pond";
        if (argc >= 3) {
            path = argv[2];
        }
        if (argc >= 4) {
            stem = argv[3];
        }
        return skim_run(path, stem);
    }
    fprintf(stderr, "usage: moldwire bake|skim\n");
    return 2;
}
