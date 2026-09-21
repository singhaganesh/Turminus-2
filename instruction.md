# Anvil focus index

Anvil under `/srv/anvil` stores focus events as NDJSON and builds a companion byte-offset index. Ops runs `/srv/anvil/bin/anvil index <ledger> <index>` then `/srv/anvil/bin/anvil roster <ledger> <index> <tag> <out.json>` (typical paths: `/srv/anvil/fixtures/focus.ndjson`, `/srv/anvil/var/focus.idx`, `/srv/anvil/var/roster.json`).

On mixed checkouts, CRLF files and a leading UTF-8 BOM make selections miss names, land on the wrong JSON line, or emit extras; LF-only files without a BOM still look correct. Multi-byte UTF-8 inside fields also moves later selections. Fix C sources under `/srv/anvil` (start with the index and selection packages in `/srv/anvil/src` and `/srv/anvil/include`) so index and selection regenerate correctly through `/srv/anvil/bin/anvil`. The index and selection modules must behave correctly when driven by that binary, not only via hand-written outputs. Static hand-written index or selection JSON files are not enough. After edits, run `make -C /srv/anvil reforge`. Stay offline. The image builds from `environment/` into `/srv/anvil`.


Index lines are `id`, then a tab, then a decimal byte offset, sorted by `id` ascending (ties by offset ascending). Offsets are byte counts from the start of the ledger file to the first byte of that record; BOM bytes count when present; CR and LF each count. Roster JSON has sorted `ids` for records whose `tag` equals the request, plus `count`. When the same `id` appears more than once, keep the last record in file order. Do not strip the BOM from the ledger as a fix.
