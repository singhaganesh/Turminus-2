# Harden glazeurn-spool — hide the alias, confirm the generator lever, de-leak the answer (target HARD, NO false failures)

You are hardening ONE task:
`/home/ganesh/Work/AirDawg/New Terminus 2/submiterRepo/tasks/glazeurn-spool`.

**Corrected read: this is HARD-capable, not a spec-implementation medium.** The
graded transform (heat: swap in bag, push one token, +1 tick, +2 mark;
`frost_bag` = pre-kiln bag, `live_bag` = post swap+push; identical lists on heat →
non-zero + no `GUARD`) is stated — but the *bug* is not the transform. The bug is
structural and survives reading:

- **Shallow-copy Rc aliasing (DEB-C2-0250 class).** `foldrib/rim.rs` builds the
  frost snapshot with `ids: a.ids.clone()`, cloning the `Rc<RefCell<…>>` (a shared
  reference), not deep-copying. When `load::step` applies swap/push to the live
  session it also mutates the frost view, so the two bag lists come out identical.
  The fix is a genuine deep copy: `Rc::new(RefCell::new(a.ids.borrow().clone()))`,
  plus `rim_b` copying `cells`.
- **Generator-not-runtime indirection.** `bake.sh` runs `emitbay/main.rs` →
  `hearth::rib_d()`, which REGENERATES `foldrib/rim.rs`, `internpit/pool.rs`,
  `restcue/ink.rs` from embedded string templates, THEN compiles
  `steerpit/boot.rs`. Editing the generated files and rebuilding **wipes the
  edit** — the load-bearing fix must live in the `emitbay/hearth.rs` templates.
- **≥3 interacting loci:** `rim_a` deep copy, `rim_b` cells copy, `dump`'s frost
  source, and the `sess.flag && frost_s == live_s → 1` guard.

Keep this structural core and the native/ELF requirement. This pass removes the
three things that leak it and confirms the generator lever bites — targeting a
genuine <1/3, **without introducing a single false failure**.

You have NO frontier-model access. Never claim/invent an Opus 5 / GPT-5.6 /
harbor-agent result. Prove work only with the local probes and the local
red-team run at the end.

═══════════════════════════════════════════════════════════════════════
## FALSE-FAILURE FIREWALL — read this before any edit (highest priority)
═══════════════════════════════════════════════════════════════════════

1. **Every graded property must be EXPLICIT or DERIVABLE — never NOT_PUBLIC.**
   The transform SPEC stays stated in `instruction.md` (it is EXPLICIT and must
   be). What you remove is only the worked *answer* example, never a rule.

2. **Held-out spool values must be COMPUTABLE from the stated rule.** Tests
   already derive expected values via `_want()`; keep that. Never hardcode a magic
   expected list.

3. **Grade OBSERVABLE output, never code shape.** Grade `pair.json` values,
   `GUARD` contents/existence, rc, `\x7fELF` magic. Never assert the source uses
   `Rc::new`/deep-copy, names `hearth`/`rim_a`, or contains a string. The aliasing
   fix must be graded by its EFFECT (frost ≠ live after a mutating kiln), not by
   how it is written — otherwise a different-but-correct deep copy false-fails.

4. **ALT is the mandatory false-failure detector.** `alt_solution.sh` must be a
   genuinely DIFFERENT-but-correct implementation (e.g. deep-copy via a fresh
   `Vec` rebuild, or restructured frost snapshot, applied in the generator
   templates) and must score **reward 1**. If any move makes ALT fail, that move
   grades an implementation detail = false failure → fix the move.

5. **The generator lever must not become a false failure.** It is fair to
   require the fix survive `bake.sh` (i.e. live in the templates) — that is the
   task's real mechanism. But you must NOT grade *where* the source lives; grade
   only that after the standard `bake.sh` rebuild the BEHAVIOR is correct. A
   solution that edits templates (or restructures the generator) and rebuilds must
   pass; ALT proves it.

6. **Prove no false failure before finishing:** run the oracle solution AND the
   ALT solution through the real suite; BOTH must pass; `false_failure_lint.py
   --strict` clean. Quote the output.

═══════════════════════════════════════════════════════════════════════

## Why it is easy now (three leaks to kill — keep the depth)

1. **The instruction leaks the exact answer** (tick 8, mark 6, frost oak elm ash,
   live four tokens with yew and fir). Free points.
