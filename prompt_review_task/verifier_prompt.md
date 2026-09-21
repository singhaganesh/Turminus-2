You are validating verifier integrity for:

```bash id="m2k9xp"
tasks/<task-name>
```

Read `docs/edition2/QUALITY_GUIDELINES.md`, `docs/edition2/HARBOR_COMPONENTS.md`,
and `docs/edition2/CI_CHECKS.md` (test.sh reward footer is the canonical script
end on standard tasks — Harbor scores reward.txt, not exit code; do not add trailing
`exit`; digest-pinned `FROM`; no runtime verifier installs).

Step 1 — Run verifier diagnostics

```bash id="f4u8cw"
python3 scripts/verifier_health.py \
  --task-dir tasks/<task-name> \
  --output-json /tmp/<task-name>-verifier-health.json
```

Hard rules:

* NEVER claim a command passed unless it was actually executed
* ALWAYS show exact harbor command output
* NEVER run `verifier_health.py` concurrently with other harbor runs on the same task

Failure handling:
If the verifier-health report fails, repair ONLY the failing verifier-health axes.

Failure interpretation rules:

* `randomized_order FAIL`

  * remove order dependency
  * remove hidden shared-state coupling
  * ensure tests are execution-order independent

* `partial_oracle FAIL`

  * strengthen discriminator logic
  * improve negative-case detection
  * prevent weak-oracle acceptance paths

* `repeat_oracle FAIL`

  * eliminate oracle nondeterminism
  * stabilize flaky behavior
  * remove randomness/time/env dependency from oracle path

Preservation discipline for ALL edits:

1. Identify at-risk gates before modifying files
2. Limit edits strictly to verifier-health failures
3. Avoid unrelated cleanup/refactors
4. Run collapse checks after edits
5. Re-run Step 2b mechanical gates in this exact order:

   * `python3 scripts/task_gate.py tasks/<task-name> --strict --report-dir /tmp/tb3-gates --skip-harbor`
   * `./scripts/check-task.sh --strict --report-dir /tmp/tb3-gates tasks/<task-name>`
   * `python3 scripts/collapse_check.py tasks/<task-name>`
   * `python3 scripts/harbor_gate.py tasks/<task-name> --oracle --nop`
6. Re-run:

```bash id="n7q3va"
python3 scripts/verifier_health.py \
  --task-dir tasks/<task-name> \
  --output-json /tmp/<task-name>-verifier-health.json
```

Artifact for Step 4:

```bash id="r1h6tb"
--verifier-health /tmp/<task-name>-verifier-health.json
```

Final report MUST include:

* verifier-health decision
* blocking failure type(s)
* exact verifier-health outcomes
* edited files (if any)
* preservation checks performed
* post-edit mechanical gate results
* confirmation that no out-of-scope edits were made


TASK PATH : tasks/<task-name>
