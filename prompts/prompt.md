Convert the JSON task idea below into one complete submission-ready Terminus 2.0 task with the highest practical chance of one-shot acceptance. Do the full workflow end to end. Do not stop at ideation or drafting.

TASK IDEA (JSON):
```json
[PASTE JSON IDEA HERE]
```

Expected JSON fields (shape-dependent — read `task_shape` first):
- **Always:** `id`, `title`, `domain`, `premise`, `why_hard`, `difficulty_summary`, `graded_on`, `capability`, `capability_name`, and `task_shape` (one of `repair_existing_system` | `constrained_build` | `reverse_engineering` | `optimization_under_constraints` | `adversarial_generalization` | `formal_reasoning`; if absent, infer from `domain` — `debugging` ⇒ `repair_existing_system`, `software-engineering` ⇒ `constrained_build`).
- **Repair shape only** (`repair_existing_system`): `symptom`, `defect`, `trap`.
- **Non-repair shapes** (SE / `constrained_build` etc.): `spec` (the capability contract to implement), `hardness_source` (why *building* it correctly is hard — protocol/concurrency/edge coverage/format), `adversarial_cases` (held-out inputs a naive implementation fails), and optional `trap` (the plausible-but-wrong implementation to defeat). These play the author-only role that `defect` plays for repair.

Everything below branches on **repair vs non-repair**. `.cursor/rules/idea-validation.mdc` is the source of truth for the shape branch (`task_shape`, `instruction_framing`, `hardness_source`); this prompt obeys it.

Read and obey:
`prompts/oneshot_unique_task.md` (full workflow + uniqueness evidence law),
`AGENTS.md`, `terminus_blockers_checklist.txt`, `prompts/terminus_task_category_guide.md`,
`.cursor/rules/unique-task-generation.mdc`, `.cursor/rules/submission-category-blocklist.mdc`,
`.cursor/rules/difficulty-calibration.mdc`, `.cursor/rules/idea-validation.mdc`,
`.cursor/rules/task-checker-ready.mdc`, `.cursor/rules/checker-lessons.mdc`,
`prompts/TASK_CHECKER.md`, `prompts/AUTHOR_PRE_SHIP_PROBES.md`,
`docs/edition2/QUALITY_CRITERIA.md`,
`docs/HARD_BUT_FAIR_AUTHORING.md`, `commands.md`.

Mandatory policy:
- All 9 primary categories are open. Classify honestly. Do not relabel.
- Difficulty: metadata + checker complexity must be **`medium` or `hard`**
  (prefer hard; never easy). Empirically vs **Claude Opus 5** and **GPT-5.6**.
  Author to pass `prompts/TASK_CHECKER.md` via `.cursor/rules/task-checker-ready.mdc`.
- Max similarity **15%**, target **10% or lower**. Never invent a %. Run
  `python3 scripts/uniqueness_probe.py inventory`, then `probe`, then
  `structure-plan` before creating `tasks/`, then `structure` +
  `check-similarity.py --include-structure` after the skeleton exists.
  Instruction-only is not enough (same `cmd/driver/stages` house layout can
  be ~9% prose / ~78% structure).
- No templated/shallow/reskin tasks. Do not invent unsupported fields/commands.
- Never move, rename, or stash other tasks under `tasks/.peers/`, `tasks/.stash/`,
  or any `tasks/.*` path. Canonical location is only `tasks/<slug>/`. “Peer” is
  vocabulary for other tasks already under `tasks/`, not a directory to create.

What to do:
- Follow `prompts/oneshot_unique_task.md` end to end.
- Preserve the core spirit of the JSON idea (`premise`, `graded_on`, hardness).
- If too easy, too similar, weak, misclassified, leaky, or blocker-prone, revise
  structurally. If unrepaired, propose 2 stronger nearby variants, pick one, continue.

Phase 0 — substrate gate (run BEFORE creating `tasks/`, right after idea validation):

**Difficulty comes from the PROBLEM, not the environment or the vocabulary.** Not
resource pressure, not verbose instructions, not trick formatting, not extra edge
cases or decoys bolted onto a shallow core, and NOT bespoke nouns dressing up a
trivial bug. If the core problem is easy, no wrapping and no renaming make it hard
— a frontier model decodes the vocabulary in seconds and finds the one bug.