2. **The bug is made glaring, not subtle.** Broken `internpit/pool.rs` (and its
   template in `hearth.rs`) packs `frost_s = pack(&live_ids, &pool.cells)` and
   `live_s = pack(&live_ids, &pool.cells)` — two literally-identical lines that
   scream the bug, so the agent never has to reason about the Rc alias. The
   difficulty should come from the aliasing, not a copy-paste tell.
3. **The generator lever is unconfirmed.** Nothing proves that fixing the
   generated files + rebuild leaves the bug (regeneration wipes it). If that is
   not proven, the generator indirection may be inert and half the difficulty is
   dead.

## The three moves (apply all)

### Move 1 — Make the aliasing the sole, subtle mechanism (biggest lever)

Remove the copy-paste tell. In the `emitbay/hearth.rs` templates (and the
matching generated files, which bake will overwrite anyway), wire `dump` so it
packs frost from the frost snapshot and live from the live session **correctly**
(`frost_s = pack(&frost_ids, &frost.cells)`, `live_s = pack(&live_ids,
&pool.cells)`) — so the two lines are no longer identical and the code reads as
plainly correct. The ONLY thing that makes the two lists collapse is the shallow
`ids: a.ids.clone()` Rc-alias in `rim_a` plus the missing `cells` copy in
`rim_b`. Now the bug survives reading: the pack code looks right; the fault is the
shared `Rc<RefCell>`. Keep it a plausible mistake, not a stub.

### Move 2 — Confirm the generator lever bites (R5 + a dedicated probe)

Prove the fix must live in the generator, not the generated files:
- Keep `source_only.sh` (R5): edit source without running `bake.sh` → reward 0.
- ADD `gen_only.sh` (R10gen): apply the correct fix ONLY to the generated files
  `foldrib/rim.rs` / `internpit/pool.rs` (NOT the `emitbay/hearth.rs` templates),
  then run `bake.sh` → the generator regenerates the broken versions → reward 0.
  Declare it `"R10gen": {"script": "gen_only.sh", "expect_reward": 0}`.
  If R10gen scores 1, the generator indirection is inert (bake is not actually
  overwriting, or boot compiles the generated file before regen) — report that
  finding and tighten the build order; do not silently patch it away.

### Move 3 — Remove the worked answer, grade on held-out spools

In `instruction.md`, delete the sentence giving the shipped-spool output (tick 8,
mark 6, the exact token lists). Keep every RULE (grammar, heat/peek, swap/push,
frost = pre-kiln bag, live = post swap+push, identical-lists-on-heat → non-zero +
no GUARD, empty → non-zero + no GUARD, success writes GUARD = ok). Confirm the
value assertions grade at least one held-out heat spool AND one held-out peek
spool via `_want()`, with nothing copyable from the instruction. A held-out heat
spool whose swap/push actually changes the bag is what forces the alias to
matter — ensure at least one held-out spool mutates the bag non-trivially.

## Half-fix matrix (must hold after hardening)

- Fix `dump`/pack wiring only, leave the Rc-alias in `rim_a` → held-out heat spool
  red (frost still equals live after the kiln mutates the shared ids).
- Fix the Rc-alias only, leave `rim_b` cells uncopied → red (frost cells empty /
  wrong).
- Apply the full fix to the generated files but not the `hearth.rs` templates,
  then `bake.sh` → red (regenerated broken) — this is R10gen.
- Full correct fix in the generator templates + `bake.sh` → green; oracle AND alt
  both green.

Encode as preship probes (extend the existing set): keep `source_only.sh` (R5,
reward 0), `decoy_fix.sh` (R6, COVER.txt desk-count onto tick, reward 0),
`shortcut_fix.sh` (R7, hand-written pair.json, reward 0), `alt_solution.sh` (ALT,
reward **1**); ADD `gen_only.sh` (R10gen, reward 0), `alias_only.sh` (R10a, Rc
deep-copy only without cells/wiring, reward 0), and `wire_only.sh` (R10b, pack
wiring only leaving the alias, reward 0).

## Fairness (do not cross)

- `instruction.md` keeps the full transform SPEC (EXPLICIT), loses only the
  worked example. Never name `hearth`, `rim_a`, `Rc`, "deep copy", "generator",
  or the alias. State observable symptoms + rules, not the fix.
- Keep the mill NATIVE and the `\x7fELF` assert (`_assert_native`, gz11). Keep the
  `bake.sh` rebuild lever; a source edit without rebuild scores 0.
