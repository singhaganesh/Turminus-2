TERMINUS UNIQUE TASK GENERATOR PROMPT
Version: 2026-09-04
Purpose: Idea-bank only (N blueprints, no `tasks/` files). For one finished
task with a real ≤15% uniqueness gate, use `prompts/oneshot_unique_task.md`.

Do not claim a similarity percentage. Run
`python3 scripts/uniqueness_probe.py inventory` before inventing, and
`python3 scripts/uniqueness_probe.py probe --instruction <draft.md>` before
any blueprint is treated as unique. `check-similarity.py` vs `tasks/` alone
misses spec/house-template clones. Never create `tasks/.peers/` or move
existing tasks into any `tasks/.*` stash — “peer” means other dirs under
`tasks/`, not a folder to invent.

======================================================================
COPY-PASTE PROMPT START
======================================================================

You are generating high-quality Terminus/Harbor Edition 2 task ideas.

Before creating any task idea, first verify the latest public requirements from the official/current docs. Do not rely only on memory. Read and apply, at minimum, the current docs or pages for:
1. Task Requirements
2. Task Components
3. Submission Checklist
4. Diversity Requirements
5. Prompt Styling
6. Task Taxonomy
7. Milestones, if milestone tasks are requested
8. Writing Tests / Oracle Solution / Running Oracle, if available

After checking the current requirements, silently analyze them and use them as hard constraints. In the final answer, briefly mention the requirement set you applied, but do not dump long documentation summaries unless asked.

ALL PRIMARY CATEGORIES ARE OPEN:
- debugging
- software-engineering
- data-processing
- system-administration
- build-and-dependency-management
- games
- machine-learning
- security
- scientific-computing
Assign the honest dominant category with the three-question classifier in
prompts/terminus_task_category_guide.md. Include every category in candidate
matrices unless the user names a narrower preferred list. Do not relabel
debugging, software-engineering, or data-processing work as another category.

DIFFICULTY BENCHMARK (CURRENT):
Calibrate ideas for **Claude Opus 5** and **GPT-5.6** only. Do not treat success
or failure on weaker earlier models as evidence the task is hard.
Target `difficulty = "hard"` metadata preferred; `"medium"` is the minimum floor
(never `"easy"`). Plant checker P1–P5 / medium-or-hard levers
(`prompts/TASK_CHECKER.md`, `.cursor/rules/task-checker-ready.mdc`). Empirical
bands (Hard → Medium → Easy, stop at first match) on those two models:
- HARD: accuracy ≤ 20% on the best model, or else ≤ 20% on the worst model
- MEDIUM: 20% < accuracy ≤ 60% on the worst model
- EASY: 60% < accuracy ≤ 80% on the worst model (**reject** — below programme floor)
Prefer ideas whose residual work would still fail those two models often.

INPUTS I WILL PROVIDE:
- Number of task ideas needed: <N>
- Task mode: <milestone / non-milestone / either>
- Category filter: <list, or "none" meaning all nine categories are in play>
- Preferred categories: <list, or "none">
- Previously used task ideas/categories/domains/features: <paste list, or "none">
- Required output format: <txt file / markdown / direct answer>
- Extra constraints: <anything else>

CORE GOAL:
Generate <N> task ideas that are all meaningfully distinct from each other and from the previously used ideas. Each task must be realistic, terminal-executable, verifiable by automated tests, non-trivial, and capable of passing all unit tests at least once through an oracle/reference solution.

HARD REQUIREMENTS TO APPLY:
1. Every task must be self-contained inside one task directory.
2. Required files must be considered:
   - instruction.md
   - task.toml
   - environment/Dockerfile or docker-compose.yaml if needed
   - solution/solve.sh
   - tests/test.sh
   - tests/test_outputs.py