**The four-point depth test — an idea must pass ALL FOUR to reach `medium`/`hard`.**
There are two calibrated variants; use the one matching `task_shape`.

**(A) REPAIR shape (`repair_existing_system`).** Calibrated against this repo's
measured-hard repair tasks (`holdtrace-forge`, `crashsig-rail`,
`stackfold-prelude`); all four hit every point.

1. **Generator, not runtime.** The bug lives in a code generator / rebuild /
   codegen / compile / regeneration step, so scoring depends on regenerating and
   the model cannot pass by editing the artifact it can see. (holdtrace: `forge`
   regenerates emit+consume; crashsig: `compile` regenerates SIGNATURE_OWNERS;
   stackfold: `render` regenerates the symmap.)
2. **≥3 independent insights.** Three or more distinct realisations where fixing
   one does NOT reveal the others. The same fix applied in two files is ONE
   insight, not two. (crashsig: import-recovery + key-normalise + completeness +
   fault-path. sheetlag-rivet, done right: stale-snapshot source + field order +
   wrong count basis.)
3. **Unfakeable discriminator.** The graded artifact is something the agent
   cannot see or fabricate — a deployed/archived input made by the OLD code, a
   held-out sample the agent never sees, or a corruption/fault-recovery path.
   Self-generated fixtures that share the bug are invisible; only the independent
   authority catches it. (holdtrace: deployed `lane_ops.trc`; stackfold: held-out
   lines; crashsig: corrupted-map recovery check.)
4. **Applied domain knowledge.** Solving needs specialised knowledge actually
   applied, not recalled — binary wire formats, linker symbol layout, module
   import/codegen semantics, etc.

**(B) NON-REPAIR shape (`constrained_build` / software-engineering, and the other
non-repair shapes).** Here there is no hidden defect to diagnose — the agent is
implementing a stated capability. Hardness comes from *building it correctly*, not
from finding a bug. An SE idea must pass ALL FOUR:

1. **Naive implementation fails.** The obvious first-pass implementation a
   competent engineer writes from the spec passes the visible/happy-path cases but
   FAILS the graded suite. If a straightforward implementation passes everything,
   the task is easy — reject. (This is the SE analog of "generator, not runtime":
   the difficulty is real implementation complexity, not scenery.)
2. **≥3 independent, interacting spec facets.** Three or more distinct
   requirements where getting one right does not give you the others, and a
   correct solution must satisfy all together (e.g. protocol framing + ordering +
   backpressure; or grammar + precedence + error recovery). Satisfying one facet
   must not reveal or auto-satisfy another.
3. **Unfakeable conformance discriminator.** The graded suite includes held-out /
   adversarial inputs the agent never sees and cannot hardcode to — the
   implementation must GENERALIZE (a hidden conformance corpus, randomized-then-
   fixed cases, an independent reference the impl is checked against). A solution
   that special-cases the visible examples fails.
4. **Applied domain knowledge.** Building it correctly needs specialised knowledge
   actually applied — protocol/RFC semantics, language/grammar rules, concurrency
   and memory-model correctness, wire/format conformance, numerical stability, etc.

**The GAP test (decisive — apply FIRST). Branch on shape.**

