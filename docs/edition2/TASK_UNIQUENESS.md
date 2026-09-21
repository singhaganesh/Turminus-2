# Task Uniqueness (Edition 2)

Every submitted task must be **genuinely unique** — not a reskin, clone, or templated variant of an existing task in this repo, prior Terminus/Snorkel editions, TBench.ai, or open-source benchmarks.

## Platform + local rule

- **Maximum allowed similarity: 15%** (`0.15`) to any existing task — **same limit locally and on platform**.
- **Target:** stay **≤ 10%** when possible; **> 15%** is a **blocking** uniqueness failure (local Phase A2 and platform review).
- Do **not** submit tasks that differ only by nouns, file names, or a single swapped subsystem while keeping the same instruction shape, environment layout, verifier structure, or oracle patch pattern.
- New-task drafting MUST follow `.cursor/rules/unique-task-generation.mdc` and
  `prompts/oneshot_unique_task.md`. Idea banks may still use
  `prompts/terminus_unique_task_generator_prompt.md`.

## What counts as “too similar”

Reject or redesign when the candidate shares more than the allowed similarity band with another task on:

| Signal | Examples of templated reuse |
|--------|----------------------------|
| Instruction prose | Same opening/closing shape, shared schema block, recycled “symptoms-only repair under `/app`” skeleton |
| Task shape | Same repair topology, same JSON report contract, same milestone progression pattern |
| Environment layout | Same directory topology with renamed modules (`pkg_a/foo.py` → `pkg_b/foo.py`) |
| Verifier design | Same test names/assertion clusters with token substitution |
| Oracle pattern | Same `solve.sh` structure (heredoc rewrites, identical phase order) with cosmetic edits |

**Allowed:** Standard Harbor file layout (`instruction.md`, `task.toml`, `tests/test.sh`, …) alone is **not** duplication. Shared *structure* only matters when it encodes reused task **shape**, shallow edit frontiers, or templated verifier design.

## Authoring requirements

1. **No clone-and-rename** — Do not start from an approved task and swap domain nouns.
2. **No house template** — Vary instruction voice, length, and structure across tasks (see [INSTRUCTION_STYLING.md](INSTRUCTION_STYLING.md)). Do not copy the same “Repair X under `/app` … schema block” shape task after task.
3. **Distinct topology** — Step 2a must pass the topology-distribution and discovery-budget checks (`@idea-validation.mdc` checks 19–21). One-function exploit loci trivialize even when wording differs.
4. **Reference tasks calibrate; they do not clone** — Use `reference_task_id` for hardness calibration, not as a Dockerfile/instruction/test template (`docs/HARD_BUT_FAIR_AUTHORING.md`).

## Local check

Authoring uniqueness (run **before** and **during** construction):

```bash
python3 scripts/uniqueness_probe.py inventory
python3 scripts/uniqueness_probe.py probe \
  --instruction /tmp/<task-name>-instruction.md \
  --exclude <task-name>
python3 scripts/uniqueness_probe.py structure-plan \
  --manifest /tmp/<task-name>-structure.txt \
  --instruction /tmp/<task-name>-instruction.md \
  --exclude <task-name>
```

After the env skeleton exists:

```bash
python3 scripts/uniqueness_probe.py structure \
  --task-dir tasks/<task-name> --exclude <task-name>
```

`inventory` prints occupied **layout_family** values (e.g. `go-cmd-driver-stages`).
Reusing an occupied family is a hard authoring FAIL even if instruction prose
looks different. Instruction-only probes miss this: the same Go
`cmd/driver/stages` house layout has measured ~9% prose / ~78% structure.

This scores drafts against local `tasks/` **and** `specs/` public-contract
text. `ci_checks/check-similarity.py` compares finished task dirs under
`tasks/` (use `--include-structure` before submit).

From repo root (compares against other tasks under `tasks/`):

```bash
python3 ci_checks/check-similarity.py tasks/<task-name> \
  --include-structure \
  --enforce-threshold
```

Early instruction-only official probe (still `tasks/` peers only; **not** a
structure pass):

```bash
python3 ci_checks/check-similarity.py --draft-instruction /tmp/<task-name>-instruction.md \
  --enforce-threshold
```

- Default local threshold: **15%** (`0.15`) — matches the platform uniqueness gate
  (`SIMILARITY_ALERT_THRESHOLD` in `ci_checks/check-similarity.py`).
- Target **≤ 10%** when possible; `--threshold` may still be passed explicitly if needed.
- `--include-structure` also scores `task.toml` metadata, visible file names, and test names (required before submit).
- Strict Step 2b preflight (`./scripts/check-task.sh --strict`) runs this check when `tasks/` contains peer tasks.
- Never quote a similarity percentage except from checker stdout.

## Reviewer feedback category: **Uniqueness**

Flag under **Uniqueness** when:

- Similarity search or local check reports **> 15%** to any peer task.
- Instruction/environment/verifier reads like a find-replace of an existing submission.
- Multiple tasks in the same batch share the same narrative arc, schema fan-out, or “three-file Rust repair + sweep_report.json” pattern without distinct causal structure.

**Consequence:** High-severity rejection; redesign from a new idea or substantially new topology — not a wording pass.
