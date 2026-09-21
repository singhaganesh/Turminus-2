# Offset contract

The focus index is a byte-oriented companion to the NDJSON ledger.

- Offsets are counted from byte zero of the on-disk ledger file.
- A UTF-8 BOM (EF BB BF), when present, occupies the first three bytes.
- Both CR (0x0D) and LF (0x0A) are ordinary bytes in the offset arithmetic.
- Record payloads are UTF-8 JSON objects; multi-byte code points consume multiple
  offset bytes.

The `doctor` subcommand and `tidy_rewrite_lf` helper can rewrite a ledger for
human inspection. Index and roster must read the ledger bytes as stored.
