# Quality Guidelines (Edition 2)

## High-level requirements

| Requirement | Summary |
|-------------|---------|
| **Instruction styling** | 1–2 problem paragraphs; requirements ≤2 paragraphs / ≤20 bullets; human voice, not LLM-polished |
| **Multi-step** | ≥5 terminal commands; intermediate state; reasoning/recovery; not one-shot |
| **Testable** | Fully specified; deterministic tests on final state |
| **Novel / unique** | No TB / Snorkel Ed1 variants; **≤ 15%** similarity to any existing task (local+platform) ([TASK_UNIQUENESS.md](TASK_UNIQUENESS.md)); no templated reskins |
| **No privileged ops** | No `--privileged` or unsafe Docker |
| **Standalone** | No human input after start; validated via Harbor |

## Scenarios to avoid

### 1. No latency-based tests

Do not assert p50/p95/p99, throughput, or “reasonable” timing. Test correctness only.

### 2. Identical testing for oracle and agent

Forbidden: detecting `/oracle`, setting `EVAL_IS_ORACLE`, different permissions, or conditional test logic for agent vs oracle.

### 3. Tag docker-compose / multi-container

In `task.toml` metadata when applicable: `custom_docker_compose = true`, `is_multi_container = true`. (New tasks of these types are not accepted in this repo.)

### 4. No runtime web fetching

Bundle data in the task repo. Package installs only at **image build** in Dockerfile — not in `test.sh` or `solve.sh` at runtime.

### 5. Do not create `/tests` or `/solution` in Dockerfile

Harbor reserves these paths at runtime.

### 6. Always write reward on failure

```bash
pytest ...
rc=$?

if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
```

Platform `check_test_sh` accepts both the inline `$?` form and `rc=$?` captured immediately after pytest; the variable form is preferred because any line between pytest and the conditional silently clobbers `$?`.

Never `exit` before the reward block. On standard (non-UI) tasks, the reward `if`/`else` block is the **canonical end of `test.sh`** — do not add a trailing `exit`. Harbor reads `/logs/verifier/reward.txt` for scoring, not the script exit code. Reviewers must not flag a missing trailing exit.

### 7. Default environment variables in test.sh

```bash
TEST_DIR="${TEST_DIR:-/tests}"
pytest "${TEST_DIR}/test_outputs.py" ...
```

Or hardcode `/tests/test_outputs.py`. Do not `exit 1` when `TEST_DIR` is unset.

### 8. No oracle-replication performance thresholds

Thresholds must reflect meaningful completion, not ~5% of oracle score. Multiple valid strategies should pass.

## Quick reference

| Rule | Summary |
|------|---------|
| No latency tests | Correctness only |
| Identical testing | Same env for oracle and agent |
| Tag compose | `custom_docker_compose = true` |
| Tag multi-container | `is_multi_container = true` |
| No web fetch | Local data only at runtime |
| Reserved dirs | Don't touch `/tests`, `/solution` in Dockerfile |
| Always write reward | `0` on failure |
| Default env vars | `${VAR:-default}` |

Repo-specific hardness policy: `docs/HARD_BUT_FAIR_AUTHORING.md`, `scripts/collapse_check.py`.

## Oracle and NOP agents

| Agent | Command | Expected |
|-------|---------|----------|
| **Oracle** | `harbor run -a oracle -p <task>` | **PASS** — proves task is solvable |
| **NOP** | (no-op baseline; runs verifier only) | **FAIL** (`reward.txt` = 0) — if NOP passes, task/verifier is wrong |

Oracle runs your `solution/solve.sh` then tests. Platform may run oracle multiple times; this repo requires oracle **10/10** at Step 4.

## Frontier agent testing (difficulty)

After oracle passes, run frontier models (evaluate **Hard → Medium → Easy**, stop at first match):

| Label | Rule |
|-------|------|
| **Hard** | ≤ 20% on **best** model, **or** ≤ 20% on **worst** model |
| **Medium** | 20% < worst ≤ 60% |
| **Easy** | 60% < worst ≤ 80% |
| **Reject** | worst > 80% |

```bash
harbor run -a terminus-2 -m openai/@openai/gpt-5.6 -p <task-folder>
harbor run -a terminus-2 -m anthropic/@anthropic/claude-opus-5 -p <task-folder>
```

Benchmark models for difficulty checks: **GPT-5.6** and **Claude Opus 5** (thresholds unchanged; stronger models may shift empirical MEDIUM/HARD labels — calibrate to these two).

Run each model multiple times (platform suggests ~5 per model) for stable pass rates. **Good failure:** reasoning errors, missed edge cases. **Bad failure:** unclear instructions, environment bugs — fix the task.

**Solvable vs passing:** oracle PASS proves the task is solvable; frontier-agent pass rate measures difficulty. A solvable task can still be too easy (worst model > 80% → reject band).

## Anti-cheating

- Dynamic/computed validation; answers not derivable from reading tests alone
- Reject: hardcoded pass values, guessable outputs, oracle copied from assertions
- Review watchlist: decompile hidden answers, swap in dummy binaries, delete/modify tests, unpinned git clones, ground truth in agent-writable paths
- Git repos in image: clone then `git checkout <commit>` at build time

## Test-quality eval flags (platform cross-check)

After normal test review, verify any platform test-quality flags:

| Flag | Meaning |
|------|---------|
| `req-gap` | Instruction requires something no test asserts |
| `weak-assertion` | Test too loose to catch wrong solutions |
| `phantom-spec` | Tests enforce undeclared behavior |
| `flaky-execution` | Correct solution can fail from timing or infra |
| `vacuous-test` | Test passes regardless of output |

The eval may miss real issues or flag acceptable tests — use judgment.

## Agent Review (platform)

Platform **Agent Review** is advisory — it does **not** block submission. Use it as a second pass for format, safety, and quality hints; local gates (`harbor tasks check`, oracle/NOP, repo Step 4) remain authoritative here.

## Rubric (platform UI — not in zip)

Synthetic rubrics are a starting point only — **edit for accuracy** before "Send to Reviewer".

- **≥ 3 distinct negative criteria** (e.g. `-1`, `-2`, `-3`, `-5` — never `-4`); milestone tasks: at least one negative per milestone (MEDIUM)
- **10–40** max cumulative positive points (non-milestone); per-milestone **10–40** each for milestones
- **Milestone layout:** `# Rubric 1`, `# Rubric 2`, … per milestone; non-milestone flat list (optional `# Rubric 1`)
- Positive language phrasing with negative scores for bad behavior (MEDIUM)
- Every line: starts with `Agent`, ends with `, <score>`; scores only **±1, 2, 3, or 5**
- Use **negative** scores for harmful behavior (do not flip severe negatives into minor positives)
- Do **not** reference pytest/`/tests/`, `task.toml`, `instruction.md`, or oracle/NOP runs
- Do **not** ship `rubrics.txt` (plural) in the zip — use required `rubric.txt`

## CI iteration workflow

```bash
harbor tasks check <task-folder> -m openai/@openai/gpt-5.6
```

Fix one failure at a time using [CI_CHECKS.md](CI_CHECKS.md). Re-run until all CI and LLMaJ checks pass, then oracle, then agents.
