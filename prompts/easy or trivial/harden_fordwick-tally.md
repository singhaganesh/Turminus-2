# Harden fordwick-tally — stress occlusion re-ID, combine facets, kill the tolerance crutch (video, NO false failures)

You are hardening ONE task:
`/home/ganesh/Work/AirDawg/New Terminus 2/submiterRepo/tasks/fordwick-tally`.

Do NOT redesign it. The substrate is sound: a `video-processing` /
`constrained_build` task — count distinct bodies whose centroid crosses the scan
row `y=70` top-to-bottom over a clip, count-once, similar/overlapping bodies
still separate. The mill is a folded `/app/varnish/mill.pyc` rebuilt from
`blot.py`/`tether.py`/`spout.py`/`spanwell.py` via `kiln/bake.sh` → `pack.py`
(the R5 rebuild lever). The broken pipeline (`blot_mark`) counts band-OCCUPANCY
flips at `y=70`, not distinct top-to-bottom centroid crossings, so the intended
fix is a real per-body tracker. Keep all of this.

Frontier models solve it because the standard people-counter pipeline (MOG2
background subtraction + contour centroids + nearest-centroid tracking + a
has-crossed flag) suffices: the held-out reels each stress ONE facet in
isolation, none forces severe occlusion re-identification, and the ±1 tolerance
on busy clips covers the sloppy cases. This pass moves the difficulty onto the
one facet that is NOT a library one-liner — identity through severe occlusion —
and combines facets so half-fixes fail, **without introducing a single false
failure**.

You have NO frontier-model access. Never claim/invent an Opus 5 / GPT-5.6 /
harbor-agent result. Prove work only with the local probes and the local
red-team run at the end.

═══════════════════════════════════════════════════════════════════════
## FALSE-FAILURE FIREWALL — read before any edit (highest priority; VIDEO rules)
═══════════════════════════════════════════════════════════════════════

1. **Tolerance grading, never byte-exact (INVERSE rule).** Grade the reported
   integer `crossings` against a tolerance band. NEVER assert byte-exact frames,
   whole-output media, or a digest of any video/frame. `false_failure_lint.py`
   flags byte-exact media asserts even if the instruction claims otherwise.

2. **Every graded property EXPLICIT or DERIVABLE — never NOT_PUBLIC.** The
   counting rule (top-to-bottom centroid passage, count-once, overlap/shadow
   still separate) is stated and must stay stated. Any NEW graded requirement
   (e.g. shadows do not count as bodies) MUST be added to `instruction.md` in
   operator language before it is graded — an unstated rule is an ambush.

3. **Held-out truth must be COMPUTABLE from the stated rule.** Each new reel's
   true `crossings` must follow from "distinct bodies whose centroid completes
   top-to-bottom passage, counted once." Never a truth the rule can't produce.

4. **Grade the count, not the method.** Never assert the source uses MOG2,
   Kalman, Hungarian, a specific tracker, or contains a string. Grade only the
   reported `crossings` (and rc / sheet-absence on unreadable input).

5. **ALT is the mandatory false-failure detector.** `alt_solution.sh` must be a
   genuinely DIFFERENT-but-correct tracker (e.g. Kalman + Hungarian association
   vs greedy nearest-centroid) and must score **reward 1** on every reel,
   including the new hard ones. If a hardening move makes ALT fail, that move
   grades an implementation detail or set an unreachable tolerance = false
   failure → fix the move, do not weaken ALT.

6. **Deterministic fixtures.** New reels are synthetic, generated with a FIXED
   seed, 160x120 @ 12fps, offline. Decode must be deterministic (pinned cv2) so
   R8/oracle-idempotency holds — the same reel yields the same count every run.

7. **Prove no false failure before finishing:** run the oracle solution AND the
   ALT solution through the full suite; BOTH must pass every reel;
   `false_failure_lint.py --strict` clean. Quote the output.

═══════════════════════════════════════════════════════════════════════

## Why it is easy now (three things to fix)

