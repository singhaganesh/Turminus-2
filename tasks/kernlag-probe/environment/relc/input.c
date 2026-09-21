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

static void apply_policy_release(char *release, size_t n) {
    FILE *fp = fopen("/app/snapvault/policy.conf", "r");
    char line[128];
    char val[RELEASE_LEN];
    if (!fp) {
        return;
    }
    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "DEFAULT_RELEASE=%63s", val) == 1) {
            snprintf(release, n, "%s", val);
        }
    }
    fclose(fp);
}

int choose_layout(source_pick *out) {
    char release[RELEASE_LEN];
    char running[RELEASE_LEN];

    if (!out) {
        return -1;
    }
    memset(out, 0, sizeof(*out));

    if (read_pin(release, sizeof(release)) != 0) {
        return -1;
    }
    apply_policy_release(release, sizeof(release));

    if (read_running_release(running, sizeof(running)) == 0 &&
        strcmp(release, running) == 0) {
        snprintf(out->layout_path, sizeof(out->layout_path),
                 "/app/snapvault/releases/%s/sched_entity.tab", release);
        snprintf(out->tag_value, sizeof(out->tag_value), "live:%s", running);
        out->from_bundle = 1;
        return 0;
    }

    snprintf(out->layout_path, sizeof(out->layout_path),
             "/app/snapvault/releases/%s/sched_entity.tab", release);
    snprintf(out->tag_value, sizeof(out->tag_value), "bundle:%s", release);
    out->from_bundle = 1;
    return 0;
}