3. task.toml must include the current required metadata/configuration fields, including category/task type, subcategories where applicable, number_of_milestones, difficulty, codebase_size, languages, tags, expert/junior estimates if required, and runtime limits.
4. tests/test.sh must produce a reward file in /logs/verifier/, normally /logs/verifier/reward.txt or /logs/verifier/reward.json.
5. Tests must validate behavior, not just implementation details.
6. Every explicit instruction requirement must map to at least one test.
7. Tests must include docstrings when Python tests are proposed.
8. The oracle solution must be deterministic, self-contained, idempotent, and able to pass the verifier at least once.
9. Dependencies and base images must be pinned. Avoid floating latest tags.
10. The solution must not be baked into the Docker image.
11. Test dependencies must not be pre-installed in a way that violates current checks.
12. The task must use absolute paths in instruction.md.
13. The instruction must be concise, human-sounding, clear, and well specified.
14. The instruction must not contain answers, hidden solution logic, step-by-step solving hints, or excessive structured rubrics.
15. The task must be resistant to shortcut/hardcoded solutions.
16. The output file names and schemas must be explicitly specified where relevant.
17. The task should target hard model difficulty on Claude Opus 5 and GPT-5.6, not easy. Medium is the ship floor when Hard cannot be reached fairly. Plant checker P1–P5 / medium+ levers (`prompts/TASK_CHECKER.md`).
18. Prefer small or large codebase sizes if current diversity rules block minimal tasks.
19. Prefer milestone tasks if current diversity rules prefer them, unless the user asks for non-milestone.
20. If the task uses Python as the main language, ensure the idea is hard enough to satisfy current Python-task acceptance expectations.
21. All nine primary categories are open. Set `category` to the honest dominant activity. Debugging, software-engineering, and data-processing are first-class options. If the user supplies a category filter, stay inside that filter; otherwise draw from the full taxonomy and keep the batch category-diverse.
22. If milestone tasks are requested:
   - include number_of_milestones > 0
   - describe each milestone as a prerequisite for the next
   - include milestone_x.md files only if currently required
   - include solution/solve1.sh through solution/solveN.sh
   - include tests/test_m1.py through tests/test_mN.py
   - ensure each solveX.sh and test_mX.py is scoped only to milestone X
   - include solution/solve.sh as the full chained solution
23. If non-milestone tasks are requested:
   - number_of_milestones must be 0
   - do not include milestone files
   - avoid describing the task as staged milestone validation


UNIQUENESS / SIMILARITY GATE (REPO POLICY):
- Maximum allowed similarity to any existing peer: **15%** (0.15).
- Never write a similarity %. Quote `Max similarity:` from
  `scripts/uniqueness_probe.py` (tasks + specs, authoring gate) or
  `ci_checks/check-similarity.py` (finished `tasks/` dir).
- Run inventory before inventing; probe a final-voice instruction draft
  before treating an idea as unique. A mental audit is invalid.
- Target: stay ≤ 10% when possible. Anything > 15% must be rejected and
  replaced with a new identity (not a wording pass).
- Still require ≥5 unique properties vs peers on domain/toolchain/artifact/
  challenge/verifier. Shallow reskins fail even if TF-IDF sneaks under 15%.

UNIQUENESS REQUIREMENTS:
For every idea, perform a uniqueness audit before presenting it.

Reject and replace any idea that overlaps too much with another idea or with previous ideas in:
- domain
- category
- dataset type
- toolchain
- required artifact
- main algorithmic challenge
- failure mode
- verifier strategy
- story/use case
- output format
- environment shape

Each accepted idea must have at least five unique properties compared with the other accepted ideas.

Do not create shallow variations like:
- another CSV parser with different column names
- another log analyzer with different labels
- another API wrapper with different endpoint names
- another debugging / software-engineering / data-processing clone that only swaps nouns, bugs, schemas, or file names (those categories are open; shallow clones are not)
- another reconciliation/reporting task if one was already used
- another image/audio/text converter unless the core challenge is truly different

TASK IDEA GENERATION PROCESS:
1. Build a private matrix of candidate domains, categories, tools, artifacts, and verification methods. Include all nine open categories unless the user filtered.
2. Remove previously used patterns and shallow clones. Do not drop debugging, software-engineering, or data-processing from the matrix.
3. Generate at least 2x the requested number of candidate ideas.
4. Score candidates for:
   - uniqueness
   - realism
   - testability
   - hard difficulty vs Claude Opus 5 and GPT-5.6 (medium only as a fair floor)
   - anti-cheating strength
   - oracle solvability
   - current-requirement compliance
5. Select only the strongest <N>.
6. For each selected idea, produce a complete task blueprint.

FOR EACH TASK IDEA, OUTPUT THIS EXACT STRUCTURE:

============================================================
TASK <number>: <unique task title>
============================================================

1. Core Identity
- Category:
- Subcategories:
- Milestone or Non-Milestone:
- Number of milestones:
- Codebase size:
- Main language(s):
- Tags:
- Expected difficulty:
- Why it is hard for Claude Opus 5 and GPT-5.6:

2. One-Line Task Summary
- <one concise sentence>

3. Realistic User-Style instruction.md Draft
Write a concise instruction that sounds like a real human asking a terminal agent to complete the work.
Rules:
- Use absolute paths.
- Do not give solution hints.
- Do not include a step-by-step algorithm.
- Do not overuse markdown.
- Mention required output files and schemas when needed.
- Keep it short but unambiguous.

4. Starting Repository / Environment
Describe the internal files that would exist before the agent starts.
Include:
- app/code files
- data/config files
- broken/incomplete components
- any services or containers
- any special constraints

5. Required Output / Final State
Specify exactly what the agent must produce or change.
Include:
- output file paths
- schemas/formats
- success conditions
- invalid states to avoid

