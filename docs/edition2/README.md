# Terminus Edition 2 — Platform Reference

Canonical Snorkel/Harbor **platform** requirements for task submissions. This
repo adds **local** gates on top (`commands.md`, `scripts/check-task.sh`,
`scripts/approve_task.py`, collapse checks, hard-but-fair lints).

When platform docs and repo tooling disagree, follow **repo commands and
`.cursor/rules/`** for day-to-day authoring; use this folder to understand what
reviewers and `harbor tasks check` expect on upload.

## Documents

| Doc | Contents |
|-----|----------|
| [TASK_REQUIREMENTS.md](TASK_REQUIREMENTS.md) | Structure, instruction, solution, tests, difficulty, anti-cheating, rubric, automated checks |
| [HARBOR_COMPONENTS.md](HARBOR_COMPONENTS.md) | Components, Docker environment setup, oracle, verifier, runtime paths |
| [QUALITY_GUIDELINES.md](QUALITY_GUIDELINES.md) | Quality bar, oracle/NOP/agents, rubric, banned scenarios |
| [INSTRUCTION_STYLING.md](INSTRUCTION_STYLING.md) | Human prompt voice, six principles, spec-doc loophole, reviewer criteria |
| [CI_CHECKS.md](CI_CHECKS.md) | Blocking/warning CI checks, LLMaJ, iteration workflow |
| [DOCKERFILE_BEST_PRACTICES.md](DOCKERFILE_BEST_PRACTICES.md) | Canonical TB base images (§2), justification rules, Dockerfile policy |
| [TASK_UNIQUENESS.md](TASK_UNIQUENESS.md) | Anti-templating, 15% max similarity (local+platform), `prompts/oneshot_unique_task.md` + `scripts/uniqueness_probe.py` |
| [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) | Pre-submit verification, Harbor commands, LLMaJ, agent runs |

## Repo workflow (not duplicated here)

- Step prompts: `prompts/Step1.md` … `prompts/Step5.md`
- Process: `workflow-prompts.md`
- Commands: `commands.md`
- Construction: `.cursor/rules/task-creation.mdc`
- Review: `.cursor/rules/review-and-submit.mdc`
- Policy: `docs/HARD_BUT_FAIR_AUTHORING.md`

## Quick platform commands

```bash
# Oracle sanity (matches upload expectations)
harbor run -a oracle -p <task-folder>

# Static / LLMaJ-style checks (CI model)
harbor tasks check <task-folder> -m openai/@openai/gpt-5.6

# Frontier agent trial (difficulty calibration — Opus 5 + GPT-5.6)
harbor run -a terminus-2 -m openai/@openai/gpt-5.6 -p <task-folder>
harbor run -a terminus-2 -m anthropic/@anthropic/claude-opus-5 -p <task-folder>
```

Local equivalents: `scripts/harbor_gate.py`, `scripts/run_static_checks.py`,
`scripts/approve_task.py --strict`.
