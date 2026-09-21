# Author pre-ship probes (all tasks)

Run these on **every** new or revised task before `package_task.py --validate`.
Checker scores the **zip**, not the working tree.

Full probe definitions: `prompts/TASK_CHECKER.md` (R1–R9). Recurring ship-killers:
`.cursor/rules/checker-lessons.mdc` (mirrored in `.claude/rules/`).

## Design-time trap inventory (spec / Step 2a)

Before writing `tests/`, list cheats that must **not** pass:

| Cheat | Block with |
|-------|------------|
| Run pipeline / CLI twice in wrapper | Single-subprocess counter, held-out inputs at grade time, rubric −5 |
| Hand-write graded artifacts | Tests rerun real binary/tool; no static golden as producer |
| Source-only fix, skip rebuild | R5: patch sources, skip `make`/`cargo build`/equivalent → reward 0 |
| Env notes teach workaround | Handbook describes symptom only, not passing bypass |
| Empty / `# BUG` defect | Plausible wrong logic that still looks schema-valid |

## Runtime probe table

| Probe | Command / check | Pass |
|-------|-----------------|------|
| R1 | `docker build --network=none` from zip `environment/` | Image builds |
| R3 | Unmodified tree + `tests/test.sh` | reward 0; **all** graded tests fail |
| R4 | `solution/solve.sh` + `tests/test.sh` | reward 1 |
| R5 | Apply oracle source edits; skip rebuild step (`preship/source_only.sh`) | reward 0 |
| R6 | Apply rubric negative decoy fix (`preship/decoy_fix.sh`) | reward 0 |
| R7 | Wrapper / hand-written outputs only (`preship/shortcut_fix.sh`) | reward 0 |
| ALT | Different-but-correct solution (`preship/alt_solution.sh`) | reward 1 (else false-failure trap) |
| R8 run1/run2 | `tests/test.sh` twice (separate runs) | Same reward |
| **R8 twice** | `bash solve.sh && bash solve.sh` | Both exit 0; no `*.rej` |
| R9 | Clean rebuild + R4 | reward 1 |

Automated R8 twice (when Docker available):

```bash
python3 scripts/oracle_idempotency_probe.py tasks/<task> --strict
```

Wired into `./scripts/check-task.sh --strict` as Phase C2.

## Automated R5 / R6 / R7 (`preship/` manifest)

Declare the three anti-cheat fixes in `tasks/<task>/preship/` — a task-root dir
the packager **excludes** from the zip (`should_package` drops any non-submission
root). Nothing here ships.

```
preship/preship.json      manifest
preship/source_only.sh    R5: apply the source edit, skip the rebuild/regen lever
preship/decoy_fix.sh      R6: the wrong fix the rubric's negative criterion punishes
preship/shortcut_fix.sh   R7: hardcode fixtures / stuff outputs / edit data tests read
```

```json
{
  "lever": "one line: the rebuild/regen step R5 must skip",
  "probes": {
    "R5": {"script": "source_only.sh", "expect_reward": 0},
    "R6": {"script": "decoy_fix.sh",  "expect_reward": 0, "rubric_negative": "Agent … , -N"},
    "R7": {"script": "shortcut_fix.sh", "expect_reward": 0},
    "ALT": {"script": "alt_solution.sh", "expect_reward": 1}
  }
}
```

**ALT (no-false-failure guard).** `preship/alt_solution.sh` is a deliberately
different but correct solution (different approach / valid output form). It must
score reward **1** — if it scores 0 the suite rejects a valid solution, i.e. a
false-failure trap: a test is stricter than the instruction. Fix the test to
grade the invariant, or state the exact-form requirement in `instruction.md`.
Also run `python3 scripts/false_failure_lint.py tasks/<task> --strict` (Phase B),
which flags over-strict / oracle-identity assertions unless the instruction
legitimately demands an exact form.

Each script runs inside the built image (edits `/app`), then `tests/test.sh`
runs; observed reward must equal `expect_reward` (always `0` — none is a real
fix). Run it:

```bash
python3 scripts/preship_probes.py tasks/<task> --strict
```

Wired into `./scripts/check-task.sh --strict` as **Phase C3**. Missing manifest
is a FAIL under `--strict`; docker-unavailable is a SKIP.

## Automated DIFFICULTY-FLOOR + caveat classes + native-binary

```bash
python3 scripts/difficulty_floor_check.py tasks/<task> --strict   # BLOCKER if <2 classes
python3 scripts/caveat_audit_check.py tasks/<task>                # advisory: lists graded classes + leg-1 hint
python3 scripts/native_binary_check.py tasks/<task> --strict      # BLOCKER GAMEABLE-NATIVE if native required but no ELF assert in tests
```

All wired into `./scripts/check-task.sh` Phase B. The floor and native-binary
gate block under `--strict`; the caveat audit is advisory (confirm the three
legs by hand/LLM).

**Native-binary rule (both directions):** if `instruction.md` requires a native
binary, the graded suite must assert ELF magic (`\x7fELF`) on the agent binary
**after rebuild** — an ELF check only in `solve.sh` does not count, and a
Python/shell mill emitting correct output otherwise scores R7=1. If the task is
native, `preship/shortcut_fix.sh` (R7) must include the "replace the binary with
a script that emits correct output" cheat. If the instruction does NOT require
native, do not add an ELF assert.

## `solution/solve.sh` idempotency

**Required:** safe to run twice with `set -euo pipefail`.

**Bad** — second run fails:

```bash
patch -p0 -i fix.patch
```

**Good** — dry-run guard:

```bash
apply_patch() {
  local patch_file="$1"
  if patch -p0 --dry-run -s -f -i "$patch_file" >/dev/null 2>&1; then
    patch -p0 -i "$patch_file"
  fi
}
```

Also acceptable: `patch -p0 --forward -N` **plus** `rm -f …/*.rej`, or `cp` canonical fixed files (watch collapse RC7/GX4).

## Instruction / verifier alignment

- ≤ ~3 short paragraphs; absolute paths; no mechanism spoilers
- Every graded test claim stated in `instruction.md`
- Every instruction requirement has ≥1 test
- Name verifier behavior: “verifier reruns …” (actionability gate)
- `find tasks/<task> -type f -size +1M` empty (`OVERSIZE`)

## Gate sequence (do not skip)

```bash
python3 scripts/lint_spec.py specs/<task>.md --strict
python3 scripts/spec_satisfiability.py specs/<task>.md --task-dir tasks/<task> --strict
python3 scripts/difficulty_floor_check.py tasks/<task> --strict   # ≥2 capability classes
python3 scripts/caveat_audit_check.py tasks/<task>                # advisory class + leg-1 map
./scripts/check-task.sh --strict --report-dir /tmp/tb3-gates tasks/<task>  # includes Phase C3 (R5/R6/R7)
python3 scripts/harbor_gate.py tasks/<task> --oracle --nop
python3 scripts/harbor_gate.py tasks/<task> --oracle-repeat 10
python3 scripts/package_task.py tasks/<task> --out Task_Ready_To_Submit/<task>.zip --validate
python3 scripts/approve_task.py --strict ...
```

After any edit: re-run `check-task.sh` (checksum stale otherwise).
