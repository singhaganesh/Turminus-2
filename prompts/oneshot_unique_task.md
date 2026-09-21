# One-shot unique task creation

Token-cheap, evidence-gated prompt. Use this instead of the long idea generator
when the goal is **one finished task** that stays **≤ 15%** similar.

Why the old prompt failed: agents wrote “similarity 8%” from a mental audit.
The official checker only compares `tasks/`. This repo often has many `specs/`
and few finished tasks, so a spec/house-template clone can look unique until
later (80%). **Percentages without checker stdout are a lie.**

======================================================================
COPY-PASTE PROMPT START
======================================================================

Create ONE submission-ready Terminus 2.0 task. Do the full path. Do not stop at
an idea. Do not dump docs into chat.

INPUTS (fill; if missing, assume and state once):
- slug: <kebab-case or invent from JSON `id`>
- category: <JSON `domain`, or one of 9, or "any">
- milestone: 0 unless asked
- extra: <or none>
- idea_json: <paste JSON below, or "none">

If `idea_json` is present, it is the seed. Do not invent a different task.
Expected fields: `id`, `title`, `domain`, `premise`, `symptom`, `defect`,
`trap`, `why_hard`, `difficulty_summary`, `graded_on`, `capability`,
`capability_name`.
Public → instruction: `title`, `premise`, `symptom`, `graded_on`.
Author-only (never solver-visible): `defect`, `trap`, `why_hard`,
`difficulty_summary`. Still run occupancy + probe; if >15%, keep the same
core idea but change identity (artifact/command/voice), do not noun-swap.

READ ON DEMAND (do not paste them back):
- `terminus_blockers_checklist.txt`
- `prompts/terminus_task_category_guide.md` (3-question classifier only)
- `.cursor/rules/idea-validation.mdc` during spec
- `.cursor/rules/task-creation.mdc` while writing files
- `.cursor/rules/task-checker-ready.mdc` / `prompts/TASK_CHECKER.md` (P1–P5, R probes)
- `.cursor/rules/checker-lessons.mdc` (recurring ship-killers — never reintroduce)
- `prompts/AUTHOR_PRE_SHIP_PROBES.md` (R1–R9 probes, GAMEABLE traps, idempotent solve.sh, `preship/` R5/R6/R7)
- `docs/edition2/QUALITY_CRITERIA.md` (the review criteria to self-map; DIFFICULTY-FLOOR + caveat classes)
- `commands.md` for exact gate commands
- `docs/edition2/DOCKERFILE_BEST_PRACTICES.md` for the image

EVIDENCE LAW (blocking):
- Max similarity **15%**. Target **≤ 10%**. >15% = redesign identity, not wording.
- Never write a similarity %. Only quote a `Max similarity:` line from
  `scripts/uniqueness_probe.py` or `ci_checks/check-similarity.py` in this turn.
- Instruction-only pass is **not** enough. Official gate uses `--include-structure`
  (metadata + file paths + test names). Known failure: two Go tasks with
  `environment/cmd/driver/stages/` can be ~9% on prose and ~78% on structure.
- No PASS/READY/APPROVED/SUBMIT without the command stdout that proves it.

PEER LAYOUT (blocking — do not “stash” other tasks):
- Tasks live only at `tasks/<slug>/`. Never create or use `tasks/.peers/`,
  `tasks/.stash/`, or any `tasks/.*` directory for task trees.
- “Peer” in uniqueness docs means other dirs already under `tasks/` — it is
  **not** a folder name. Do not `mv`/`rename` existing `tasks/<other>/` out of
  the way to lower similarity or isolate concurrent work; that hides them from
  `check-similarity.py` (dotdirs are skipped) and is forbidden.
- If peers exist, keep them at `tasks/<other>/` and invent a distinct identity.

OCCUPIED FINGERPRINTS — reject a candidate that reuses any of:
domain, toolchain, artifact path, command/entrypoint, verifier shape,
instruction skeleton, oracle patch pattern, story arc, **layout_family**,
**env_roots topology**.

Structure identity (blocking): change **≥3** of these vs every occupied peer:
1. primary language  2. category  3. layout_family (see inventory)
4. env top-level directory set  5. entrypoint/command family
6. output artifact family  7. verifier assertion style

Forbidden reskins: CSV/ETL column swap; same bug-hunt topology; noun-swap
feature app; API wrapper/report/converter with a new label; clone of an
approved task or of a spec public contract; **same `cmd/driver/stages` (or
other house skeleton) with renamed packages**.

