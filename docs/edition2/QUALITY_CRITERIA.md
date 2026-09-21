# Quality criteria — author self-map (internal)

The review side scores each defect against **one** criterion from the table below
and emits a `quality_check.md`. **You do not emit that report.** Use this table
while authoring to self-map: every finding you fix maps to exactly one criterion,
so nothing is double-counted or missed. Fix at construction time what the review
would otherwise bounce.

Score each defect **once**. A Go Dockerfile that does not build is `verifiable`
(R1), not also `solvable`, `environment_hygiene`, and `category_and_tags`.
Instruction how-to / fixture names are `instruction_concision` (`HINTS` /
`PRESCRIPTIVE`), not `anti_cheat_robustness` if R5 and R7 stayed 0. Pytest on the
agent PATH is `environment_hygiene`. Static `DIFFICULTY-FLOOR` is the
`difficulty_floor` gate. P1 / P3 / P5 / a `broken` caveat class live on
`difficult`. Assessed `too_easy` / `ambushes` are labels, not gate fails.

| id | Pass when | Fail only when |
|---|---|---|
| `verifiable` | Suite exists, pytest pinned, `test.sh` runs it on the authored image | R1; 0 tests; runner never starts. Home for "image does not build". |
| `solvable` | `solve.sh` derives the fix (not `echo` of fixtures) and R4 reward 1 | Hardcoded oracle; R4 reward 0. **Not** R1 — that is `verifiable`. |
| `difficult` | P1–P5 hold with quoted evidence; graded caveat classes not `broken` | P1 lookup; P3 R5=1; P5 NOP-PASS; a graded caveat class `broken`. `DIFFICULTY-FLOOR` is the `difficulty_floor` gate, not this. |
| `interesting` | A working engineer would recognise the job | Toy / generated scaffolding only |
| `outcome_verified` | Tests assert behaviour of the artifact the agent produces | `IMPL-TEST`; grading source text |
| `anti_cheat_robustness` | R5 stays 0; R7 stays 0; tests do not auto-rebuild; tests/oracle/rubric not in agent tree; **if native required, tests assert ELF on the rebuilt binary** | R5=1; R7>0; suite rebuilds the binary; `GAMEABLE-NATIVE` (native required but no ELF assert → Python/shell mill scores R7=1). Doc spoilers are `HINTS`, not this — unless they make a shortcut score 1. |
| `task_security` | No secrets, no runtime net beyond package install, no privileged, no harness-dir wipe | `NET-AT-RUNTIME`; `SECRET`; `PRIVILEGED` |
| `functional_verification` | Tests run the program and compare structured output | Keyword scan of agent source |
| `deterministic_reproducible` | R8 identical reward 1; pins; no unseeded RNG in suite | R8 fail; floating `latest`. |
| `essential_difficulty` | Hard part is the planted defect, not schema/format plumbing | Instruction already names the constant the tests want |
| `test_instruction_alignment` | Stated requirements are tested; those tests flip (fail R3, pass R4) | Core requirement untested; inverted / scenery test. Unstated extras are MINOR `UNSPECIFIED-GRADING` — do not fail this gate if a correct solution still passes them and the stated contract is graded. |
| `novel` | Not a re-skin visible in this batch | Same mechanism, different nouns |
| `agentic` | ≥5 chained commands, intermediate state, not one-shot | Lookup + instruction names the file |
| `reviewable` | A reviewer can recompute expected values from instruction + env without `solution/` | Hidden convention |
| `instruction_concision` | ≤3 paragraphs, ≤20 requirement bullets, no how-to, absolute paths | `VERBOSE-INSTRUCTION`; `HINTS`; `PRESCRIPTIVE` |
| `solution_quality` | Strict mode, derives answer, idempotent, no tests/ edits | `HARDCODED-SOLUTION`; `NO-STRICT-MODE` |
| `environment_hygiene` | No tests/solution COPY; apt cleaned; pytest not on agent PATH; no leftover bak | `TEST-DEPS-IN-IMAGE`; `STALE-FILES`; `RESERVED-DIR`. |
| `structured_data_schema` | If JSON/CSV/YAML required, fields are stated | `SCHEMA-UNSPECIFIED` |
| `typos` | Names and instruction paths resolve | `A3.11` |
| `category_and_tags` | Category fits; 3–6 specific tags | Missing category; tag count outside 3–6. Do not fail because claimed difficulty differs from assessed level — the ladder is advisory. |
| `no_extraneous_files` | Every shipped file is referenced or a planted decoy | Dead file with a "not used" comment |
| `verifier_execution_isolation` | `/tests` not in the agent image; reward from pytest rc | Suite COPY; reward from agent-writable file |
| `binary_reward` | `reward.txt` is literal 0/1 from pytest rc, both branches | `NO-REWARD-FILE` |

