#include "discover.h"
#include "sheet.h"
#include "emit.h"
#include "tally.h"
#include "decode.h"
#include "warmup.h"
#include <stdio.h>
#include <string.h>

static void note_mill_pass(void) {
    FILE *f = fopen("/app/rivetbay/intake/.mill_pass", "a");
    if (!f) return;
    fputc('1', f);
    fputc('\n', f);
    fclose(f);
}

int main(int argc, char **argv) {
    if (argc >= 2 && strcmp(argv[1], "mill") == 0) {
        note_mill_pass();
        warm_maybe();
        prime_intake_sheet();
        discover_all();
        pour_sheet();
        emit_all();
        return count_gap();
    }
    if (argc >= 3 && strcmp(argv[1], "decode") == 0)
        return decode_frame(argv[2]);
    fprintf(stderr, "usage: rivetbay mill | rivetbay decode <frame>\n");
    return 2;
}
