### Decision
GO — Debugging repair of C stackfold symmap generated from object files before the linked runtime; Makefile dependency + post-ship gate; held-out render PCs; rebuild lever on `make -C /app/symmill ship`.

### Metadata
- version: 2
- Task name: stackfold-prelude
- Title: Map generated before the link
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "profiler", "symmap", "makefile", "stackfold"]
- Milestones: 0

## Authoring Brief

### Triviality Ledger
- Serial `make` ordering without symmap input on linked ELF still leaves object-merge maps; gate + check enforce linked buildid.
- Hand-written symmap/profile fail render name checks and buildid parity.
- Source-only Makefile tweak without `ship` leaves stale symmap/profile.

### Per-gate Pitfall Inventory
- RC2: repair paths in benchhart layout only.
- GX9: grade symmap mode/buildid and profile symbol names, not boolean keys.
- CR1: oracle patches Makefile + gate hook, not instruction nouns.
- R5: tests never call `make ship`.
- R3: all 11 graded tests fail on shipped tree.

### Initial Draft Commitments
- environment/symmill/Makefile — symmap depends on objects + object index mode
- environment/symmill/hooks/gate.sh — no-op post-ship validation decoy
- tests/test_outputs.py — symmap parity, held-out render, profile names

### Public contract
- `make -C /app/symmill ship` rebuilds runtime, symmap from linked ELF, profile.json; exits 0 only when map matches link identity and covers all text symbols.
- `/app/bin/stackfold render` writes JSON samples with `symbol` and `offset`.
- Object-merge or stale symmaps must fail `stackfold check` and block a correct ship.

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
  role: behavioral verifier
- path: solution/solve.sh
  role: oracle
- path: environment/Dockerfile
  role: image build
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/symmill/Makefile
  role: build orchestration defect
- path: environment/symmill/hooks/gate.sh
  role: post-ship validation hook
- path: environment/symmill/stampdeck/repair.list
  role: repair path map

### fix_frontier
- count: 2
- distribution: linkyard Makefile, gate hook
- naming_policy: neutral bench paths
- forbidden_stems: symmap, prelude, object
- helpers_policy: stackfold check behavior documented in wire.txt
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: symmap headers, nm parity, render JSON symbols
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis + rebuild + parallel build trap
- collapse_risk: ordering-only Makefile decoy

### category_profile
- challenge_family: stale_generated_artifacts
- profile_name: symmap_link_race
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: Makefile line hints, object-merge mode name as fix recipe
- category_specific_hardness_bar: rebuild ship before grade
- category_specific_verifier_risks: high resolve rate masks one new symbol
- coverage_role: debugging rebuild-before-claim

### satisfiability_risk
- rc2_planned_name_risk: low
- gx9_contract_risk: low
- cr1_symbol_frontier_risk: low
- hidden_contract_risk: low

### actionability_plan
- verifier_command_visible: stackfold render + ship named
- source_fix_intent_visible: layout.txt module list
- generated_output_rule_visible: symmap + profile rules public
- exact_formula_home: instruction.md
- schema_home: instruction.md

### waiver_plan
- waivers_expected: false
- waiver_rationale: no waiver expected

### reference_pattern
- justification_if_none: no promoted reference for symmap-before-link parallel build race

### realism_source
- source_type: synthetic_exception
- evidence_basis: parallel Make symmap/link ordering bugs in native profiler pipelines
- upstream_or_synthetic_rationale: behavior mirrors real build-graph mistakes; no upstream repo shipped
- minimization_preserves: linked-ELF symmap contract and render JSON shape
- synthetic_exception_review: Makefile defect looks like normal dependency oversight, not sabotage

### difficulty_mechanism_plan
- mechanisms: buried_local_constraints, stateful_multi_step_dependencies, deceptive_but_valid_local_evidence, false_green_intermediate_states, cross_file_cross_format_invariants
- adversarial_layers_count: 4
- fairness_guardrails: all local and deterministic
- mechanism: buried_local_constraints
  placement: symmap rule depends on objects not linked runtime
  why_model_misses_it: high resolve rate on legacy symbols
  fairness_guardrail: public ship contract names linked ELF
- mechanism: stateful_multi_step_dependencies
  placement: runtime, symmap, profile, gate hook
  why_model_misses_it: patching Makefile without ship leaves stale artifacts
  fairness_guardrail: tests grade on-disk outputs only
- mechanism: deceptive_but_valid_local_evidence
  placement: gate.sh exits 0 without checking
  why_model_misses_it: serial make appears to fix ordering
  fairness_guardrail: rubric punishes serial-only ordering decoy
- mechanism: false_green_intermediate_states
  placement: most samples still resolve to plausible names
  why_model_misses_it: agents stop after partial resolution
  fairness_guardrail: ring_dispatch name contract is public
- mechanism: cross_file_cross_format_invariants
  placement: Makefile, symmap header, profile JSON
  why_model_misses_it: hand-edited symmap passes smoke render
  fairness_guardrail: buildid + mode checks public

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert rebuilds ship and checks ring_dispatch by name
- shortcut_audit: hand-written symmap, serial ordering only, render hardcode
- ablation_plan: revert Makefile dep or gate hook and expect reward 0
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Opus 5 / GPT-5.6

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: reward.txt is 1 only when every pytest passes

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: samples and runtime bundled offline
