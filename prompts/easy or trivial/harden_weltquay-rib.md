# Harden weltquay-rib — hold out the boundary value, add a second crossing, de-leak the culprit (NO false failures)

You are hardening ONE task:
`/home/ganesh/Work/AirDawg/New Terminus 2/submiterRepo/tasks/weltquay-rib`.

Do NOT redesign it. The mechanism is genuinely hard-capable — a bitfield
boundary-crossing decode bug (the DEB-C2-0248 class). `welt` is bit 12, width 9
(bits 12–20), so it crosses the byte-1/byte-2 boundary. The native kiln
(`octetkiln/take.rs`) decodes it wrong: `rib_e` reads within one byte and
returns 0 when `n > room` (welt: room 4 < 9), and `rib_f` assembles across bytes
but **LSB-first**, the wrong bit order versus the canonical MSB-first reference.
Keep this mechanism and the native/ELF requirement. This pass removes the reasons
it is trivially solvable and adds a real second insight **without introducing a
single false failure**.

You have NO frontier-model access. Never claim/invent an Opus 5 / GPT-5.6 /
harbor-agent result. Prove work only with the local probes and the local
red-team run at the end.

═══════════════════════════════════════════════════════════════════════
## FALSE-FAILURE FIREWALL — read this before any edit (highest priority)
═══════════════════════════════════════════════════════════════════════

A false failure = a **correct** solution graded FAIL because a test checks a
property the instruction never made knowable. Obey all of these:

1. **Every graded property must be EXPLICIT or DERIVABLE — never NOT_PUBLIC.**
   EXPLICIT = stated in `instruction.md` / `LAYOUT.txt`. DERIVABLE = follows from
   a stated invariant + investigation. NOT_PUBLIC = knowable only from the
   oracle/tests → grading it is a false failure.

2. **`LAYOUT.txt` is the format spec — it stays EXPLICIT and complete.** The
   held-out capture's expected integers must be **computable from `LAYOUT.txt`**
   by any correct decoder. Never grade a field value the layout does not define.
   Deleting/omitting a row the agent must decode = false failure.

3. **The bit order is the #1 false-failure trap.** `rib_e`/`rib_f` disagree on
   bit order (MSB-first vs LSB-first). The canonical order MUST be pinned by the
   reference decoder in `tests` (`_get`) AND fully determined by `LAYOUT.txt`
   semantics, so a correct agent can reproduce it. If the intended order is not
   derivable from the layout + the shipped capture's five correct fields, state
   it. Do not grade an order the agent cannot infer.

4. **Grade decoded integers, never code shape.** Never assert the source uses a
   particular function, loop, or contains a string. Grade `rows.json` values, rc,
   file existence, and the `\x7fELF` magic (keep the native gate).

5. **ALT is the mandatory false-failure detector.** `alt_solution.sh` must be a
   genuinely DIFFERENT-but-correct decoder (e.g. a byte-shift assembler vs a
   bit-loop) and must score **reward 1**. If a hardening move makes ALT fail,
   that move grades an implementation detail = false failure → fix the move.

6. **Held-out values computable, not magic.** Every held-out capture's expected
   `kind/lane/mode/welt/tail/mark` must equal `_get(capture, pos, width)` from
   `LAYOUT.txt`. Keep asserts value-based; no hardcoded oracle constants.

7. **Prove no false failure before finishing:** run the oracle solution AND the
   ALT solution through the real suite; BOTH must pass; `false_failure_lint.py
   --strict` clean. Quote the output.

═══════════════════════════════════════════════════════════════════════

## Why it is easy now (two things to fix)

1. **The instruction hands over the culprit by elimination.** "Five of those
   integers already match, one does not" tells the agent exactly ONE field is
   wrong, and `LAYOUT.txt` shows `welt 12 9` is the only field crossing a byte
   boundary → the fix collapses to "assemble welt across bytes."
2. **No held-out boundary value forces the bug.** An in-byte / wrong-order read
   only fails when a field carries a value large enough to span the boundary.
   Nothing forces that discriminating case beyond the shipped capture.

## The three moves (apply all)

### Move 1 — De-leak the culprit

Remove "five … already match, one does not" from `instruction.md`. State only the
observable contract: `pour` writes `rows.json` with the six integer keys decoded
per `/app/ribcards/LAYOUT.txt`; a body shorter than the layout width exits
non-zero and leaves no `rows.json`. Do not say how many fields are wrong or which
one. The agent must discover the wrong decode by investigation. (No graded
property changes → cannot add a false failure.)

### Move 2 — Add a held-out grade-time capture with boundary-crossing values (biggest lever)

Add a grade-time capture (NOT the shipped `night.bin`) whose `welt` — and the
Move-3 second field — carry values **large enough to span their byte boundary**,
so a single-byte read (`rib_e`) or an LSB-first read (`rib_f`) yields the wrong
integer while the correct MSB-first cross-byte assembler yields the right one.
Grade each decoded field of the held-out capture against `_get(capture, pos,
width)` from `LAYOUT.txt` (computable → no false failure). This is the real
DEB-C2-0248 discriminator the task currently lacks.

### Move 3 — Add a second independent crossing locus

