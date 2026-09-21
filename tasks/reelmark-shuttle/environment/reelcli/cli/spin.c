#include "common.h"
#include "sel.h"
#include "stock.h"
#include "xin.h"

#include <stdio.h>
#include <string.h>
#include <unistd.h>

static int blob_has(const char *path, const char *name)
{
    FILE *fp;
    char line[LINE_LEN];
    char row_name[NAME_LEN];
    int id;
    char cls[32];

    fp = fopen(path, "r");
    if (fp == NULL) {
        return 0;
    }
    while (fgets(line, sizeof(line), fp) != NULL) {
        if (strncmp(line, "CALL ", 5) != 0) {
            continue;
        }
        if (sscanf(line + 5, "%63s %d %31s", row_name, &id, cls) >= 2) {
            if (strcmp(row_name, name) == 0) {
                fclose(fp);
                return 1;
            }
        }
    }
    fclose(fp);
    return 0;
}

static int read_spool_call(const char *path, char *name, unsigned name_len)
{
    FILE *fp;
    char line[LINE_LEN];

    fp = fopen(path, "r");
    if (fp == NULL) {
        return -1;
    }
    if (fgets(line, sizeof(line), fp) == NULL) {
        fclose(fp);
        return -1;
    }
    fclose(fp);
    if (sscanf(line, "%63s", name) != 1) {
        return -1;
    }
    if (strlen(name) >= name_len) {
        return -1;
    }
    return 0;
}

int cmd_spin(int argc, char **argv)
{
    const char *blob = CAPSET_PATH;
    const char *spool = NULL;
    char call[NAME_LEN];
    char stamp[32];
    int mark = 0;
    int admit_rc;
    int bank;
    int covered;
    const char *st;
    const char *prefix;
    FILE *fp;

    stamp[0] = '\0';
    if (argc >= 2 && strcmp(argv[0], "--blob") == 0) {
        blob = argv[1];
        spool = (argc >= 3) ? argv[2] : NULL;
    } else if (argc >= 1) {
        spool = argv[0];
    }
    if (spool == NULL) {
        fprintf(stderr, "usage: nockreel spin [--blob PATH] SPOOL\n");
        return 2;
    }
    unlink(ACCEPT_PATH);
    if (read_spool_call(spool, call, sizeof(call)) != 0) {
        return 2;
    }
    admit_rc = xin_blob(blob, &mark, stamp, sizeof(stamp));
    if (admit_rc < 0) {
        return 2;
    }
    bank = sel_bank(admit_rc);
    if (bank == 0) {
        covered = blob_has(blob, call);
        prefix = "table:";
    } else {
        covered = stock_has(call);
        prefix = "builtin:";
        snprintf(stamp, sizeof(stamp), "stock");
    }
    st = covered ? "replayed" : "unsupported";
    printf("{\"loaded\":\"%s%s\",\"status\":\"%s\",\"call\":\"%s\"}\n",
           prefix, stamp, st, call);
    fp = fopen(LOADED_SET_PATH, "w");
    if (fp != NULL) {
        fprintf(fp, "%s%s\n", prefix, stamp);
        fclose(fp);
    }
    if (admit_rc == 0 && bank == 0) {
        fp = fopen(ACCEPT_PATH, "w");
        if (fp != NULL) {
            fputs("1\n", fp);
            fclose(fp);
        }
    }
    (void)mark;
    return 0;
}
