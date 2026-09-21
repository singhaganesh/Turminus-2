# Step 1: Idea Generation (ChatGPT)

Platform shape bar for seeds (before Step 2a): `docs/edition2/TASK_REQUIREMENTS.md`,
`docs/edition2/QUALITY_GUIDELINES.md` — multi-step (not one-shot), novel vs TB/Ed1,
testable, no latency tests, no multi-container/UI new starts.
Also screen seed ideas against `terminus_blockers_checklist.txt`; do not carry
forward ideas that would predictably hit empirical difficulty below **MEDIUM**
for **Claude Opus 5** and **GPT-5.6** (prefer HARD; Easy/Trivial = reject),
fail `prompts/TASK_CHECKER.md` floor (P1–P4 / R5/R7), internet/runtime
dependency, test alignment, answer leakage, nondeterminism, milestone layout,
long-context, rubric, or packaging blockers.

Every primary category is open. Keep the seed bank category-balanced across the
full taxonomy (`debugging`, `software-engineering`, `data-processing`,
`system-administration`, `build-and-dependency-management`, `games`,
`machine-learning`, `security`, `scientific-computing`). Classify honestly with
`prompts/terminus_task_category_guide.md`. Do not relabel debugging, software-
engineering, or data-processing work as another category just to dodge taxonomy.

Use these two prompts in order.

## Prompt 1 (Option B - build seed bank)

Run Option B from `web/bulk-idea-generation.md` in goal-sized mode across all
nine open categories. The final target after Option A is 150 Step-2a-ready seeds.
Keep the bank category-balanced, keep Topology distinct within category, and
return one downloadable `.md` seed-bank file. Prefer seeds that would still be
hard for Claude Opus 5 and GPT-5.6 using the current platform thresholds in
`@difficulty-calibration.mdc` Part E.

## Prompt 2 (Option A - refine/consolidate bank)

Run Option A from `web/option-a-seed-refinement.md` in step2a-bank mode against the attached bulk-ideas file.
The final target is 150 Step-2a-ready seeds.
Repair or replace weak seeds instead of collapsing to a tiny shortlist.
Keep all nine open categories balanced, keep Topology distinct within category,
and return one downloadable `.md` file. Drop or harden any seed that would
saturate Opus 5 or GPT-5.6.
