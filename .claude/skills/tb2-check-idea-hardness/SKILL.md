---
name: tb2-check-idea-hardness
description: Screen a list of Terminal-Bench task IDEAS (JSON) and predict which are hard-capable (can reach frontier-hard) versus which cap at medium/easy. Pull when the user pastes one or more task-idea JSON objects and asks which will be hard, or to triage ideas before building. Judges the IDEA's ceiling, not a built task. Read-only: classifies and explains, does not author or harden tasks.
disable-model-invocation: true
---

# tb2-check-idea-hardness — predict which task ideas are hard-capable

Input: one or more task-idea JSON objects (fields like `domain, title, premise,
symptom, defect, why_hard, trap, difficulty_summary, graded_on, capability,
capability_name, id`).

Output: per-idea verdict `HARD` / `NOT-HARD`, the reason, family, confidence,
plus totals — the compact format in §5.

You classify the **idea's difficulty ceiling** (can it be built into a
frontier-hard task). You do **not** judge a built task, run anything, or edit
files. This is analysis only.

## 0. The framing you must state and hold

- **The verdict is a PREDICTOR, not a measurement.** Terminal-Bench defines hard
  empirically: a task is *hard* only when frontier models resolve it **< 1/3**
  of the time; *medium* 1/3–2/3; *easy* ≥ 2/3. That is established by rollouts,
  never by reading. Static prediction correlates only ~r=0.44 with the empirical
  result.
- **Consequences:** lean conservative — only call `HARD` on positive structural
  evidence; express doubt through **confidence**, not by inflating the verdict.
  Humans (and this skill) spot true-hard reasonably well but are **over-optimistic
  on medium** — many "looks medium/hard" ideas measure easy. When unsure, say so.
- **Idea ceiling, not execution.** A deep idea can still be built easy (leaked
  requirement, visible fixtures, obvious defect). That is an execution failure,
  not a ceiling failure — note it, but the verdict is about the ceiling.

## 1. Parse each idea

Read every field. Missing `defect`, `graded_on`, or `why_hard` weakens
confidence — note it. Restate, in one line each: what the agent must work out,
and where the defect hides.

## 2. Classify the hardness FAMILY (routes the test)

From the measured Terminal-Bench failure taxonomy, hard tasks fall in three
families. Pick the dominant one per idea; the family decides which ceiling test
applies (each has a different "easy" trap).

- **Verification** — the agent makes a plausible attempt but fails to confirm the
  goal state: rebuild-after-edit, re-run/regenerate, prove-it-twice, avoid a
  decoy. The largest hard-task failure class (verification errors are 47–60% of
  failures on hard/long-horizon tasks). Most `C2`/`C3` ideas live here.
- **Long-horizon coherence** — many *dependent* steps where context is lost,
  ordering matters, and each step can fail. Hard from genuine chained depth, not
  volume.
- **Adversarial / creative** — the core problem is itself hard: cryptanalysis,
  regex/grammar synthesis, filter bypass, niche-but-documented knowledge that
  must be *applied*. No planted defect required.
- **Constrained-build (software-engineering)** — no planted defect; the agent
  IMPLEMENTS a stated capability (interpreter, protocol, tool, package, codegen).
  The spec is fully stated (that is required, not a leak). Hardness comes from
  building it correctly. Route these to the constrained-build test in §3, NOT the
  verification test — the "not reading-comprehension" rule does not apply the same
  way, because a stated spec is expected here; the SE cap is "a naive impl passes",
  not "the requirement is stated".

## 3. Apply the family's ceiling test

### Verification family — ALL must hold to be HARD-capable
1. **Requirement–insight GAP (decisive).** Can the tests grade the *outcome*
   without the instruction stating the *fix/mechanism*? If the fair requirement
   **is** the insight — e.g. "detect a changed file even when device+inode are
   unchanged" literally tells the agent to content-address — it caps at
   **medium**. No de-leak can save it: stating what to grade states the fix.
2. **Structural, not stale-refresh.** The bug is in how the pipeline is
   wired/computes/times/coordinates and **survives reading** (re-running does not
   fix it): execution timing, dependency graph, positional coupling, config
   coverage, template/branch divergence, snapshot ordering, concurrency. A
   **recognizable stale-cache/stale-input gotcha** whose fix is refresh /
   re-point / re-migrate / regenerate / bump-a-constant / update-a-cache-key caps
   at medium — models pattern-match these.
3. **Not reading-comprehension.** Difficulty is not "implement a stated
   spec/grammar/rule." Models read well; spec-implementation caps at medium.
4. **≥2–3 genuinely independent insights.** Fixing one does not reveal the
   others. One insight applied across several files is **one** insight.

Miss any one → NOT-HARD (medium/easy), and name which test failed.

### Constrained-build (SE) family — ALL must hold to be HARD-capable
The idea states the capability to build; there is no bug to diagnose. Judge
whether *building it correctly* is hard:
1. **Naive impl fails (decisive).** The obvious first-pass implementation a
   competent engineer writes from the spec would FAIL the graded suite (because it
   is checked against adversarial/held-out cases, interacting facets, concurrency,
   or conformance a first pass gets wrong). If a straightforward impl passes
   everything → **easy/medium** (`naive-passes`). This REPLACES the GAP test here:
   a stated spec is not a cap for SE.