1. **Standard pipeline suffices** — MOG2 + centroids + nearest-centroid tracking
   + has-crossed flag; the occlusion facet is present in the instruction but never
   stressed enough to break simple association.
2. **One facet per reel** — `knot` (twin pass), `halt` (linger), `recede`
   (retreat), `crowd` (busy), `climb` (opposite dir) each isolate one facet; a
   basic tracker passes all.
3. **Tolerance crutch** — ±1 for counts ≥6 lets an undercount on busy/occluded
   clips slide.

## The five moves (apply all)

### Move 1 — Severe merge-occlusion reels, graded EXACT (biggest lever)

Add held-out reels where **two (or more) similar bodies fully merge into a single
blob for many frames** while both complete the top-to-bottom crossing, then
separate. A nearest-centroid tracker sees one blob → counts 1; truth is 2. This
forces appearance/trajectory re-identification, which is NOT a cv2 one-liner.
**Design the true count of these reels to be ≤5** so the instruction's EXACT-match
rule applies — the tolerance cannot rescue a merged-blob undercount. Include: two
bodies merging then splitting; three bodies where the middle one is fully occluded
mid-crossing; two bodies that swap horizontal positions while merged (identity
must not swap-cancel).

### Move 2 — One reel that combines facets (half-fix matrix)

Add a reel that simultaneously has: severe occlusion + a cast shadow crossing the
line + a body that crosses, retreats above the line, and re-crosses (count once) +
one opposite-direction body (must NOT count). A solution that fixes occlusion
alone still overcounts the shadow; fixes shadow alone still miscounts the
retreat; etc. This makes the facets interact so no single fix passes.

### Move 3 — Make shadow-rejection load-bearing (and STATE it)