Do not reuse house sentences such as “Repair X under `/app/environment` so
`/app/bin/Y` regenerates `/app/output/Z.json`. Hand-written JSON is not
enough… Stay offline.” Vary voice, opening, artifact, command family, **and
directory topology**.

Hardness: `difficulty = "hard"` preferred, `"medium"` minimum (never `"easy"`)
vs **Claude Opus 5** and **GPT-5.6**. Plant checker P1–P5 and medium/hard levers
(`@task-checker-ready.mdc`, **`@checker-lessons.mdc`**, **`prompts/AUTHOR_PRE_SHIP_PROBES.md`**). Never reintroduce:
test-side rebuild (R5), NOP-passing graded tests, telegraphed defects, fat
vendor blobs / missing `.cargo` in the zip (R1), stubbable binaries (R7),
CLI wrappers that double-run the pipeline (GAMEABLE), non-idempotent `solve.sh`
(R8_twice / `NOT-IDEMPOTENT`), env notes that teach passing workarounds,
`tool_specific` without a tool tag, or oracle comments that narrate the bug.
Instruction alone must not be solvable. ≥3 discoveries not in the instruction.
≥3 coordinated loci. No new multi-container or UI tasks.

---

PHASE 0 — occupancy (required before inventing)
```
python3 scripts/uniqueness_probe.py inventory
```
Use privately. Note occupied categories, languages, **layout_family**,
**env_roots**, outputs, commands, instruction heads. Do not reuse an occupied
layout_family.

PHASE 1 — 3 candidates, keep 1
Invent ≥3 identities that miss every occupied fingerprint **including
structure**. Keep the strongest. Private card (no files yet):
- slug | honest category | langs | layout_family (must be free) | shape
- one-line job
- 5 unique properties vs occupied set
- public outputs + entrypoint
- env top-level dirs (must not mirror a peer’s topology)
- why Opus 5 / GPT-5.6 still fail
- trap the verifier must defeat

Classifier: start state / main reasoning / verifier proof. Set `category` to
that answer. Do not relabel.

