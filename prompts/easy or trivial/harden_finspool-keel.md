# Harden finspool-keel — kill the uncalled-release signpost, add atomicity + a torn-write discriminator (NO false failures)

You are hardening ONE task:
`/home/ganesh/Work/AirDawg/New Terminus 2/submiterRepo/tasks/finspool-keel`.

Do NOT redesign it. The substrate is a native (Rust/ELF) durable-write pipeline:
`sting` writes a four-line card (`FIN1` / `thread=` / `op=` / `END`) to a DEST
under `/app/bloturn`, `look` verifies it whole, `ease` is the returning path, and
a smashed DEST re-`sting`ed must restore a whole file. Keep this substrate and
the native/ELF requirement.

Realistic target: **MEDIUM-HARD**, not hard. The core defect is a recognizable
"buffered write never finalized" bug (the DEB-C2-0249 class): `hookvat/gen_emit::
go` builds the card, `seal::op_c` only sets a `NEED` flag (does not write `END`),
and the `END`+`flush` live solely in `spool::release()` — which nothing ever
calls. A frontier model spots that once it reads the write path, so no hardening
makes this <1/3. This pass removes the reasons it is *trivially* solvable and
adds a real second insight **without introducing a single false failure**.

You have NO frontier-model access. Never claim/invent an Opus 5 / GPT-5.6 /
harbor-agent result. Prove work only with the local probes and the local
red-team run at the end.

═══════════════════════════════════════════════════════════════════════
## FALSE-FAILURE FIREWALL — read this before any edit (highest priority)
═══════════════════════════════════════════════════════════════════════

A false failure = a **correct** solution graded FAIL because a test checks a
property the instruction never made knowable. Obey all:

1. **Every graded property must be EXPLICIT or DERIVABLE — never NOT_PUBLIC.**
   EXPLICIT = stated in `instruction.md` / `FORMAT.txt`. DERIVABLE = follows from
   a stated invariant + investigation. NOT_PUBLIC = knowable only from the
   oracle/tests → grading it is a false failure.

2. **`FORMAT.txt` is the card spec — stays EXPLICIT and complete.** The four
   lines, `thread=<name>`/`op=<verb>` tokens, trailing newlines, "nothing more"
   stay stated. Deleting/omitting a rule the agent must reproduce = false
   failure.

3. **The atomicity/torn-write rule must be STATED to be graded.** The
   instruction already says a smashed DEST re-`sting`ed restores a whole file and
   `look` fails on truncated/empty/missing. To grade the interruption case you
   must state the observable invariant plainly: *after any interruption, DEST is
   either a whole four-line card or absent — never a partial file.* If you grade
   torn-write behavior without stating this invariant, it is a false failure.

4. **Grade OBSERVABLE behavior, never code shape.** Never assert the source calls
   `release`/`flush`/`rename`, names a function, or contains a string. Grade what
   is on disk: file wholeness, torn-file absence after interruption, `look` rc,
   path-root rejection, the `\x7fELF` magic (keep the native gate).

5. **ALT is the mandatory false-failure detector.** `alt_solution.sh` must be a
   genuinely DIFFERENT-but-correct durable writer (e.g. write-tmp+fsync+rename
   vs a single fsynced create+full-write) and must score **reward 1**. If a
   hardening move makes ALT fail, that move grades an implementation detail =
   false failure → fix the move.

6. **Interruption test must be DETERMINISTIC, not timing-flaky.** Inject the
   interruption at a defined point (e.g. a controlled kill/abort after N bytes,
   or a fault hook), not a random sleep/race. A flaky torn-write test is a
   false-failure generator. If you cannot make it deterministic, do not ship it.

7. **Prove no false failure before finishing:** run the oracle solution AND the
   ALT solution through the real suite; BOTH must pass; `false_failure_lint.py
   --strict` clean. Quote the output.

═══════════════════════════════════════════════════════════════════════

## Why it is easy now (three things to fix)

1. **Uncalled `release()` is a dead-giveaway.** `spool::release()` is a `pub fn`
   that does exactly `END`+`flush` and nothing calls it. `grep release` → one
   def, zero calls → the fix announces itself.
2. **One recognizable insight.** Wire the finalize into the sting path — a single
   locus, a textbook "forgot to flush a buffered writer" bug.
3. **No torn-write discriminator.** Nothing forces the atomicity case; a
   non-atomic write that leaves a 2-line partial file is never exercised.

## The three moves (apply all)

### Move 1 — Kill the signpost