- Grade values via `_want()` on held-out spools; behavior for the aliasing (frost
  ≠ live after a mutating kiln); no hardcoded expected lists; no code-shape
  asserts.

## Files you may touch

- `instruction.md` (Move 3 — remove the worked answer only)
- `environment/emitbay/hearth.rs` (Move 1 — the generator templates: make the
  pack wiring correct so the alias is the sole fault)
- `environment/foldrib/rim.rs`, `environment/internpit/pool.rs` (keep in sync
  with the templates for readability; bake regenerates from hearth)
- `tests/test_outputs.py` (Move 3 — confirm/broaden held-out heat + peek spools
  that mutate the bag; keep `_want()`; keep native asserts and all coverage)
- verifier fixtures / held-out spools (values computable from the stated rule)
- `preship/*` (add `gen_only.sh`, `alias_only.sh`, `wire_only.sh`; keep
  R5/R6/R7/ALT)
- `solution/*` so the oracle fixes the generator templates and rebuilds
Do not weaken gz01–gz12 coverage or the ELF gate.

## Prove it (run; quote real output)

```
python3 scripts/difficulty_floor_check.py tasks/glazeurn-spool
python3 scripts/caveat_audit_check.py tasks/glazeurn-spool
python3 scripts/native_binary_check.py tasks/glazeurn-spool          # ELF gate still enforced
python3 scripts/false_failure_lint.py tasks/glazeurn-spool --strict
python3 scripts/preship_probes.py tasks/glazeurn-spool --strict      # R5/R6/R7/R10gen/R10a/R10b=0, ALT=1
python3 scripts/oracle_idempotency_probe.py tasks/glazeurn-spool --strict
python3 scripts/harbor_gate.py tasks/glazeurn-spool --oracle --nop
./scripts/check-task.sh --strict tasks/glazeurn-spool
python3 scripts/package_task.py tasks/glazeurn-spool --out Task_Ready_To_Submit/glazeurn-spool.zip --validate
```

Pass conditions (false-failure gate FIRST):
- **Oracle solution passes the full suite. ALT solution passes the full suite.**
  `false_failure_lint.py --strict` clean. If ALT fails → a move grades an impl
  detail → fix the move.
- The pack wiring reads as correct; the sole fault is the Rc-alias + missing cells
  copy (Move 1). No two-identical-lines tell remains.
- R10gen (generated-files-only + bake) reward 0 — confirms the generator lever is
  real. R10a (alias-only) and R10b (wire-only) reward 0; full fix reward 1.
  R5/R6/R7 reward 0.
- `instruction.md` no longer states the shipped-spool output; keeps the full
  transform rule. Held-out heat + peek spools grade the values via `_want()`.
- ELF gate intact; Oracle 1, NOP 0, idempotent.

## Local red-team (no API key)

Two prompts in a throwaway built container:

1. **Leak check:** *"read only instruction.md and the environment; without running
   anything, name the exact fix and files."* Success = it can state the observable
   rule (frost ≠ live after a heat kiln; the transform) but must investigate to
   find (a) the shallow Rc-alias in the frost snapshot AND (b) that the fix must
   live in the `emitbay` generator or `bake.sh` wipes it. It must NOT be able to
   read the fix off two identical pack lines or copy the answer from the
   instruction.
2. **False-failure check:** run the ALT implementation; confirm it passes. If a
   correct-but-different deep copy / generator restructure fails, report and fix
   the offending assert.

## Report (short)

1. Copy-paste tell removed: pack wiring now correct; the alias is the sole fault
   (show the before/after of the two pack lines and the `rim_a` clone).
2. Generator lever confirmed: R10gen (generated-only + bake) = 0; how bake
   regenerates over the edit.
3. Worked answer removed; transform rule kept; held-out heat + peek spools grade
   the values.
4. Half-fix matrix (R10a alias-only, R10b wire-only, R10gen = 0).
5. **False-failure proof: oracle PASS + ALT PASS + false_failure_lint clean**
   (quote output).
6. Floor before → after; ELF gate confirmed intact.
7. Full preship rewards (R5/R6/R7/R10gen/R10a/R10b/ALT).
8. Red-team results (leak + false-failure).
9. Files changed.

Never claim a probe, red-team, or frontier-model result you did not run. If any
new graded property cannot be made EXPLICIT or DERIVABLE, drop that assertion
rather than ship a false failure.