Hardness screen (BLOCKING, before PHASE 2): run the kept identity through the
`tb2-check-idea-hardness` skill and `@idea-validation.mdc` #19/#20/#22/#24. The
decisive one is the **GAP test (#24)**: if the tests cannot grade the outcome
without the instruction stating the fix (requirement ≡ insight), the idea caps at
medium — deepen or drop, do not proceed. Also require symptoms-only framing (#20)
and ≥3 non-derivable discoveries (#19).

PHASE 2 — instruction probe BEFORE the rest of the tree
Write ONLY `/tmp/<slug>-instruction.md` in final human voice (absolute paths,
no hints, every tested requirement stated). Then:
```
python3 scripts/uniqueness_probe.py probe \
  --instruction /tmp/<slug>-instruction.md \
  --exclude <slug>
```
If exit 1 or any `FAIL:`: delete the draft, new identity, return to PHASE 1.
Do not synonym-swap.

PHASE 2b — structure plan BEFORE creating `tasks/<slug>/`
Write `/tmp/<slug>-structure.txt` with metadata + ≥5 planned `path:` lines
(real env modules, not only Harbor boilerplate). Keys: `category`,
`languages`, `difficulty`, `codebase_size`, `path: environment/...`,
`test: test_...`. Then:
```
python3 scripts/uniqueness_probe.py structure-plan \
  --manifest /tmp/<slug>-structure.txt \
  --instruction /tmp/<slug>-instruction.md \
  --exclude <slug>
```
If exit 1: new topology (different layout_family / env_roots), return to
PHASE 1. Do not create `tasks/<slug>/` until instruction **and** structure-plan
both print `Similarity within allowed band` (≤15%, prefer ≤10%).

PHASE 3 — spec, no task files
```
python3 scripts/tb3_doctor.py
python3 scripts/validate_loop.py init <slug>
```
Follow `prompts/step2a.md` + `@idea-validation.mdc`. GO spec at
`specs/<slug>.md` then:
```
python3 scripts/validate_loop.py finalize <slug>
python3 scripts/lint_spec.py specs/<slug>.md --strict
python3 scripts/spec_satisfiability.py specs/<slug>.md --strict
python3 scripts/reference_task_check.py specs/<slug>.md --strict
```
Fail → amend spec, do not draft `tasks/`.

PHASE 4 — construct once, then mid-build structure gate
Follow `@task-creation.mdc` and `prompts/Step2b.md`. Create
`tasks/<slug>/` from the spec commitments. Pin image digest. `allow_internet =
false`. Deps in Dockerfile. Canonical `tests/test.sh`. Instruction = probed
draft (edit only if contract changes; then re-run PHASE 2).

Design the graded suite to clear **DIFFICULTY-FLOOR**: ≥2 capability classes
(recompute/consistency, variant/holdout, fault rejection, sequencing/recovery),
or 1 + ≥3 execution-dependent tests. For each graded class, satisfy the caveat
audit three legs (instruction states rule · env tempts wrong move · solution
shows right move).

Also author the anti-cheat probe fixtures in `tasks/<slug>/preship/` (a
task-root dir the packager excludes from the zip; see
`prompts/AUTHOR_PRE_SHIP_PROBES.md`):
`preship.json`, `source_only.sh` (R5), `decoy_fix.sh` (R6), `shortcut_fix.sh`
(R7) — each must leave reward 0.

As soon as instruction + env skeleton + test stubs exist (before polishing
oracle):
```
python3 scripts/uniqueness_probe.py structure \
  --task-dir tasks/<slug> --exclude <slug>
python3 ci_checks/check-similarity.py tasks/<slug> \
  --include-structure --enforce-threshold
```
If either FAILs: delete/rebuild topology; do not rename modules under the same
`cmd/driver/stages` (or equivalent) skeleton.

PHASE 5 — gates (fix and continue; no fake pass)
```
python3 scripts/spec_satisfiability.py specs/<slug>.md --task-dir tasks/<slug> --strict
python3 ci_checks/check-similarity.py tasks/<slug> --include-structure --enforce-threshold
python3 scripts/task_gate.py tasks/<slug> --strict --report-dir /tmp/tb3-gates --skip-harbor
python3 scripts/difficulty_floor_check.py tasks/<slug> --strict   # BLOCKER: >=2 capability classes
python3 scripts/caveat_audit_check.py tasks/<slug>                # advisory: graded classes + leg-1 hint
./scripts/check-task.sh --strict --report-dir /tmp/tb3-gates tasks/<slug>  # includes Phase C3 (R5/R6/R7)
python3 scripts/oracle_idempotency_probe.py tasks/<slug> --strict --report-dir /tmp/tb3-gates
python3 scripts/preship_probes.py tasks/<slug> --strict --report-dir /tmp/tb3-gates  # R5/R6/R7 must be reward 0
python3 scripts/harbor_gate.py tasks/<slug> --oracle --nop
python3 scripts/step2b_ready.py tasks/<slug> --strict --report-dir /tmp/tb3-gates \
  --oracle-job-dir jobs/<oracle> --nop-job-dir jobs/<nop>
python3 scripts/harbor_gate.py tasks/<slug> --oracle-repeat 10
python3 scripts/package_task.py tasks/<slug> --out Task_Ready_To_Submit/<slug>.zip --validate
# Spot-check zip vs @checker-lessons.mdc (cargo .cargo+checksums if vendored;
# no >1MB members; tests have no _rebuild; instruction has no mechanism spoilers).
python3 scripts/first_look_packet.py tasks/<slug> --out /tmp/<slug>-first-look.txt
```
Then Step 5 rubric + Step 6 notes (UI only; `prompts/Step5.md`, `Step6.md`).
Then `scripts/approve_task.py --strict` per `commands.md`.

After any instruction or env-layout edit, re-run instruction `probe` and
`structure`. If either fails, redesign; do not polish.

CHAT REPORT (short):
- slug, honest category vs requested, layout_family
- pasted uniqueness stdout: probe + structure-plan + structure + final
  check-similarity --include-structure
- 5 unique properties (include topology differences)
- 7 acceptance checks: no overreach, no coverage gap, no leakage, oracle 1.0,
  NOP 0.0, anti-cheat, actionable instruction
- DIFFICULTY-FLOOR: capability classes hit (≥2); caveat legs per graded class
- preship R5/R6/R7: each reward 0 (paste `preship_probes.py` status)
- gates run + blockers
- ready only if approve_task.py exited 0

======================================================================
COPY-PASTE PROMPT END
======================================================================

## Operator notes

JSON idea: paste the object into `idea_json` above, **or** use `prompts/prompt.md`
and replace `[PASTE JSON IDEA HERE]`. Both run the same uniqueness + one-shot path.

Category-locked run: keep `category:` filled and add “honest category must stay `<name>`”.

Idea-bank only (no files): use `prompts/terminus_unique_task_generator_prompt.md`.
Still run `uniqueness_probe.py inventory` first and do not claim a %.