## Blocking gates (the review side's Harbor subset)

`verifiable`, `solvable`, `difficulty_floor`, `outcome_verified`,
`anti_cheat_robustness`, `task_security`, `functional_verification`,
`deterministic_reproducible`, `test_instruction_alignment`, `agentic`,
`environment_hygiene`, `structured_data_schema`, `typos`, `category_and_tags`,
`no_extraneous_files`, `verifier_execution_isolation`, `binary_reward`.

`difficulty_floor` is the static `DIFFICULTY-FLOOR` BLOCKER (≥2 capability
classes, or 1 + ≥3 execution-dependent tests) — enforced by
`scripts/difficulty_floor_check.py`. It is not `too_easy` and not P1.

## Programme overrides (this repo wins over raw review text)

- `difficulty` must be `medium` or `hard` — never `easy` (the review ladder is
  advisory; this programme's floor is not). See `.cursor/rules/task-checker-ready.mdc`.
- pytest pinned under `/opt/verifier` in `environment/Dockerfile`, **off** agent
  PATH; `test.sh` invokes the absolute path and installs nothing. Do not fail
  ship solely on `TEST-DEPS-IN-IMAGE` for that isolated-prefix layout.
- Similarity ≤ 15% (target ≤ 10%).

## Mapping to the automated gates

| Review criterion / tag | Author-side gate |
|---|---|
| `difficulty_floor` / `DIFFICULTY-FLOOR` | `scripts/difficulty_floor_check.py` (Phase B, blocks `--strict`) |
| caveat class `broken` | `scripts/caveat_audit_check.py` (advisory) + 3-leg self-audit |
| `anti_cheat_robustness` (R5/R7), decoy (R6) | `scripts/preship_probes.py` (Phase C3) |
| `GAMEABLE-NATIVE` (native required, no ELF assert) | `scripts/native_binary_check.py` (Phase B, blocks `--strict`) |
| `FALSE-FAILURE` (test rejects a valid solution) | `scripts/false_failure_lint.py` (Phase B) + ALT probe in `preship_probes.py` (expect_reward 1) |
| `deterministic_reproducible` (R8) | `scripts/oracle_idempotency_probe.py` (Phase C2) |
| `verifiable`/`solvable` (R1/R3/R4/R9) | `scripts/harbor_gate.py` + `smoke_task.sh` |
| rubric format, pins, paths, hygiene | `scripts/run_static_checks.py` (Phase A) |
| `SPEC-DRIFT` (SE build ≠ idea `spec`/facets/held-out) | spec-fidelity self-audit (`.cursor/rules/task-checker-ready.mdc`) — SE form of `MECHANISM-DRIFT` |
| `NAIVE-PASSES` (SE naive impl passes graded suite) | `naive_impl.sh` probe in `preship_probes.py` (expect_reward 0) |
| `HAPPY-PATH-ONLY` (SE graded on visible cases only) | `happy_path_only.sh` probe (expect_reward 0) + SE `spec_coverage`/`protocol_conformance` floor classes |
| `MEDIA-EXACT` (video/perceptual output graded byte-exact) | `false_failure_lint.py` INVERSE rule — flags byte-exact media asserts even if instruction claims byte-identical |
| `UNSTATED-TOLERANCE` (video graded to an exactness the instruction never stated) | authoring check `idea-validation.mdc` #26 — `graded_on` must state the frame range / L2 / SSIM tolerance |
| video floor via tolerance/conformance | `difficulty_floor_check.py` `media_conformance` class (submiter-only) |

**Shape note.** Repair (`repair_existing_system`) tasks use symptoms-only
instructions and the R5/R6/R7 probes; non-repair (`constrained_build`/SE) tasks
state the full spec and use the `naive_impl`/`happy_path_only`/`spec_gaming` probes.
Both share `false_failure_lint`, `native_binary_check`, the ALT probe (expect 1),
and the `difficulty_floor` gate (which now detects SE capability classes too).

**Video-processing note.** `video-processing` is a `constrained_build`
specialization. Grade with a STATED tolerance (inclusive frame range, ±N frames,
L2/SSIM/PSNR ≥ threshold) — byte-exact media output is a false failure (the
`false_failure_lint` INVERSE rule enforces this). Discriminator = a held-out test
video (example video visible only). Environment: pinned digest base image with
fixed `cv2`/`ffmpeg`/`numpy` for deterministic decode (R8 must hold),
`allow_internet = false`, all video fixtures bundled locally (never a
download-a-video task). Floor is met via the `media_conformance` class.