2. **≥3 independent, interacting facets.** Three or more requirements that must
   all hold together and do not auto-satisfy each other (e.g. framing + ordering +
   backpressure; grammar + precedence + error-recovery). One facet spread over
   files is one facet.
3. **Unfakeable conformance discriminator.** Graded on held-out/adversarial inputs
   the agent cannot see or hardcode — the impl must generalize. Visible-example-only
   grading collapses it.
4. **Applied domain knowledge.** Correct construction needs applied specialised
   knowledge (protocol/RFC, grammar, memory-model/concurrency, wire format).

Miss any one → NOT-HARD, and name which test failed.

**Video-processing sub-case (constrained_build).** Same four tests. The
discriminator (point 3) is the held-out **test video** (example video visible
only); a CV script tuned to the example fails the held-out video. Grading MUST be
tolerance-based (frame range / L2 / SSIM) — a task graded byte-exact on media is
broken (`MEDIA-EXACT`), not hard. Cap tags `naive-passes` (a trivial CV, e.g.
fixed threshold, passes the held-out video) and `happy-path-only` (graded only on
the example) apply. Mark video verdicts `confidence: low|med` — one measured
anchor only (corpus `video-processing`).

### Long-horizon family — HARD if
Many **dependent** steps (order matters, state accumulates, each can fail) such
that context loss or a mid-chain slip fails the run — not a long list of
independent chores. Volume alone is instruction-following, not hardness.

### Adversarial / creative family — HARD if
The core problem is genuinely hard to *derive/solve* (not stated in a spec):
real cryptanalysis, synthesis, bypass, or applied niche knowledge. The
reading-comprehension rule does **not** apply here.

## 4. Decide and label the failure mode

For NOT-HARD, tag the specific cap so the author knows the fix (or that there
isn't one):

- `req≡insight` — requirement is the insight → **drop or accept medium**; hardening cannot help.
- `stale-refresh` — recognizable stale-cache/input gotcha → medium.
- `reading-comp` — spec/grammar/rule implementation → medium.
- `one-insight` — a single realisation (possibly spread across files) → medium.
- `volume-not-depth` — many independent steps, no chained depth → medium/easy.
- `naive-passes` — (SE) the obvious impl passes the graded suite → deepen the spec (add interacting facets + held-out conformance) or accept medium.
- `happy-path-only` — (SE) graded only on visible examples, no held-out/adversarial corpus → collapses; add a conformance discriminator.

For HARD, note the one thing most likely to collapse it in execution (usually
"leaking the requirement / losing the gap", "visible fixtures instead of
held-out", or "an obvious defect that does not survive reading").

## 5. Output format

```
#<n> (<id>) — HARD | NOT-HARD — <family> — <one-line reason; for NOT-HARD name the cap tag> — [confidence: high|med|low]
...

Totals: HARD = <k> (#…), NOT-HARD = <m> (#…)
Borderline / low-confidence: #…, #…
Note: static prediction only; empirical hard = frontier resolve < 1/3, confirmed by rollouts.
```

Per HARD idea, add one line: **Build guard** — the trap to avoid so the ceiling
survives construction. Per `req≡insight`/`stale-refresh`/`reading-comp` idea, add:
**Recommendation** — drop, or accept as medium.

## 6. Calibration anchors (match these, not generic intuition)

These are ground-truth-labelled `C2` "Rebuild before you claim" ideas. Use them
to keep verdicts consistent; a new idea that mirrors one should get its label.

**HARD (structural, gap holds):**
- *Input manifest one run behind* — import-time read vs main-body write (execution timing).
- *Both sides generated from one spec* — fixtures share the writer's bug; needs an independent recording. Gap: requirement ("reader decodes the deployed recording") ≠ insight.
- *Partial output fails to import* — write-guard branch treats parse-fail as nothing-to-do → silent fallback.
- *Map generated before the link* — build-graph dependency on objects not the linked artifact; only bites under parallelism.
- *Registry snapshot taken at import* — dispatch map snapshotted before lazy load (timing).
- *Consumer indexes the generated list* — positional coupling across two regenerated artifacts.
- *Annotation scanned in one configuration* — preprocessing config-coverage gap.

**NOT-HARD (cap noted):**
- *Bundled types one release behind* — stale bundle → re-point source (`stale-refresh`).
- *Table version below the floor* — bump a version constant (`stale-refresh`).
- *Template database still cloned* — re-migrate the template (`stale-refresh`).
- *Golden refreshed by the broken tool* — regenerate golden from rules (`stale-refresh`).
- *Generator version string not bumped* — add generator to the cache key (`stale-refresh`).
- *Inode reused by the write* — "detect content change under unchanged device+inode" is the fix stated as the requirement (`req≡insight`); also a cache-invalidation gotcha. **Medium** even after de-leaking.

## 7. Guardrails

- Judge the ceiling, not execution; never run or edit anything.
- Only `HARD` on positive structural evidence; otherwise lower the confidence,
  not raise the verdict.
- Long-horizon, adversarial, and constrained-build (SE) families have less
  calibration here than the verification family (the §6 anchors are all repair-family
  `C2`) — mark those verdicts `confidence: low|med` until SE anchors are measured.
- End every report with the reminder that only rollouts (frontier resolve < 1/3)
  confirm hard; this is a predictor to triage which ideas are worth building.