Add a reel where a cast shadow sweeps across `y=70` as its own connected blob. A
naive detector counts the shadow → overcounts. **State the rule in
`instruction.md`**: shadows/shading are not bodies and do not add to the count
(the instruction already says "one shades the other" for overlap — extend it to
"a cast shadow crossing the scan is not a body"). Only then grade it (firewall #2).

### Move 4 — Tighten the tolerance crutch on discriminating reels

Keep the public rule (exact ≤5, ±1 for ≥6) — do not change the stated contract.
But ensure the **discriminating reels (Moves 1-3) have true counts ≤5** so they
are graded EXACTLY. Reserve ±1 only for genuinely high-count ambiguous reels
where even the oracle+ALT can legitimately differ by 1 (confirm both pass).

### Move 5 — Confirm the rebuild lever bites

Keep R5 (`source_only.sh`: edit the `.py` modules, skip `kiln/bake.sh` → stale
`mill.pyc` runs → reward 0). Verify it still scores 0 after your changes; if a
rebuild is not actually required (pack.py silently reuses), report it, do not
paper over it.

## Half-fix matrix (must hold after hardening)

- Occupancy-flip counter (current bug) → red on every real reel.
- Centroid tracker WITHOUT occlusion re-ID → merge reels (Move 1) red.
- Occlusion re-ID but no shadow rejection → shadow reel (Move 3) red.
- Handles occlusion+shadow but not retreat/re-cross → combined reel (Move 2) red.
- Counts every direction (no top-to-bottom filter) → `climb`/opposite-dir red.
- Full correct tracker (occlusion re-ID + shadow reject + directional + count-once)
  → green; oracle AND alt both green on all reels.

Encode as preship probes (extend the existing set — keep R5/R6/R7/R7launch/R7pyc/
R7path/naive_impl/happy_path_only/spec_gaming/ALT): ADD `R10a` (occlusion-only,
no shadow reject → reward 0) and `R10b` (shadow-reject-only, no occlusion re-ID →
reward 0).

## Fairness (do not cross)

- Grade the integer `crossings` with a tolerance band; never byte-exact on media.
- State every graded rule (count-once, top-to-bottom, overlap-separate, shadows-
  not-bodies) in `instruction.md`. New reel truths computable from that rule.
- Python + cv2/numpy/toml only; offline; 160x120 @ 12fps. Deterministic synthetic
  reels (fixed seed). Oracle rebuilds via `kiln/bake.sh`; no hardcoded outputs;
  no hand-written sheet.
- Do not name the tracker/method in the instruction or grade on code shape.

## Files you may touch

- `tests/reels/` — add the merge-occlusion reels (Move 1), combined-facet reel
  (Move 2), shadow reel (Move 3); all synthetic, fixed seed, held out from `/app`
- `tests/test_outputs.py` — add `_within` cases for the new reels with truths
  computable from the rule; keep all existing coverage; keep exact/±1 bands
- `instruction.md` — state the shadow-not-a-body rule (Move 3) in operator
  language; do not name the method or leak the impl
- verifier fixtures / reel generator (deterministic; kept out of `/app`)
- `preship/*` — add `R10a`, `R10b`; keep the existing probe set and `preship.json`
- `solution/*` and the folded-source oracle only so the oracle handles the new
  reels and still rebuilds via `bake.sh`
Do not weaken existing fdw01-fdw11 coverage or the rebuild lever.

## Prove it (run; quote real output)

```
python3 scripts/difficulty_floor_check.py tasks/fordwick-tally
python3 scripts/caveat_audit_check.py tasks/fordwick-tally
python3 scripts/false_failure_lint.py tasks/fordwick-tally --strict
python3 scripts/preship_probes.py tasks/fordwick-tally --strict   # R5/R6/R7*/naive/happy/spec_gaming/R10a/R10b=0, ALT=1
python3 scripts/oracle_idempotency_probe.py tasks/fordwick-tally --strict
python3 scripts/harbor_gate.py tasks/fordwick-tally --oracle --nop
./scripts/check-task.sh --strict tasks/fordwick-tally
python3 scripts/package_task.py tasks/fordwick-tally --out Task_Ready_To_Submit/fordwick-tally.zip --validate
```

Pass conditions (false-failure gate FIRST):
- **Oracle passes the full suite. ALT passes the full suite** (every reel,
  including merge/shadow/combined). `false_failure_lint.py --strict` clean.
- Merge-occlusion reels (Move 1) have true count ≤5 and are graded EXACTLY; a
  nearest-centroid-only solution fails them.
- R10a (occlusion-only) and R10b (shadow-only) reward 0; full fix reward 1.
  R5/R6/R7*/naive_impl/happy_path_only/spec_gaming reward 0.
- New reel truths computable from the stated rule; shadow rule stated in
  `instruction.md`. Oracle 1, NOP 0, idempotent (same reel → same count).

## Local red-team (no API key)

1. **Naive-pipeline check:** in a throwaway built container, implement the
   standard MOG2 + nearest-centroid + has-crossed counter and run it on the new
   reels. Success = it FAILS the merge-occlusion and combined reels (proves the
   difficulty moved onto occlusion re-ID, not scenery).
2. **False-failure check:** run the ALT tracker (Kalman+Hungarian); confirm it
   passes every reel. If a correct-but-different tracker fails a reel, the reel's
   truth or tolerance is wrong — fix it, do not weaken ALT.

## Report (short)

1. Merge-occlusion reels added: how many bodies merge, true counts (≤5, exact),
   why nearest-centroid fails them.
2. Combined-facet reel: which facets co-occur; half-fix matrix (R10a/R10b = 0).
3. Shadow rule stated in instruction + shadow reel added.
4. Tolerance: discriminating reels graded exact; ±1 reserved for high-count only.
5. Rebuild lever R5 still 0.
6. **False-failure proof: oracle PASS + ALT PASS on all reels + false_failure_lint
   clean** (quote output).
7. Floor + full preship rewards.
8. Red-team results (naive-pipeline fails hard reels; ALT passes).
9. Files changed.

Never claim a probe, red-team, or frontier-model result you did not run. If any
new graded property cannot be made EXPLICIT or DERIVABLE, or any tolerance would
reject a valid tracker, drop that assertion rather than ship a false failure.
