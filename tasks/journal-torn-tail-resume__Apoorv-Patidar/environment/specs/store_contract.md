# wrenkv store contract

This document is normative for every process that touches a wrenkv store
directory. The CLI is `/app/bin/wrenkv`; its subcommands and flags are frozen:

```
wrenkv load DIR --ops FILE [--crash-after N | --crash-tail N]
wrenkv recover DIR [--crash-after N]
wrenkv compact DIR [--crash-after N]
wrenkv dump DIR
```

Exit codes: `0` success, `2` usage error, missing store directory, or invalid
ops input, `67` the deterministic kill used by the crash flags. Any other
exit code from `recover` or `dump` is a defect.

## Store directory layout

A store directory holds up to three kinds of files:

- `append.log` — the append-only operation log. Never rewritten in place,
  only appended to or cleared as a whole during a fold.
- `base-<gen>.tbl` — immutable baked generations. Generation 1 is the first
  bake; every bake creates the next generation and never mutates an older
  one.
- `keep.json` — the coordination record. Written atomically (temporary file,
  fenced, then renamed). Fields:
  - `gen` — generation counter, bumped by every bake.
  - `base_file` — file name of the current baked generation (`null` on a
    store that has never been baked).
  - `covered_seq` — highest record sequence number baked into `base_file`.
  - `log_bytes` — size of `append.log` at the moment the coordination record
    was written. Informational.

A store directory with none of these files is a fresh store: it reads as
empty with `covered_seq` 0.

## Operations and sequence numbers

An ops file holds `put KEY VALUE`, `del KEY`, and `incr KEY DELTA` lines.
Keys match `[A-Za-z0-9._:-]{1,64}`; values are 1..256 bytes with no
whitespace; deltas are signed integers. Blank lines and `#` comments are
skipped, and every line is validated before any store work starts. Every
applied operation
gets the next sequence number, starting at 1. `incr` reads the current value
of the key: absent counts as `0`, and a value that is not an integer is a
load error (exit 2) at that operation. Every operation before the failing
one stays durable. `del` of an absent key is recorded but changes nothing.

## Fences and the crash flags

A fence flushes a buffered handle to stable storage. It is the only
durability primitive; anything not behind a fence may be lost when a process
dies. The crash flags make a process die deterministically, mid-flight, with
exit 67:

- `--crash-after N` — die immediately after the process completes its Nth
  fence. `N = 0` dies before the first fence.
- `--crash-tail N` (load only) — after the first N operations are each
  individually fenced, write only the first half of the next record and die.
  This simulates a torn trailing record. If the ops file has no record after
  the first N, the load completes normally.

The loader acknowledges and fences every operation individually: after a
`--crash-after N` kill, exactly the first N operations of that load are
durable, and after a `--crash-tail N` kill, exactly the first N operations
are durable and the log ends in a torn record.

## Read path

A reader merges the baked generation named by the coordination record with
every log record whose sequence number is greater than the record's
`covered_seq`, in sequence order. `put` overwrites the row and stamps it with
the record's sequence number (`rev`), `incr` folds the delta into the
current value and stamps it, `del` removes the row. `dump DIR` prints one
JSON object on stdout:

```json
{"covered_seq": 0, "entries": [{"key": "a", "value": "1", "rev": 3}]}
```

Field types: `covered_seq` is an integer; every entry is an object with a
string `key`, a string `value`, and an integer `rev`. `entries` is sorted by key; `covered_seq` is the value from the coordination
record; `rev` is the sequence number of the last operation that wrote the
key. Reading never modifies the store. Like every reader, `dump` ends its
scan cleanly at a record that fails its framing or integrity check: earlier
records stand, the scan result is served, and the exit code is 0.

## Recovery rules

`recover DIR` rebuilds the baked generation from the coordination record and
the log, then installs both:

1. Merge the baked generation with every log record whose sequence number is
   greater than the record's `covered_seq`.
2. Bake the merged rows as the next generation.
3. Install the new coordination record.

A record that fails its framing or its integrity check ends the scan. Every
earlier record stands; the bad trailing record is discarded. Recovery must
not fail, exit nonzero, or lose earlier records because the log ends in a
torn record.

After a bake completes, the coordination record is installed: `dump`'s
`covered_seq` equals the highest record sequence folded into the baked
generation, and the named generation file holds the merged rows. A store
whose coordination record never advances is defective.

Before a load appends new records, it must remove a torn trailing fragment
left by an earlier kill (the bytes of the partial record itself), so records
written afterwards are ordinary readable records. Writing new records after
an unrepaired fragment is a defect: every record past it would be invisible
to every reader.

Recovery is idempotent: running it to completion twice in a row must leave
identical `dump` output. Recovery is resumable: if a recovery pass is killed
at any fence point, the next recovery pass must still restore every
operation that was durable before the first pass started. A killed pass must
never leave the store unable to reach that state.

## Fold rules

`compact DIR` folds the current rows into the next baked generation and
clears the log. The log may only be cleared after the new generation and its
coordination record are installed and durable: until then the log is the
only surviving copy of the operations the previous baked generation does not
cover. After a fold killed at any fence point, a completed recovery must
restore every operation that was durable before the fold started.

## Anti-goals

The CLI surface, the file names above, the record framing, and the `dump`
schema are frozen. Rewriting store files by hand outside the CLI is not a
supported way to reach any of the states described here.
