Fold pipeline bench notes. Source changes under `/app/symmill` and `/app/pcfold` are required before the fold artifacts match the linked runtime.

The fold pipeline must regenerate `/app/symmill/fold/runtime.symmap` and `/app/symmill/fold/profile.json`. Manual or hand-written copies are insufficient. `make -C /app/symmill emitmap` is the pipeline entry that rebuilds that pair.

Symmap header is `PCFOLD1` with `mode` set to `linked`, string `buildid`, an `origin pcfold-index-linked` line produced by `pcfold index --linked`, and `sym` rows. Hand-built maps lack that origin line. The symmap must contain at least 8 `sym` rows. Each `sym` row lists name, start address, and span size in hex.

Span sizes must match `nm -n --defined-only` ordering on `/app/symmill/fold/runtime` (each symbol ends where the next text symbol begins; the last symbol uses a 64-byte span). Linked maps must not keep uniform `0x40` object-merge placeholder spans.

Runtime `buildid` in the symmap must be at least 8 hex characters and match the `Build ID:` from `readelf -n /app/symmill/fold/runtime`. Bench anchor stamp `/app/benchframes/anchor/buildid.stamp` mirrors that value after a correct pipeline run.

`/app/pcfold/conf/latch.env` must keep `FOLD_LATCH on` so `/app/bin/pcfold check` enforces symmap identity. `/app/bin/pcfold check <runtime> <symmap>` must exit non-zero when the symmap buildid drifts from the runtime ELF and must exit zero for the on-disk pair after repair. `make -C /app/symmill emitmap` must fail when that check rejects the map.

The verifier reruns `/opt/verifier/bin/pcfold-grade render` on held-out sample files without invoking emitmap.

Profile `frames` are a JSON array of objects with string `pc`, string `symbol`, and integer `offset`.

Bench anchor symbol addresses live in `/app/benchframes/anchor/symbols.tab`.