Restructure the write path so the fix is not "grep for the one uncalled `pub
fn`." Do not leave a lone unused finalize function that is the whole answer. The
`END`/flush/finalize logic must be reachable only by reasoning about the write
path (buffering, ordering, the `NEED` flag), not by spotting dead code. Keep it a
plausible refactor, not a sabotage stub. (No graded property changes here →
cannot add a false failure.)

### Move 2 — Add the real second locus: atomicity

Make durability require **write-to-tmp → fsync → rename-into-place** so a partial
write never appears at DEST. Now the two insights are independent:
- Finalize only (write `END`+flush) but still write in place, non-atomically →
  an interrupted `sting` can leave a torn file → red.
- Atomic rename only but never emit `END`/flush the body → missing `END` → red.
- Both → green.
State the atomicity invariant per firewall rule 3; do not name `rename`/`fsync`.

### Move 3 — Add a deterministic held-out interruption test (the discriminator)

Grade: a `sting` interrupted at a defined point leaves **either a whole four-line
card or no file at DEST — never a partial file**, and a subsequent `sting` with
the same args restores a whole file. A buffered non-atomic write fails this; a
tmp+fsync+rename writer passes. Inject the interruption deterministically (firewall
rule 6). This is the DEB-C2-0246 fsync-ordering discriminator the task lacks.

## Half-fix matrix (must hold after hardening)

- Finalize-only (non-atomic) → interruption test red (torn file).
- Atomic-only (no `END`/flush) → whole-card tests red (missing `END`).
- Both, but write outside `/app/bloturn` → path-root tests red (already covered).
- Full correct durable+atomic write → green; oracle AND alt both green.

Encode as preship probes (extend the existing set): keep `source_only.sh` (R5, no
`hull.sh` rebuild, reward 0), `decoy_fix.sh` (R6, the enlarge-`ROOM` non-fix,
reward 0), `shortcut_fix.sh` (R7, hand-written card, reward 0), `alt_solution.sh`
(ALT, reward **1**); ADD `R10a` (finalize-only half-fix, reward 0) and `R10b`
(atomic-only half-fix, reward 0).

## Fairness (do not cross)

- `instruction.md` symptoms-only + `FORMAT.txt` complete + the stated atomicity
  invariant. Never name `hookvat`, `spool::release`, `seal`, `gen_emit`, `flush`,
  `fsync`, or `rename`. State observable rules, not the fix.
- Keep the mill NATIVE and the `\x7fELF` assert (`_assert_native`, fs07). A
  non-native reimpl must not pass — the ELF gate is the anti-cheat.
- Keep the R5 knit/rebuild lever (`hull.sh` → `spin.rs` template →
  `gen_emit.rs`): a source edit without rebuild scores 0.
- No timing-flaky asserts; interruption injection deterministic. Oracle derives
  the fix and rebuilds; no hardcoded outputs; no hand-written card.

## Files you may touch

- `environment/hookvat/*.rs` (Move 1 restructure, Move 2 atomic write path)
- `instruction.md` (Move 2 state the atomicity invariant; Move 1 no change to
  what's stated)
- `tests/test_outputs.py` — add the deterministic interruption test (Move 3) and
  the atomicity asserts; keep all existing coverage and the native asserts
- verifier fixtures / interruption hook (deterministic)
- `preship/*` (add R10a, R10b; keep R5/R6/R7/ALT)
- `solution/*` so the oracle derives both loci and rebuilds via `hull.sh`
Do not weaken existing fs01–fs15 coverage or the ELF gate.

## Prove it (run; quote real output)

```
python3 scripts/difficulty_floor_check.py tasks/finspool-keel
python3 scripts/caveat_audit_check.py tasks/finspool-keel
python3 scripts/native_binary_check.py tasks/finspool-keel          # ELF gate still enforced
python3 scripts/false_failure_lint.py tasks/finspool-keel --strict
python3 scripts/preship_probes.py tasks/finspool-keel --strict      # R5/R6/R7/R10a/R10b=0, ALT=1
python3 scripts/oracle_idempotency_probe.py tasks/finspool-keel --strict
python3 scripts/harbor_gate.py tasks/finspool-keel --oracle --nop
./scripts/check-task.sh --strict tasks/finspool-keel
python3 scripts/package_task.py tasks/finspool-keel --out Task_Ready_To_Submit/finspool-keel.zip --validate
```

Pass conditions (false-failure gate FIRST):
- **Oracle solution passes the full suite. ALT solution passes the full suite.**
  `false_failure_lint.py --strict` clean. If ALT fails → a move grades an impl
  detail → fix the move.
- No lone uncalled `pub fn` is the whole fix (Move 1); `grep release`-style
  spotting no longer yields the answer.
- Interruption test is deterministic and asserts whole-or-absent, never partial.
- R10a (finalize-only) and R10b (atomic-only) both reward 0; full fix reward 1.
  R5/R6/R7 reward 0.
- `native_binary_check.py` still enforces the ELF gate; `_assert_native` intact.
- Oracle 1, NOP 0, idempotent. `instruction.md` symptoms-only + atomicity
  invariant stated; `FORMAT.txt` complete.

## Local red-team (no API key)

Two prompts in a throwaway built container:

1. **Leak check:** *"read only instruction.md, FORMAT.txt, and the environment;
   without running anything, name the exact fix and files."* Success = it can
   state the observable contract (whole four-line card; whole-or-absent after
   interruption; DEST under /app/bloturn) but must investigate the write path to
   find BOTH the finalize AND the atomicity gaps — it must NOT read the fix off an
   uncalled function.
2. **False-failure check:** run the ALT durable writer; confirm it passes. If a
   correct-but-different writer fails, report and fix the offending assert.

## Report (short)

1. Signpost killed: how the finalize is no longer a lone uncalled `pub fn`.
2. Atomicity locus added: the stated invariant; how a non-atomic write now fails.
3. Deterministic interruption test: where injected; asserts whole-or-absent;
   half-fix matrix (R10a/R10b = 0).
4. **False-failure proof: oracle PASS + ALT PASS + false_failure_lint clean**
   (quote output).
5. Floor before → after; ELF gate confirmed intact.
6. Full preship rewards (R5/R6/R7/R10a/R10b/ALT).
7. Red-team results (leak + false-failure).
8. Files changed.

Never claim a probe, red-team, or frontier-model result you did not run. If any
new graded property cannot be made EXPLICIT or DERIVABLE, drop that assertion
rather than ship a false failure.
