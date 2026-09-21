///////////    Run only if any file changes made in step 3a //////////////////////








A task-file edit happened after Step 2b evidence, so the dirty-flag rule fired.
Do NOT run oracle 10x.
Do NOT package.
Do NOT approve.
Apply `terminus_blockers_checklist.txt` to the revised task before rerunning
mechanical evidence. Any listed blocker introduced or still present by the edit
must be fixed before Step 3b resumes.

Return to Step 2b mechanical evidence:

python3 scripts/spec_satisfiability.py specs/<task-name>.md --task-dir tasks/<task-name> --strict
python3 scripts/task_gate.py tasks/<task-name> --strict --report-dir /tmp/tb3-gates --skip-harbor
./scripts/check-task.sh --strict --report-dir /tmp/tb3-gates tasks/<task-name>
python3 scripts/harbor_gate.py tasks/<task-name> --oracle --nop

Then rerun Step 3b from sub-step 1.
Proceed to Step 4 only after Step 3b again says Ready for Step 4.