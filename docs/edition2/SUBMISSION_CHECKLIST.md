# Submission Checklist (Edition 2)

Use before upload. Repo Step 4 adds mechanical gates — see `prompts/step4.md` and `commands.md`.

## Task design

- [ ] Clear, unambiguous problem; explicit requirements
- [ ] **Unique task** — not a reskin or template of an existing task; **≤ 15%** similarity local+platform ([TASK_UNIQUENESS.md](TASK_UNIQUENESS.md); `.cursor/rules/unique-task-generation.mdc`)
- [ ] Absolute paths; output files named; schemas specified
- [ ] Difficulty target: worst-model pass rate **< 80%**

## Required files

**Always:** `task.toml`, `environment/Dockerfile` (builds, pinned)

**Non-milestone (`number_of_milestones = 0`):**

- [ ] `instruction.md` — human-written ([INSTRUCTION_STYLING.md](INSTRUCTION_STYLING.md))
- [ ] `solution/solve.sh` — deterministic oracle
- [ ] `tests/test.sh` — reward file ([HARBOR_COMPONENTS.md](HARBOR_COMPONENTS.md))
- [ ] `tests/test_outputs.py` — docstrings, behavior tests

**Milestone (`number_of_milestones >= 2`):**

- [ ] `[[steps]]` count = `number_of_milestones`
- [ ] No root `instruction.md`, `tests/`, `solution/`
- [ ] Each `steps/milestone_N/`: `instruction.md`, `tests/test.sh`, `test_mN.py`, `solution/solve.sh`, `solution/solveN.sh`

## Rubric (Snorkel platform UI)

- [ ] Synthetic rubric generated then **edited** for accuracy
- [ ] **≥ 3 negative criteria** (e.g. `-1`; never `-4`)
- [ ] 10–40 positive points (non-milestone); per-milestone scaling for milestones
- [ ] See `TASK_PROPOSAL_RUBRIC.md` / `prompts/Step5.md`

## Quality

- [ ] Requirement ↔ test coverage (explicit, implicit, edge cases)
- [ ] Anti-cheating; behavior not implementation
- [ ] [QUALITY_GUIDELINES.md](QUALITY_GUIDELINES.md)

## Automated verification

### Oracle (must PASS)

```bash
harbor run -a oracle -p <task-folder>
```

Local: `python3 scripts/harbor_gate.py tasks/<task> --oracle --nop`

### NOP (must FAIL at 0.0)

NOP performs no work; validates verifier wiring. If NOP scores > 0, fix tests or environment.

### CI (`harbor tasks check`)

```bash
harbor tasks check <task-folder> -m openai/@openai/gpt-5.6
```

Fix failures one at a time — see [CI_CHECKS.md](CI_CHECKS.md) for per-check fixes.

- [ ] All blocking CI checks pass
- [ ] Dockerfile warnings addressed when practical (`check_dockerignore`, `check_layer_volatility`, …)

### LLMaJ (via `harbor tasks check`)

- [ ] behavior_in_task_description, behavior_in_tests
- [ ] informative_test_docstrings, anti_cheating_measures
- [ ] structured_data_schema, hardcoded_solution, file_reference_mentioned

## Real agent testing (platform)

```bash
harbor run -a terminus-2 -m openai/@openai/gpt-5.6 -p <task-folder>   # ×3 runs
harbor run -a terminus-2 -m anthropic/@anthropic/claude-opus-5 -p <task-folder>   # ×2 runs
```

Difficulty-check models were upgraded: tasks are benchmarked against **Claude Opus 5** and **GPT-5.6** (previously Opus 4.8 and GPT-5.5). Thresholds and EASY/MEDIUM/HARD bands are unchanged — only the benchmark models changed. Because the new models are stronger, tasks that previously rated MEDIUM or HARD may land Easy; calibrate accordingly.

| Difficulty | Threshold |
|------------|-----------|
| Hard | ≤ 20% best **or** ≤ 20% worst |
| Medium | 20% < worst ≤ 60% |
| Easy | 60% < worst ≤ 80% |
| Reject | worst > 80% |

Record best-model and worst-model pass rates; set `difficulty` in metadata to match empirical band where required.

## Repo Step 4 (before platform upload)

- [ ] `python3 scripts/step2b_ready.py` PASS
- [ ] `python3 scripts/harbor_gate.py --oracle-repeat 10` — 10/10
- [ ] `python3 scripts/package_task.py --validate`
- [ ] First-look PASS (`docs/FIRST_LOOK_DRY_RUN.md`)
- [ ] `python3 scripts/approve_task.py --strict` exit 0

## Self-check

1. First-time reader understands the task?
2. Any ambiguous requirements?
3. Could an agent cheat?
4. Tests verify behavior?
5. Solution deterministic?

## Platform submit

1. Download task skeleton from platform **Resources** when starting fresh
2. Upload ZIP; keep **Send to reviewer** unchecked; enable rubric generation on first pass
3. After CI email, **Revise** → fix blocking checks using [CI_CHECKS.md](CI_CHECKS.md)
4. Edit rubric in UI (≥3 negatives; 10–40 points); **Agent Review** is advisory only — does not block upload
5. Final submit: uncheck rubric regeneration; check **Send to reviewer**

- [ ] ZIP of **files at archive root** (not the containing folder)
- [ ] Non-milestone: `instruction.md`, `task.toml`, `environment/`, `solution/`, `tests/`
- [ ] Milestone: `task.toml`, `environment/`, `steps/milestone_N/…` only — no root `instruction.md` / `tests/` / `solution/`
- [ ] Exclude repo-local metadata per `AGENTS.md` (`output_contract.toml`, `rubrics.txt`, AI scaffolding, …)
- [ ] Rubric edited in platform UI (≥3 negatives; 10–40 points); uncheck "regenerate rubric" before final "Send to Reviewer"
- [ ] Upload to terminus-project-v2; metadata filled in

**Common zip mistakes:** extra wrapper folder; missing files; `jobs/` or root `README.md` in archive; nested `rubrics.txt`.

Do not claim PASS/READY without command output (`AGENTS.md`).
