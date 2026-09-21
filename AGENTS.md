# AGENTS.md

TB3 Ed2. Unit: `tasks/<task-name>/`. Start: `docs/ARCHITECTURE.md`;
platform bar: `docs/edition2/`; policy/rules: `docs/HARD_BUT_FAIR_AUTHORING.md`,
`.cursor/rules/`, `commands.md`. Practical reviewer blockers:
`terminus_blockers_checklist.txt`.

## Must

1. No PASS/READY/APPROVED/SUBMIT claim without command output.
2. Long run: `python3 scripts/tb3_doctor.py`.
3. New-task gate: `lint_spec` -> `spec_satisfiability` -> `task_gate` ->
   `check-task.sh` -> `oracle_idempotency_probe.py --strict` ->
   `harbor_gate --oracle --nop` -> `step2b_ready` ->
   `harbor_gate --oracle-repeat 10` -> `package_task --validate` ->
   Step 5 rubric + Step 6 submission notes (UI only, chat handoff) ->
   first-look -> `approve_task.py --strict`; exact commands in `commands.md`.
4. `check-task.sh` is only preflight; Harbor, first-look, zip, approval remain.
5. Task edits stale Step 2b evidence; approval checks `.step2b-checksum`.
6. Do not invent paths, `task.toml` fields, or commands; open source/commands.
7. Host Python is not container Python; task `python3` needs Dockerfile support.
8. If terminal output disappears, run `echo visible`; else use a fresh shell.
9. Milestones: `steps/milestone_N/{instruction.md,tests/,solution/}`,
   `version="2.0"`, matching `[[steps]]`.
10. No new multi-container/UI starts; in-progress may finish.
11. All nine primary categories are open (`debugging`, `software-engineering`, `data-processing`, `system-administration`, `build-and-dependency-management`, `games`, `machine-learning`, `security`, `scientific-computing`). Classify honestly; do not relabel. See `.cursor/rules/submission-category-blocklist.mdc` and `prompts/terminus_task_category_guide.md`. Empirical difficulty is judged on **Claude Opus 5** and **GPT-5.6**. Metadata and checker complexity must be **`medium` or `hard`** (floor medium; prefer hard). `easy` / `too_easy` do not ship.
12. New tasks must be strictly unique (≤ **15%** similarity local+platform; target ≤ 10%). Never invent a similarity %. Run `python3 scripts/uniqueness_probe.py inventory` then `probe` + `structure-plan` before creating `tasks/`, then `structure` after the skeleton. Official dir check: `python3 ci_checks/check-similarity.py tasks/<task> --include-structure --enforce-threshold`. Instruction-only is not enough. Follow `.cursor/rules/unique-task-generation.mdc` and `prompts/oneshot_unique_task.md`. Never stash or move peer tasks under `tasks/.peers/` or any `tasks/.*` path — only `tasks/<slug>/` is valid.
13. Before new task drafting, task revision, packaging, or approval, check
 `terminus_blockers_checklist.txt` and remove any blocker it names. Also author to pass
 `prompts/TASK_CHECKER.md` via `.cursor/rules/task-checker-ready.mdc` and
 `.cursor/rules/checker-lessons.mdc` (P1–P5; R1–R9; no recurring ship-killers;
 `prompts/AUTHOR_PRE_SHIP_PROBES.md` for R8 twice / GAMEABLE traps;
 `rubric.txt` required; pytest in Dockerfile, not `test.sh`). After fixes, always
 re-run `package_task.py --validate` and verify zip fingerprints (especially Rust
 `.cargo/` + checksums) — the checker scores the zip, not the chat tree.

Zip bans: `output_contract.toml`, `quality_check_adjudication.json`,
`construction_manifest.json`, `waivers.json`, `rubrics.txt` (plural),
`.step2b-checksum`, AI scaffolding (`AGENTS.md`, `.cursor/`, `.claude/`,
`.aider/`, `.continue/`, `skills.md`). **`rubric.txt` is required** at the task
and archive root (checker format). Do **not** put a `[rubric]` table in
`task.toml` (`package_task.py` strips it; zip validation rejects it). Step 6
submission notes remain UI-only; see `prompts/Step6.md`.