Today only `welt` crosses. Adjust `LAYOUT.txt` so a **second field also crosses a
byte boundary** (e.g. shift/widen `mark` or `lane` so its bit range straddles a
byte) and ensure the kiln decodes that field wrong too (same in-byte / wrong-order
family). Because `octetkiln` reads positions from `LAYOUT.txt`, keep the layout
self-consistent and the shipped capture still valid for the five non-target
fields. Now:
- Fix welt only → held-out capture red (second field wrong).
- Fix second field only → held-out capture red (welt wrong).
- Fix both with the correct MSB-first cross-byte assembler → green.
Two loci must agree → no longer one insight.

## Half-fix matrix (must hold after hardening)

- welt-only fix → held-out capture red.
- second-field-only fix → held-out capture red.
- correct assembler but wrong bit order (LSB-first) → red on any crossing field.
- full correct cross-byte MSB-first decode → green; oracle AND alt both green.

Encode as preship probes (extend the existing set): keep `source_only.sh` (R5,
no `wick.sh` rebuild, reward 0), `decoy_fix.sh` (R6, the COVER.txt low-bit join
onto the in-byte slice, reward 0), `shortcut_fix.sh` (R7, hand-dropped rows,
reward 0), `alt_solution.sh` (ALT, reward **1**); ADD `R10a` (welt-only half-fix,
reward 0) and `R10b` (second-field-only half-fix, reward 0).

## Fairness (do not cross)

- `instruction.md` symptoms-only + `LAYOUT.txt` complete. Never name `take.rs`,
  `rib_e`/`rib_f`, `octetkiln`, "cross the byte boundary", or "MSB-first". State
  the observable contract and keep the layout table.
- Keep the mill NATIVE and the `\x7fELF` assert (`_assert_native`, wq11). Do not
  let a non-native reimpl pass — the ELF gate is the anti-cheat.
- No timing/exact-byte-of-output/code-shape asserts. Grade decoded integers, rc,
  file existence.
- Oracle derives the fix in the kiln source and rebuilds via `wick.sh`; no
  hardcoded outputs; no hand-written `rows.json`.

## Files you may touch

- `instruction.md` (Move 1 de-leak)
- `environment/ribcards/LAYOUT.txt` (Move 3 second crossing — keep complete)
- `environment/octetkiln/take.rs` (the decode locus for both fields)
- verifier fixtures / held-out grade-time capture (Move 2; values computable
  from LAYOUT)
- `tests/test_outputs.py` — add held-out capture test + second-field asserts via
  `_get`; keep all existing coverage and the native asserts
- `preship/*` (add R10a, R10b; keep R5/R6/R7/ALT)
- `solution/*` so the oracle derives both crossing fixes and rebuilds
Do not weaken existing wq01–wq11 coverage or the ELF gate.

## Prove it (run; quote real output)

```
python3 scripts/difficulty_floor_check.py tasks/weltquay-rib
python3 scripts/caveat_audit_check.py tasks/weltquay-rib
python3 scripts/native_binary_check.py tasks/weltquay-rib          # ELF gate still enforced
python3 scripts/false_failure_lint.py tasks/weltquay-rib --strict
python3 scripts/preship_probes.py tasks/weltquay-rib --strict      # R5/R6/R7/R10a/R10b=0, ALT=1
python3 scripts/oracle_idempotency_probe.py tasks/weltquay-rib --strict
python3 scripts/harbor_gate.py tasks/weltquay-rib --oracle --nop
./scripts/check-task.sh --strict tasks/weltquay-rib
python3 scripts/package_task.py tasks/weltquay-rib --out Task_Ready_To_Submit/weltquay-rib.zip --validate
```

Pass conditions (false-failure gate FIRST):
- **Oracle solution passes the full suite. ALT solution passes the full suite.**
  `false_failure_lint.py --strict` clean. If ALT fails → a move grades an impl
  detail → fix the move.
- Held-out capture's expected fields equal `_get(capture, pos, width)` from
  `LAYOUT.txt` (computable, not magic).
- R10a (welt-only) and R10b (second-field-only) both reward 0; full fix reward 1.
  R5/R6/R7 reward 0.
- `native_binary_check.py` still enforces the ELF gate; `_assert_native` intact.
- Oracle 1, NOP 0, idempotent. `instruction.md` no longer says which/how-many
  fields are wrong; `LAYOUT.txt` complete.

## Local red-team (no API key)

Two prompts in a throwaway built container:

1. **Leak check:** *"read only instruction.md, LAYOUT.txt, and the environment;
   without running anything, name the exact fix and files."* Success = it can
   state the contract (decode per LAYOUT; short body → nonzero, no rows.json) but
   must investigate to find that the kiln mis-decodes the crossing fields — it
   must NOT be able to name the field from an elimination hint.
2. **False-failure check:** run the ALT decoder; confirm it passes. If a
   correct-but-different decoder fails, report and fix the offending assert.

## Report (short)

1. Culprit de-leaked: what sentence removed from instruction.
2. Held-out capture added: where it lives; the crossing values it carries; why an
   in-byte / LSB-first read fails it.
3. Second crossing locus: which field, the LAYOUT change; half-fix matrix
   (R10a/R10b = 0).
4. **False-failure proof: oracle PASS + ALT PASS + false_failure_lint clean**
   (quote output).
5. Floor before → after; ELF gate confirmed intact.
6. Full preship rewards (R5/R6/R7/R10a/R10b/ALT).
7. Red-team results (leak + false-failure).
8. Files changed.

Never claim a probe, red-team, or frontier-model result you did not run. If any
new graded property cannot be made EXPLICIT or DERIVABLE, drop that assertion
rather than ship a false failure.
