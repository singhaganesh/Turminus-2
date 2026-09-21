Step-by-Step Task Creation Flow in Cursor


Step 1 — Generate the Task
Open Cursor chat and run:

/tb3-task-author
authoring specs path: <path-to-authoring-spec>


Wait until Cursor fully finishes generating the task files before moving to the next step.


Step 2 — Run Reviewer Validation
After Step 1 completes, run this in Cursor chat:

/tb3-reviewer
reviewer specs path: <path-to-reviewer-spec>


Do not skip this step.
This is where most weak tasks get exposed:
topology collapse
instruction leakage
concentrated verifier ownership
fake multi-file complexity
shortcut repair paths
If reviewer feedback reveals structural weaknesses, fix them before packaging.


Step 3 — Package the Task
After reviewer validation is complete, run:


/tb3-packager
task path: <generated-task-folder>



This packages the finalized task into the expected deliverable structure.

Correct Execution Order
Always execute in this exact order:


/tb3-task-author
/tb3-reviewer
/tb3-packager


Do not:
package before reviewer validation
regenerate specs after packaging
skip reviewer pass because the task “looks fine”

