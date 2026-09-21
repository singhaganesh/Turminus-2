#include "../lagpipe/synclink/common.h"

#include <stdio.h>
#include <string.h>

static int read_pin(char *release, size_t n) {
    FILE *fp = fopen("/app/snapvault/default.pin", "r");
    if (!fp) {
        return -1;
    }
    if (!fgets(release, (int)n, fp)) {
        fclose(fp);
        return -1;
    }
    fclose(fp);
    size_t len = strlen(release);
    while (len > 0 && (release[len - 1] == '\n' || release[len - 1] == '\r')) {
        release[--len] = '\0';
    }
    return 0;
}

static int read_running_release(char *release, size_t n) {
    FILE *fp = fopen("/app/livekern/running.release", "r");
    if (!fp) {
        return -1;
    }
    if (!fgets(release, (int)n, fp)) {
        fclose(fp);
        return -1;
    }
    fclose(fp);
    size_t len = strlen(release);
    while (len > 0 && (release[len - 1] == '\n' || release[len - 1] == '\r')) {
        release[--len] = '\0';
    }
    return 0;
}

static int live_export_present(void) {
    FILE *fp = fopen("/app/livekern/exports/sched_entity.tab", "r");
    if (!fp) {
        return 0;
    }
    fclose(fp);
    return 1;
}

static int layout_has_field(const char *path, const char *field) {
    FILE *fp = fopen(path, "r");
    char line[256];
    if (!fp) {
        return 0;
    }
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, field) != NULL) {
            fclose(fp);
            return 1;
        }
    }
    fclose(fp);
    return 0;
}

int choose_layout(source_pick *out) {
    char release[RELEASE_LEN];
    char running[RELEASE_LEN];

    if (!out) {
        return -1;
    }
    memset(out, 0, sizeof(*out));

    if (read_running_release(running, sizeof(running)) == 0 && live_export_present()) {
        if (!layout_has_field("/app/livekern/exports/sched_entity.tab", "migration_flags")) {
            fprintf(stderr, "imprint: live export missing required fields\n");
            return -1;
        }
        snprintf(out->layout_path, sizeof(out->layout_path),
                 "/app/livekern/exports/sched_entity.tab");
        snprintf(out->tag_value, sizeof(out->tag_value), "live:%s", running);
        out->from_bundle = 0;
        return 0;
    }

    if (read_pin(release, sizeof(release)) != 0) {
        return -1;
    }
    snprintf(out->layout_path, sizeof(out->layout_path),
             "/app/snapvault/releases/%s/sched_entity.tab", release);
    snprintf(out->tag_value, sizeof(out->tag_value), "bundle:%s", release);
    out->from_bundle = 1;
    return 0;
}