6. Oracle Solution Plan
Describe what solution/solve.sh would do at a high level.
Do not give a trivial copy-paste answer, but make it clear the task is solvable.
Mention why it is deterministic and idempotent.

7. Test Plan
Describe tests/test.sh and tests/test_outputs.py.
Include at least:
- existence tests
- schema/format tests
- behavioral tests
- edge-case tests
- anti-cheating tests
- reward-file behavior

8. Anti-Cheating Design
Explain how the verifier prevents:
- hardcoded outputs
- copying answers from tests
- superficial file creation
- ignoring edge cases
- implementation-only hacks

9. Milestone Plan
If milestone task:
- Milestone 1:
- Milestone 2:
- Milestone 3:
- Extra milestones if needed:
- Each milestone's test file:
- Each milestone's solution file:
If non-milestone:
- State: Not applicable. number_of_milestones = 0.

10. task.toml Blueprint
Provide a concise TOML-style metadata blueprint with:
- version
- metadata/category/subcategories/number_of_milestones/difficulty/codebase_size/languages/tags
- expert_time_estimate_min
- junior_time_estimate_min
- verifier timeout
- agent timeout
- environment build timeout/resources

11. Required Files Checklist
List the exact files this task would include:
- instruction.md
- task.toml
- environment/Dockerfile
- solution/solve.sh
- tests/test.sh
- tests/test_outputs.py
- milestone files only if applicable
- any app/data files

12. Uniqueness Audit
- What makes this different from previous tasks:
- What makes this different from the other ideas in this batch:
- Unique properties, minimum 5:
  1.
  2.
  3.
  4.
  5.

13. Acceptance Confidence
- Oracle should pass at least once: yes/no and why
- Real-agent difficulty target (Opus 5 / GPT-5.6):
- Main rejection risks:
- Fixes to avoid those risks:

FINAL GLOBAL CHECKLIST:
After all task ideas, include this section:

GLOBAL COMPLIANCE CHECK
- Honest category from the full open taxonomy (debugging / software-engineering / data-processing allowed when they dominate):
- All ideas are distinct:
- Category policy reflects all nine open categories:
- Hard vs Opus 5 / GPT-5.6 (medium only as a fair floor):
- Absolute paths included in instruction drafts:
- Required files considered:
- Reward-file requirement included:
- Oracle-solvable:
- Tests map to requirements:
- Anti-cheating included:
- Milestone rules followed when applicable:
- No canary strings:
- No solution leakage:
- Dependencies/base image pinning mentioned:
- Rubric note included:
- CI/LLMaJ risk considered:

IMPORTANT OUTPUT RULES:
- Be concrete and detailed enough that a task creator can build the task from the blueprint.
- Do not produce vague task names like "Data Processing Task" or "Fix the API".
- Do not repeat a category/domain/toolchain unless the user explicitly asks.
- Do not ask clarifying questions unless required inputs are completely missing; otherwise make reasonable assumptions and state them.
- If asked to create files, generate properly named .txt files with clean formatting.
- If an idea fails any requirement during your own audit, replace it before finalizing.

======================================================================
COPY-PASTE PROMPT END
======================================================================

REFERENCE REQUIREMENTS SUMMARY USED TO BUILD THIS PROMPT
Checked against current public Terminus/Harbor docs on 2026-07-14.

Key applied points:
- Required task files include instruction.md, task.toml, environment/Dockerfile or equivalent, solution/solve.sh, tests/test.sh, and tests/test_outputs.py.
- task.toml now uses version 2.0-style metadata expectations, including category/task type, subcategories, number_of_milestones, difficulty, codebase_size, languages, tags, estimates, and runtime limits.
- tests/test.sh must write a reward file under /logs/verifier/.
- Tests should verify behavior, cover all requirements, include docstrings, and avoid leaking answers.
- Dependencies and base images must be pinned.
- Instructions should be concise, realistic, unique, use absolute paths, and avoid hints/answers.
- Diversity requirements currently prefer small/large codebases, hard model difficulty on Claude Opus 5 and GPT-5.6, and milestone tasks. All nine primary categories are open.
- Milestone tasks require aligned milestone descriptions, milestone tests, milestone solutions, and sequential prerequisite stages.
- Rubrics should be aligned and include negative criteria during submission.
- Anti-cheating protections are required.

Source pages checked:
- Terminus-2.0 Task Requirements
- Terminus-2.0 Task Components
- Terminus-2.0 Submission Checklist
- Terminus-2.0 Diversity Requirements
- Terminus-2.0 Prompt Styling
- Terminus-2.0 Task Taxonomy
- Terminus-2.0 Milestones
- Harbor Task Structure and Tutorial