- **REPAIR shape:** Can the tests grade the outcome *without the instruction
  stating the fix*? If the fair, must-be-stated requirement **is** the insight,
  the idea caps at medium and no de-leak saves it — stating what you grade states
  the fix. Examples that fail: "detect a changed file even when device+inode are
  unchanged" (that literally tells the agent to content-address); "compare the
  live tree to the newest snapshot" (that is the whole bug). Contrast the
  measured-hard tasks, which all have a gap: the requirement is an OUTCOME ("the
  reader decodes the deployed recording", "the new function resolves by name")
  while the insight (shared-fixture cancellation, build-graph parallelism) is
  separate and must be discovered. **If requirement ≡ insight → reject; hardening
  cannot help.**

- **NON-REPAIR shape (SE):** requirement ≡ spec is NORMAL and REQUIRED — you MUST
  state the full capability contract; hiding it would be an ambush (false
  failure). So the repair GAP test does not apply. The decisive SE gate instead
  is the **naive-implementation test**: *does the obvious implementation written
  straight from the stated spec pass the entire graded suite?* If YES → easy,
  reject (or deepen the spec: add interacting facets + a held-out conformance
  corpus a naive impl fails). If NO — because the graded suite exercises
  adversarial/held-out cases, interacting facets, concurrency, or conformance a
  first-pass impl gets wrong — the idea can be hard even though the spec is fully
  stated. Do NOT reject a non-repair idea merely because the instruction states
  the requirement; that is expected. Reject only when a naive impl passes.

**Instruction framing (`idea-validation.mdc` #20) — branch on shape.**
- **REPAIR:** instruction must be **symptoms-only**. State the operator-visible
  SYMPTOM and the required output CONTRACT; never the cause, the fix location, the
  mechanism, or a per-step recipe. A cause-revealing instruction ("the CRC uses
  half the payload") makes it spec-implementation, which frontier models one-shot.
- **NON-REPAIR (SE):** instruction must be **spec-complete but solution-open**
  (`design-brief` | `behavioral-target` | `constraint-complete`). State the FULL
  capability contract, the interface, and every verifier-relevant constraint —
  that is fair and required. Never state the *implementation strategy* (which
  algorithm/data structure/library to use) or hand over the adversarial cases; the
  solver must design the solution. Spec-complete is REQUIRED for SE; it is NOT the
  forbidden "spec-implementation" (that failure is stating the solution strategy
  AND having a naive impl pass — see the naive-impl gate).

**Discovery / difficulty budget (`idea-validation.mdc` #19) — branch on shape.**
- **REPAIR:** name ≥3 discoveries the solver must extract that are NOT stated or
  directly derivable from the instruction, each with where it lives and why the
  instruction must not reveal it. If you cannot name 3, or every item is "find
  where code doesn't match the stated spec", the idea is easy — reject.
- **NON-REPAIR (SE):** name ≥3 independent, interacting spec facets a correct
  implementation must get right together, PLUS the held-out/adversarial cases a
  naive impl fails. If you cannot name 3 interacting facets, or a first-pass impl
  passes the graded suite, the idea is easy — reject or deepen the spec.

**Run the screen.** Before writing any `tasks/` file, run the idea through the
`tb2-check-idea-hardness` skill (and `@idea-validation.mdc` #17–#22). Proceed only
on a `HARD` verdict with the gap holding; otherwise deepen or drop.

**Undergraduate test (fast reject):** could a competent junior engineer solve the
core in an afternoon with no research? If yes, it fails — usually because it has
only ONE insight (point 2) findable by grep from the symptom.

**Deepen, do not replace.** When an idea misses a point, add depth *inside* the
given `premise`/`domain`, using `why_hard`/`difficulty_summary` as intent — move
the bug into a generator, split the fix into ≥3 independent insights, add a
held-out/deployed/recovery discriminator, require real domain knowledge. Do NOT
drift from the JSON `domain`/`premise`, and do NOT build decoys/anti-cheat onto a
core that misses these points — fix the substrate first.

**Do not leak the insights (checked again in Phase 4, flagged here).**
- **REPAIR:** a deep task still fails if the instruction telegraphs the insights:
  naming the field-order rule, the count guard, the fix location, or the mechanism
  hands the model the realisations for free. State the operator-visible SYMPTOM and
  the required output RULE; never the fix or the per-insight recipe.
- **NON-REPAIR (SE):** the spec IS stated (required). What you must NOT leak is the
  *implementation strategy* and the *held-out/adversarial cases*: never name the
  algorithm/data structure to use, and never expose the hidden conformance corpus
  or how the discriminator distinguishes a correct impl from a naive one.

Record the verdict in the final output: which of the four points the idea hits,
and the concrete deepening applied for any it missed. This gate is upfront on
purpose — catch a shallow or leaky core before building the whole task around it.

Field usage (critical):
- `domain` → preferred primary category; still run honest 3-question classifier. Prefer keeping `domain` honest; if conflict, revise construction so dominant work matches `domain`, or reclassify honestly and report the drift.
- `title` / `premise` → public system behavior and instruction framing.
- `symptom` (repair only) → observable solver-visible symptoms only (no root-cause wording).
- `spec` (non-repair only) → PUBLIC. The full capability contract belongs in `instruction.md`; stating it is required, not a leak.
- `graded_on` → public success contract + verifier plan. Every graded claim must appear as an explicit instruction requirement and a matching test.
- `defect` / `trap` / `why_hard` / `difficulty_summary` → AUTHOR-ONLY. Use them to plant the failure, anti-cheat, and hardness. NEVER put them in `instruction.md`, comments, filenames, decoys, or other solver-visible surfaces.
- `hardness_source` / `adversarial_cases` (non-repair only) → AUTHOR-ONLY. `adversarial_cases` become the held-out conformance grading; never expose them or the impl strategy in solver-visible files.
- `capability` / `capability_name` / `id` → author metadata only; do not invent unsupported `task.toml` fields from them.

**Mechanism / spec fidelity (BLOCKING — the built task must BE this idea). Branch on shape.**
- **REPAIR:** the idea's hardness lives in its `defect` mechanism, not its domain.
  Build that exact mechanism — do not substitute an easier same-domain task (e.g. a
  format/grammar parser in place of the idea's real defect). Before claiming done,
  quote the idea's `defect` verbatim and map each part of it to the built task: the
  exact file and the broken line that realizes it. If any part of the `defect` has
  no home in the built files, the build has drifted off the idea — rebuild against
  the idea's mechanism; do not report done.
- **NON-REPAIR (SE):** the hardness lives in the idea's `spec` + `hardness_source`
  + `adversarial_cases`. Before claiming done, quote each and map it to the built
  task: (a) the stated contract in `instruction.md` matches `spec`; (b) each of the
  ≥3 interacting facets is exercised by a test; (c) the `adversarial_cases` /
  held-out conformance corpus is actually graded (not just happy-path). If the
  built suite only checks the happy path, or a naive impl would pass it, the build
  has drifted off the idea — deepen it; do not report done.

A task sharing the idea's domain but not its mechanism/spec is a drift failure and
is rejected.

Acceptance-critical checks (must satisfy all):
1. **No overreach / no false failures:** Tests must not require behavior absent from instructions, and must accept every valid solution — no exact-bytes / whole-output / digest / fixed-order assertion unless the instruction states that exact form. `graded_on` must be fully stated in the public contract. Prove it: author `tasks/<slug>/preship/alt_solution.sh` (a different-but-correct solution) declared as `"ALT": {"script":"alt_solution.sh","expect_reward":1}` — it must score reward 1 — and keep `scripts/false_failure_lint.py` clean. **Video / perceptual output (INVERSE rule):** for `video-processing` and any decoded-frame/stream/image output, byte-exact/whole-output/digest comparison is ITSELF a false failure (encoder/codec/opencv variance). Grade with a STATED tolerance — inclusive frame range, ±N frames, or L2/SSIM/PSNR ≥ threshold — and state that tolerance in `instruction.md` (an unstated tolerance is also a false failure). `false_failure_lint.py` enforces this: it flags byte-exact media asserts even when the instruction claims byte-identical.
2. **No coverage gap:** Every explicit instruction requirement maps to ≥1 test, including every claim in `graded_on`.
3. **No leakage:** Never expose `defect`, `trap`, solution logic, exact fix-path lists, hidden tests, verifier strategy, oracle internals, or reward behavior in solver-visible files.
4. **Solvable task:** Oracle must pass all verifier checks at least once.
5. **Non-triviality proof:** NOP/baseline must **fail** (expected mean 0.0).
6. **Anti-cheat robustness:** Explicitly defeat the JSON `trap` and block hardcoding, test gaming, output stuffing, and grading-criteria mimicry without genuine solving. Author the `tasks/<slug>/preship/` probes and confirm all score their declared `expect_reward` via `scripts/preship_probes.py --strict`. **REPAIR shape:** `source_only.sh` R5, `decoy_fix.sh` R6, `shortcut_fix.sh` R7 (all reward 0). **NON-REPAIR (SE) shape:** `naive_impl.sh` (the obvious first-pass impl — reward 0), `happy_path_only.sh` (passes visible cases, fails held-out — reward 0), `spec_gaming.sh` (hardcodes the visible outputs — reward 0). **Both shapes:** `alt_solution.sh` (a different-but-correct solution — reward 1). **If the task requires a native binary** (native/ELF/"a script is not enough"), the graded suite MUST assert ELF magic (`\x7fELF`) on the agent binary **after rebuild** — an ELF check only in `solve.sh` does not count; a Python/shell mill emitting correct output otherwise scores R7=1 (`GAMEABLE-NATIVE`). When native, `shortcut_fix.sh` must include the script-replacement cheat. Verify with `scripts/native_binary_check.py`.
7. **Actionable instructions:** `instruction.md` must specify required behavior, outputs, constraints, and absolute paths from `premise` + `symptom` + `graded_on` — not vague "make X" language.

Acceptance-quality bar:
- Target `difficulty = "hard"` (or `"medium"` minimum) using `why_hard` /
  `difficulty_summary` as design intent, without leaking them. Never `"easy"`.
- Plant checker floor P1–P5 and enough levers for checker level medium/hard
  (`.cursor/rules/task-checker-ready.mdc`).
- Satisfy the deterministic **DIFFICULTY-FLOOR**: the suite must exercise ≥2
  capability classes or 1 + ≥3 execution-dependent tests. Verify with
  `python3 scripts/difficulty_floor_check.py tasks/<slug> --strict`. Repair
  classes: recompute/consistency, variant/holdout, fault rejection,
  sequencing/recovery. Non-repair (SE) classes also count: spec_coverage,
  interface_contract, protocol_conformance, concurrency_safety.
- For every graded capability class, satisfy the **caveat audit** three legs
  (instruction states the rule · env tempts the wrong move · solution shows the
  right move). Enumerate classes with `scripts/caveat_audit_check.py`.
- Prefer non-Python if it fits; otherwise choose the best honest stack.
- Use only current required files and metadata.
- Follow current `reference_pattern` policy if applicable.
- Tests validate behavior, not source shape, unless structure is explicitly required.
- Remove all blockers before finalizing.

Environment bar:
- Canonical digest-pinned base image when required.
- `[environment] allow_internet = false`.
- Install pytest in `environment/Dockerfile`; `tests/test.sh` must not install
  (no `uvx` / pip / apt).
- Deterministic, repo-compliant environment.

Workflow bar:
- Complete idea validation, spec creation, task creation, required gates, harbor/oracle/NOP checks, packaging, Step 5 rubric, Step 6 notes, first-look, and strict approval flow exactly as required by the repo.
- If any check fails, fix honestly and continue.
- Do not stop at a partial result.
- Do not claim PASS, READY, APPROVED, ACCEPT, or SUBMIT unless command output proves it.

Final output:
- Phase 0 substrate verdict: the `task_shape`, then which of the four depth points
  the idea hits — REPAIR variant (generator / ≥3 independent insights / unfakeable
  discriminator / applied domain knowledge) or NON-REPAIR variant (naive impl fails
  / ≥3 interacting facets / unfakeable conformance discriminator / applied domain
  knowledge) — plus any deepening applied and confirmation the instruction does not
  leak (repair: the insights; SE: the impl strategy + held-out cases)
- mechanism / spec fidelity map: REPAIR — the idea's `defect` quoted verbatim, each
  part mapped to the exact built file+line; NON-REPAIR — `spec` / `hardness_source`
  / `adversarial_cases` quoted, each mapped to the stated contract, the facet tests,
  and the held-out conformance grading (drift = reject)
- mapped JSON field usage summary (public vs author-only)
- honest category vs `domain`
- uniqueness audit
- difficulty analysis vs Claude Opus 5 and GPT-5.6
- acceptance-critical checks verdict (all 7), including how `trap` was blocked
- commands/checks run
- final blocker status
- whether the task is truly ready for submission


"don't use python language for task creation use another best language"