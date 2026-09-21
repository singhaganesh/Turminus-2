#include "common.h"
#include "hdr_write.h"
#include "mix.h"
#include "note_write.h"
#include "rows_write.h"

#include <stdio.h>

int cmd_pour(void)
{
    char stamp[STAMP_LEN + 1];
    FILE *fp;

    if (mix_tag(DESC_PATH, stamp, sizeof(stamp)) != 0) {
        return 1;
    }
    fp = fopen(CAPSET_PATH, "w");
    if (fp == NULL) {
        return 1;
    }
    if (write_hdr(fp, stamp) != 0) {
        fclose(fp);
        return 1;
    }
    if (write_rows(fp, DESC_PATH) != 0) {
        fclose(fp);
        return 1;
    }
    fclose(fp);
    if (write_note(KNIT_OK_PATH, stamp) != 0) {
        return 1;
    }
    return 0;
}
