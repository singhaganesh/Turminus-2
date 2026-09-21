# Verifier Prompt (Step 3a-V)

Run diagnostic:
  python3 verifier_health.py --task-dir tasks/<task-name> \
      --output-json /tmp/<task-name>-verifier-health.json

If report fails:
- fix randomized-order / partial-oracle / repeat-oracle issues,
- apply preservation discipline for any edits,
- rerun Step 2b mechanical gates (static -> collapse -> 1x oracle + nop),
- rerun verifier_health.py.

Interpret failures explicitly:
- randomized_order FAIL -> remove order/shared-state dependency.
- partial_oracle FAIL -> strengthen discriminator behavior in tests.
- repeat_oracle FAIL -> fix oracle nondeterminism.

Pass artifact to Step 4:
  --verifier-health /tmp/<task-name>-verifier-health.json

Constraints:
- do not claim command passed unless run,
- show exact harbor command output,
- do not run verifier_health.py concurrently with other harbor runs on same task.

Report:
- verifier health decision
- blocking failure type(s)
- edited files (if any)
- post-edit mechanical gate results

Task path: tasks/<task-name>