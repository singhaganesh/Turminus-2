#ifndef ANVIL_TIDY_H
#define ANVIL_TIDY_H

/* Interactive cleanup helpers — not part of index/roster contract. */
int tidy_rewrite_lf(const char *ledger_path);
void tidy_report(const char *ledger_path);

#endif
