### Decision
GO — Attempt 1. Debugging repair of a C forgekit that lags one mill behind; three cooperating loci; held-out descriptions; rebuild lever on `/app/bin/rivetbay`.

### Metadata
- version: 2
- Task name: sheetlag-rivet
- Title: Mill one run behind
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "decoders", "mill", "event-descriptions"]
- Milestones: 0

## Authoring Brief

### Triviality Ledger
- Double mill in a wrapper hides lag for files already on disk at solve time unless grading counts mill subprocesses; a per-subprocess `.mill_pass` counter blocks that cheat. Held-out descriptions added at grade time still fail unless one mill consumes this run's intake.
- Hand-written `.kdec` files fail when the mill is the graded producer.
- Source-only edits leave the prebuilt `/app/bin/rivetbay` lagging.

### Per-gate Pitfall Inventory
- RC2: keep forgekit filenames off instruction nouns (`hangar`, `packed`, `vendor`).
- GX9: grade artifacts and decode JSON, not boolean answer keys.
- CR1: oracle symbols `grab_sheet`, `pour_sheet`, `count_gap` stay off CLI nouns in the same patch-verb sentence.
- R5: tests never rebuild; they invoke the binary.
- R3: every graded test fails on the shipped tree.

### Initial Draft Commitments
- environment/rivetbay/forgekit/snapshot.c — intake sheet captured too early
- environment/rivetbay/forgekit/emit.c — emitters follow the captured sheet
- environment/millscore/tally.c — exit status uses the captured sheet
- environment/rivetbay/forgekit/warmup.c — plausible double-mill decoy
- tests/test_outputs.py — one mill, held-out pair, decode fields, short-set exit

### Public contract
- `/app/bin/rivetbay mill` once must refresh `/app/rivetbay/intake/current.ledger` and emit one `/app/rivetbay/emitters/<name>.kdec` per `/app/rivetbay/evd/*.evd` present on that run.
- Decoder set smaller than description set → mill exit non-zero.
- `/app/bin/rivetbay decode <frame>` JSON: decoded with integer fields, or unknown when no decoder.
- Schemas as in instruction.md. Static copies of ledgers or kdec files are not enough.

### platform_files
- path: task.toml
  role: metadata; must set `[environment] allow_internet = false`
- path: instruction.md
  role: natural public task prompt
- path: output_contract.toml
  role: local output declaration
- path: tests/test.sh
  role: verifier entrypoint
- path: tests/test_outputs.py
  role: domain verifier
- path: solution/solve.sh
  role: oracle
- path: environment/Dockerfile
  role: build definition
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/rivetbay/forgekit/driver.c
  role: CLI entry
- path: environment/rivetbay/forgekit/snapshot.c
  role: intake sheet
- path: environment/rivetbay/forgekit/discover.c
  role: description scan
- path: environment/rivetbay/forgekit/emit.c
  role: decoder emit
- path: environment/millscore/tally.c
  role: exit status
- path: environment/rivetbay/forgekit/warmup.c
  role: decoy double mill
- path: environment/rivetbay/notes/forms.txt
  role: format notes

### fix_frontier
- count: 3
- distribution: snapshot, emit, tally
- naming_policy: opaque forgekit symbols
- forbidden_stems: hangar, packed, vendor
- helpers_policy: warmup and utf_tidy rhyme with ops folklore, not the fix
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: artifacts, decode JSON, process exit
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: double mill or one-file constructor tweak without tally

### category_profile
- challenge_family: pipeline ordering
- profile_name: filesystem_state_reconstruction
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: constructor, import-time read, patch files
- category_specific_hardness_bar: one invocation vs expected unknown handling
- category_specific_verifier_risks: NOP mill already green on old events
- coverage_role: debugging rebuild-before-claim

### satisfiability_risk
- rc2_planned_name_risk: low opaque symbols
- gx9_contract_risk: low artifact/json
- cr1_symbol_frontier_risk: low thin oracle
- hidden_contract_risk: low public schemas

### actionability_plan
- verifier_command_visible: mill and decode named
- source_fix_intent_visible: forgekit under /app/rivetbay
- generated_output_rule_visible: ledger and kdec rules public
- exact_formula_home: instruction field packing
- schema_home: instruction.md

### waiver_plan
- waivers_expected: false
- waiver_rationale: no waiver expected

### reference_pattern
- justification_if_none: no promoted reference matches constructor-vs-discover mill ordering

### realism_source
- source_type: synthetic_exception
- evidence_basis: common generator/import-order lag in mill pipelines
- upstream_or_synthetic_rationale: no public repo can be shipped; behavior is a standard forgekit mistake
- minimization_preserves: discover then emit in one process, unknown as normal vendor handling
- synthetic_exception_review: extra review that the constructor looks like a cache, not sabotage

### difficulty_mechanism_plan
- mechanisms: buried_local_constraints, stateful_multi_step_dependencies, deceptive_but_valid_local_evidence, false_green_intermediate_states, cross_file_cross_format_invariants
- adversarial_layers_count: 4
- fairness_guardrails: all local and deterministic
- mechanism: buried_local_constraints
  placement: intake sheet captured before discover writes
  why_model_misses_it: looks like a normal cache
  fairness_guardrail: sources are local
- mechanism: stateful_multi_step_dependencies
  placement: discover, emit, tally share the sheet
  why_model_misses_it: one-module patch leaves exit or emitters wrong
  fairness_guardrail: artifacts inspectable
- mechanism: deceptive_but_valid_local_evidence
  placement: unknown decode and warmup double mill
  why_model_misses_it: second mill looks like warmup
  fairness_guardrail: instruction requires one mill
- mechanism: false_green_intermediate_states
  placement: old events still decode
  why_model_misses_it: agents stop after existing samples work
  fairness_guardrail: new description contract is public
- mechanism: cross_file_cross_format_invariants
  placement: evd, ledger, kdec, decode JSON
  why_model_misses_it: editing one format leaves others stale
  fairness_guardrail: schemas public

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert traces mill once vs twice
- shortcut_audit: double mill, hardcoded kdec, source-only
- ablation_plan: drop tally or emit and expect residual fail
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Opus 5 / GPT-5.6

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.json+reward.txt
- binary_threshold_rule: reward.txt is 1 only when every required metric is complete

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: all evd and frames bundled in the image
