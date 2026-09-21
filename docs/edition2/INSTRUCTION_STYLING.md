# Instruction Prompt Styling (Edition 2)

`instruction.md` is the primary agent interface. Prompts should read like real
engineers using Cursor or Claude Code — varied voice task-to-task, not one
template.

**Philosophy:** Give the **what** (requirements), not the **how** (solution path).
Prompts must **not** be LLM-generated (avoid verbose, polite, repetitive GPT tone).

## Six principles

1. **Concise** — ~1 sentence to ~3 paragraphs; not long instruction-following drills.
2. **Well specified** — Clear goal; reject difficulty from huge unstated edge-case lists.
3. **Interesting** — Plausible real work.
4. **No answers/hints** — What, not how.
5. **Unique** — Non-trivial vs TB2, TB3, Snorkel Ed1 and vs every peer task (**≤ 15%** similarity local+platform; **> 15% blocks**). Vary voice and structure — no house template. See [TASK_UNIQUENESS.md](TASK_UNIQUENESS.md).
6. **Absolute paths** — `/app/...` only. **No canary strings** (legacy skeleton marker).

## Human vs synthetic

| | Avoid (synthetic) | Target (human) |
|---|-----------------|----------------|
| Tone | "You are an expert programmer…" | "We need to migrate the SQLite schema…" |
| Length | 500+ redundant words | ~150–200 actionable words |
| Guidance | "First run `ls`, then…" | "Source is in `/data`; write `/app/out/report.json`" |

## Anti-patterns (with why)

1. **Step-by-step + exact constants** — e.g. `SO_RCVBUF=262144` — gives the how.
2. **Detection guidance / hint sections** — leaks solution strategy.
3. **API-spec markdown walls** — reads like docs, not a user message.
4. **Prescriptive signatures/file trees** — over-specifies implementation.
5. **Bold callouts on formulas/limits** — telegraphs answer-shaped details.

## Repo overlay

This repo also enforces **hard-but-fair** disclosure: every **externally tested**
formula, schema, verifier command, and output path must appear in solver-visible
surfaces (`instruction.md` or fair environment docs) without naming the patch file
or reciting scenario→field→boolean answer tables. See `docs/HARD_BUT_FAIR_AUTHORING.md`
and `.cursor/rules/task-creation.mdc` (Instruction prose / RC6).

## Environment spec/doc files (no `spec.md` loophole)

Files under `environment/` (`spec.md`, `README.md`, `architecture.md`, API docs, etc.) are realistic engineering context — not a second instruction channel.

**Forbidden:**

- Step-by-step solution guides, walkthroughs, execution blueprints, or solver-directed hints (`HINT:`, `STEP N:`, "to solve this…", prescriptive TODOs, commented code walkthroughs, config examples that reveal the answer)
- Splitting operational contract out of `instruction.md` to dodge length limits — **all prompts and goals must remain in `instruction.md`** (accept a length WARN rather than offloading)
- LLM-style prompt extensions: hyper-structured templates that read like benchmark scaffolding, not real engineering docs

**Allowed (realistic engineering docs only):**

- What requirements, schemas, or protocols are — API contracts, DB schemas, business-logic specs
- Subsystem responsibility, observable API behavior, schema notes discoverable during diagnosis
- Comments/docstrings on code stubs the solver reads while debugging

**Aesthetic check:** specs must look like documents a standard engineering team would write, not overly polished LLM prompt extensions.

Litmus test: would a human engineer find this file plausible in production? Enforced by `scripts/run_static_checks.py --only environment_hidden_instructions` and zip bans on AI-scaffolding filenames (`CLAUDE.md`, `skills.md`, …).

## Reviewer checklist (instruction — HIGH)

When reviewing, reject if:

- Instructions are not concise (1 sentence–3 paragraphs) or read like GPT-style verbose prompts
- Goal is unclear or difficulty comes mainly from unstated edge-case laundry lists
- Task is not interesting to any developer audience
- Hints, step-by-step solve paths, or detection playbooks appear in `instruction.md`
- **Hidden hints** appear anywhere in the task environment (files, comments, READMEs, configs, scripts, TODOs)
- **Environment spec/docs** bypass instruction rules (see above)
- Not unique vs TB2/TB3/Snorkel Ed1 or vs peer tasks in this repo (**> 15% similarity** or templated find-replace shape)
- Paths are not absolute
- Legacy **canary strings** in `instruction.md` (MEDIUM)
- Task name appears in `instruction.md` (MEDIUM)
