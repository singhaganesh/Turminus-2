### Decision
GO — Attempt 1. Debugging repair: nightly assay clones a plaster vat that never received the latest ledger impress; bench vat is current and the error reads as a test-schema miss.

### Metadata
- version: 2
- Task name: trykiln-plaster
- Title: Template vat still cloned
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["go"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["migrations", "clone", "schema", "kiln"]
- Milestones: 0

## Authoring Brief

### Triviality Ledger
- Impressing only `/app/hearth/bench.vat` leaves plaster and worker behind.
- `scorepit/shim.go` PadSlot adds `attempt_slot` on the worker without recording the migration stem.
- Hand-editing worker.vat without shipping a new `/app/bin/kilncli` fails stale-spill and recovery spill.
- Trusting assay `schema_version=` printed from the worker without comparing inkstack heads.

### Per-gate Pitfall Inventory
- RC2: BAY_NOTES lists module dirs, not FocusPath / copy-without-head.
- GX9: grade vat columns and printed schema_version, not boolean keys.
- R5: tests do not `go build` / make; agent must ship then impress plaster and spill.
- R3: every graded test fails on the broken tree.
- P4: PadSlot decoy punished by applied-stem and mold-column tests.

### Initial Draft Commitments
- environment/kilncli/impress/apply.go — impress always uses hearth/focus.txt
- environment/claybin/spill.go — copy plaster to worker with no head compare
- environment/scorepit/score.go — print worker applied stem; require column only
- environment/scorepit/shim.go — unused PadSlot decoy
- environment/claybin/emit.go — fill worker from baked vat
- environment/claybin/plaster.vat — applied through 0003 only
- environment/scorepit/shim.go — unused PadSlot decoy
- environment/claybin/plaster.vat — applied through 0003 only
- environment/hearth/bench.vat — applied through 0004
- tests/test_outputs.py — vat schema, stale spill, holdout head, recovery spill

### Public contract
- `/app/bin/kilncli assay` on `/app/vats/worker.vat` must not unknown-column `attempt_slot`.
- `schema_version=<id>` equals lexicographic latest `*.sql` stem under `/app/inkstack/migrations/`.
- `attempt_slot` on `tries` in `/app/vats/plaster.vat` and `/app/vats/worker.vat`.
- `/app/vats/assay.ok` is written only when that printed id equals that stem.
- Spill of a vat behind that head exits non-zero and does not write `/app/vats/assay.ok`.
- Hand-written vats insufficient; grading invokes assay only.

### platform_files
- path: task.toml
  role: metadata; allow_internet false
- path: instruction.md
  role: public prompt
- path: output_contract.toml
  role: local contract
- path: tests/test.sh
  role: verifier entry
- path: tests/test_outputs.py
  role: behavioral tests
- path: solution/solve.sh
  role: oracle
- path: environment/Dockerfile
  role: golang+python offline image
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/kilncli/impress/apply.go
  role: impress target selection
- path: environment/claybin/emit.go
  role: worker fill
- path: environment/scorepit/score.go
  role: worker score
- path: environment/scorepit/shim.go
  role: decoy column pad
- path: environment/inkstack/migrations
  role: sql ledger
- path: environment/baydocs/BAY_NOTES.txt
  role: operator layout

### fix_frontier
- count: 3
- distribution: kilncli/impress, claybin, scorepit
- naming_policy: opaque kiln helpers
- forbidden_stems: template, clone, migrate, stale
- helpers_policy: vat parser co-resident; shim is decoy
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: vat parse, subprocess returncode, stdout schema_version
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: PadSlot on worker or impress bench only

### category_profile
- challenge_family: stale_clone_schema
- profile_name: migration_template_clone
- allowed_instruction_disclosures: commands, vat paths, column name, schema_version rule, spill lag exit
- forbidden_instruction_leaks: focus.txt redirect, PadSlot, copy-without-head
- category_specific_hardness_bar: bench vat green, assay unknown-column
- category_specific_verifier_risks: scenery tests on bench.vat
- coverage_role: debugging C2 rebuild-before-claim

### satisfiability_risk
- rc2_planned_name_risk: medium BAY_NOTES module list
- gx9_contract_risk: low public stems
- cr1_symbol_frontier_risk: low three roots
- hidden_contract_risk: low named assay/spill

### actionability_plan
- verifier_command_visible: kilncli assay
- source_fix_intent_visible: kiln sources under /app from BAY_NOTES
- generated_output_rule_visible: assay.ok and vats after spill
- exact_formula_home: schema_version equals latest sql stem
- schema_home: instruction.md vat paths and column

### waiver_plan
- waivers_expected: false
- waiver_rationale: none

### reference_pattern
- justification_if_none: no promoted reference for plaster-vat clone lagging ledger impress

### realism_source
- source_type: synthetic_exception
- evidence_basis: pytest-xdist / django template database cloned before migrate
- upstream_or_synthetic_rationale: cannot ship a full postgres cluster; file vat preserves clone-vs-migrate causality
- minimization_preserves: current bench, stale template clone, ledger version printed from clone
- synthetic_exception_review: focus-file redirect is a plausible workspace default

### difficulty_mechanism_plan
- mechanisms: deceptive_but_valid_local_evidence, false_green_intermediate_states, stateful_multi_step_dependencies, cross_file_cross_format_invariants
- adversarial_layers_count: 4
- fairness_guardrails: all local deterministic
- mechanism: deceptive_but_valid_local_evidence
  placement: bench.vat already has attempt_slot
  why_model_misses_it: agents impress bench and stop
  fairness_guardrail: instruction names worker unknown-column
- mechanism: false_green_intermediate_states
  placement: assay prints a schema_version from the worker even when head differs
  why_model_misses_it: version line looks healthy
  fairness_guardrail: id must equal latest sql stem
- mechanism: stateful_multi_step_dependencies
  placement: source fix then ship then impress plaster then spill
  why_model_misses_it: source-only or vat-edit-only
  fairness_guardrail: grading invokes assay without rebuild
- mechanism: cross_file_cross_format_invariants
  placement: sql stems vs applied: lines vs columns
  why_model_misses_it: PadSlot column without applied stem
  fairness_guardrail: applied list must contain head

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert compares plaster applied vs inkstack head then spills
- shortcut_audit: PadSlot, hand vat, impress bench only, skip ship
- ablation_plan: revert each of three loci
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Opus 5 / GPT-5.6

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: all tests pass

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: vats and sql bundled locally

### Failure topology
Assay unknown-column on attempt_slot while bench impress already has the column because spill copies plaster never impressed with 0004, impress ignores argv in favor of focus.txt, and assay trusts the worker applied stem.

### Environment shape
Go kilncli plus claybin spill, scorepit assay, inkstack sql, file vats, golang bookworm plus python verifier.

### Test plan
- test_k01_mold_column
- test_k02_worker_column
- test_k03_applied_head
- test_k04_column_parity
- test_k05_lag_copy_exit
- test_k06_lag_copy_untouched
- test_k07_holdout_sql_head
- test_k08_zz_recover_worker
- test_k09_ok_marker
- test_k10_version_print
- test_k11_version_matches_head
- test_k12_second_run
- test_k13_clean_exit
