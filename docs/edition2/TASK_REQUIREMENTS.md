# Task Requirements (Edition 2)

## Structural layout

| File | Required | Notes |
|------|----------|-------|
| `task.toml` | Yes | `task_type`, `subcategories`, `number_of_milestones`, `difficulty`, `codebase_size`, `languages`, `tags`, `runtime_limits` |
| `environment/Dockerfile` | Yes | Or `docker-compose.yaml` for multi-container (new multi-container tasks not accepted in this repo) |
| `instruction.md` | Non-milestone | Human-style prompt |
| `solution/solve.sh` | Non-milestone | Deterministic oracle |
| `tests/test.sh` | Non-milestone | Writes `/logs/verifier/reward.txt` |
| `tests/test_outputs.py` | Non-milestone | Pytest, docstrings on every test |
| `steps/milestone_N/` | Milestone | Per-milestone `instruction.md`, `tests/`, `solution/` |

**Codebase size** (files under `environment/`, not agent outputs): `minimal` ≈ 0–19, `small` ≈ 20–200, `large` ≈ 200+.

## instruction.md — six principles

1. **Concise** — ~1–3 paragraphs problem; requirements in ≤2 paragraphs / ≤20 bullets.
2. **Well specified** — Clear goal; reject tasks hard only via hidden edge-case laundry lists.
3. **Interesting** — Real engineering value.
4. **No answers/hints** — What, not how.
5. **Unique** — Distinct from TB2, TB3, Snorkel Edition 1, and every other task in this repo. **Maximum allowed similarity: 15%** (local + platform); **> 15% is blocking**. No clone-and-rename or templated instruction/verifier shapes. See [TASK_UNIQUENESS.md](TASK_UNIQUENESS.md).
6. **Absolute paths** — e.g. `/app/output/report.json`.

No legacy **canary strings** in `instruction.md`. See [INSTRUCTION_STYLING.md](INSTRUCTION_STYLING.md).

## task.toml

- `version = "2.0"`
- `[metadata]`: author (anonymous OK), difficulty, category, subcategories, `number_of_milestones`, `codebase_size`, `languages`, `tags` (3–6), time estimates
- `[verifier].timeout_sec`, `[agent].timeout_sec`, `[environment].build_timeout_sec`
- **`[environment] allow_internet = false`** (required)
- Milestone: `[[steps]]` count = `number_of_milestones`; per-step `[steps.agent]` / `[steps.verifier]`; no root `[agent]`/`[verifier]`

## Solution (`solve.sh`)

- Human-authored command sequence; deterministic; self-contained; idempotent
- Demonstrates **how** to derive the answer — not hardcoded outputs or echo-the-answer shortcuts
- `set -e` acceptable in `solve.sh` (unlike `test.sh`)
- No runtime internet; use seeds for any randomness
- Must solve every requirement in `instruction.md` (including untested ones)
- Milestone: `steps/milestone_N/solution/solve.sh` wrapper + `solveN.sh` scoped to N only
- Verify: `harbor run -a oracle -p <task-folder>`

## Tests

- Every explicit and implicit instruction requirement → test
- Docstrings on every test; verify **behavior**, not implementation
- Anti-cheating: dynamic/computed checks, depth, non-guessable from tests
- No latency/performance assertions
- **Identical** conditions for oracle and agent (no `/oracle` branching in `test.sh`)
- `test.sh` always writes reward (`1` or `0`); never exit before the reward block; on standard tasks the reward `if`/`else` is the script end (no trailing `exit` — Harbor scores `reward.txt`, not exit code)
- `TEST_DIR="${TEST_DIR:-/tests}"` when using `TEST_DIR`
- Dependencies **pre-installed in Dockerfile**; no runtime network in `test.sh`

## Security

- No privileged containers
- Do not `COPY` `solution/` or `tests/` into image
- Do not create or modify `/tests` or `/solution` in Dockerfile
- Minimal attack surface; build context stays in `environment/`

## Difficulty (platform agent runs)

| Tier | Threshold |
|------|-----------|
| Hard | ≤ 20% on best model **or** ≤ 20% on worst |
| Medium | 20% < worst ≤ 60% |
| Easy | 60% < worst ≤ 80% |
| Reject | worst > 80% |

## Anti-cheating

- Dynamic/computed validation; multiple aspects; answers not derivable from tests
- Reject: solution copied from assertions, guessable outputs, hardcoded pass values
- Review for cheat paths: decompile hidden answers, swap in dummy binaries, delete/modify tests, unpinned git clones, ground truth in agent-writable locations
- Git repos in image: clone then `git checkout <commit>` at build time

## Rubric (submission UI)

- Edit synthetic platform draft — do not submit unreviewed
- **≥ 3 distinct negative criteria** (`-1`, `-2`, `-3`, `-5` only — never `-4`)
- Non-milestone: **10–40** max cumulative positive points; milestones: **10–40 per milestone**
- Format: each line starts with `Agent`, ends with `, <score>`; scores **±1, 2, 3, or 5** only
- **Milestone tasks:** split the rubric into one block per milestone using `# Rubric 1`, `# Rubric 2`, etc. header lines (the CI parser expects this format)
- **Non-milestone tasks:** flat list of `Agent …, ±N` lines; a single `# Rubric 1` header is tolerated but not required
- No criteria about pytest, `/tests/`, `task.toml`, `instruction.md`, or oracle/NOP
- Penalize harmful behavior with negatives; do not rephrase severe negatives as weak positives
- See `prompts/Step5.md` and platform Rubrics Guidelines

## Submission explanation fields (platform UI)

Three paragraphs on the upload form after zip validation. **Not in zip.**

- **Difficulty Explanation** — why humans/agents struggle
- **Solution Explanation** — high-level oracle approach
- **Verification Explanation** — how tests verify behavior

~4–6 sentences each. Author voice; see `prompts/Step6.md` for style rules (no em dashes,
minimal backticks, no comma-stuffed LLM tone). Optional local copy:
`sample_task/submission-notes/<task-name>.txt`.

## Automated checks (must pass)

**CI (blocking):** `pinned_dependencies`, `check_pinned_images`, `check_sanctioned_base_images`, `check_build_context_size`, `typos`, `tests_or_solution_in_image`, `check_dockerfile_references`, `check_test_sh`, `check_task_absolute_path`, `check_privileged_containers`, `ruff`, `check_task_sizes`, `validate_task_fields`, `test_deps_in_image`, `check_canary`

**CI (warnings — see [CI_CHECKS.md](CI_CHECKS.md)):** `check_dockerignore`, `check_dockerfile_hygiene`, `check_offline_tests`, `check_apt_usage`, `check_reproducible_builds`, `check_layer_volatility`, `check_no_build_tools_in_runtime`, `check_file_extraction`, `check_heredoc_usage`, `check_recursive_permissions`

**LLMaJ:** `behavior_in_task_description`, `behavior_in_tests`, `informative_test_docstrings`, `anti_cheating_measures`, `hardcoded_solution`, `file_reference_mentioned`, `structured_data_schema`

See [CI_CHECKS.md](CI_CHECKS.md) and [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md).

## Repo-only artifacts (not in submission zip)

`output_contract.toml`, `construction_manifest.json`, `waivers.json`, `quality_check_adjudication.json`, `rubric*.txt`, `.step2b-checksum`, AI scaffolding — see `AGENTS.md` zip bans.
