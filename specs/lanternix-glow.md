### Decision
GO — Attempt 1. Debugging repair: generated Go packs sit on disk while the dispatch chart is sealed before every pack is filled, so a new recipe decodes as void. Agent must mill after source repair.

### Metadata
- version: 2
- Task name: lanternix-glow
- Title: Sealed chart misses packs
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["go"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["lanternix", "milldesk", "packbay", "wick"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/lanternix cast` refreshes generated packs from `/app/cardwell`.
- `/app/bin/lanternix readout --lamp FILE` writes `/app/glowbank/readout.json`.
- Any recipe lamp whose card the mill carries must decode; slots are lamp file values keyed by card slot names.
- Missing mill coverage for a recipe card → readout exit non-zero; no success readout rewrite.
- Unknown lamp code → `code` `void`, non-zero exit.
- Verifier reruns readout only.
- Unmodified image: `cast` exits 0, flash readout exits 2 and does not write readout.json.
- `/app/bin/lanternix` is native ELF; `/app/packbay/reg.go` imports every packbay unit dir.

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
  role: Go+python offline image
- path: construction_manifest.json
  role: local authoring artifact

### task_files

- path: environment/oxbind/seal.go
  role: chart seal
- path: environment/packbay/fetch.go
  role: pack fill gate
- path: environment/milldesk/spin.go
  role: mill writer

### fix_frontier

- count: 3
- distribution: oxbind, packbay, milldesk
- naming_policy: opaque Clip/Pull/Spin
- forbidden_stems: lanternix, readout, slots, void
- helpers_policy: milldesk main.go and play.go co-resident CLI; packbay/reg.go generated Fill helper; Warm decoy
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON artifacts, exit codes, recomputed card ids
- forbidden_assertion_styles: boolean answer keys

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: blank-import only the named flash pack

### category_profile

- challenge_family: codegen_registry_staleness
- bug_family: codegen_registry_staleness
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, JSON keys, flash symptom, void fallback
- forbidden_instruction_leaks: init snapshot, seed gate, Fill generation
- category_specific_hardness_bar: mill green while new pack still void
- category_specific_verifier_risks: test-side mill, hand-written readout
- coverage_role: debugging C2 rebuild-before-claim

### difficulty_mechanism_plan

- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: cast exits 0 with pack files present
  why_model_misses_it: agents trust mill success
  fairness_guardrail: instruction names cast rc 0, flash readout rc 2, missing readout.json
- mechanism: deceptive_but_valid_local_evidence
  placement: seed list blank-loads only named packs
  why_model_misses_it: that one lamp then works
  fairness_guardrail: every recipe lamp must decode
- mechanism: cross_file_cross_format_invariants
  placement: cards vs mill Read vs readout slots
  why_model_misses_it: edits JSON only
  fairness_guardrail: verifier reruns readout
- mechanism: stateful_multi_step_dependencies
  placement: source fix then agent mill/rebuild
  why_model_misses_it: skip mill
  fairness_guardrail: instruction requires mill after sources

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert fills all packs then mill
- shortcut_audit: seed-only flash, hand JSON, skip mill
- ablation_plan: revert each locus
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
- sidecar_or_protocol_notes: cards and lamps bundled

### satisfiability_risk

- rc2_planned_name_risk: low — fix dirs are oxbind/packbay/milldesk
- gx9_contract_risk: low JSON objects
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan

- verifier_command_visible: lanternix cast/readout
- source_fix_intent_visible: pipeline modules in ROUTE.txt
- generated_output_rule_visible: readout.json
- exact_formula_home: codes equal card ids
- schema_home: instruction.md and GRAMMAR.txt

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- justification_if_none: no promoted reference for Go generated-pack fill versus sealed dispatch chart

### realism_source

- source_type: synthetic_exception
- evidence_basis: protobuf/descriptor registry snapshot before lazy generated imports
- upstream_or_synthetic_rationale: cannot ship a private protobuf compiler tree
- minimization_preserves: mill green, pack present, decode void, skip rebuild
- synthetic_exception_review: oneshot import is a realistic decoy

### Failure topology
Operators see mill succeed and a generated pack for the new recipe on disk while readout still reports void. The chart is sealed before packs are filled, fill is gated to a stale seed, and mill rewrites an incomplete Fill list. Hold-out recipes stay void if only the named pack is wired.

### Environment shape
Go mill desk, pack crib, chart sealer, recipe cards, lamp takes, opsheets, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, Go modules, mill rebuild.

### Test plan
- test_lx00_native_mill
- test_lx01_id_parity
- test_lx02_anchor_pair
- test_lx03_held_pair
- test_lx04_prior_pair
- test_lx05_alien_exit
- test_lx06_gap_abort
- test_lx07_json_shape
- test_lx08_slot_width
- test_lx09_cross_bind
- test_lx10_held_second
- test_lx11_twice_stable
- test_lx_zz_corrupt_recover

### Drafting guardrails
Do not name snapshot, seed, or Fill. Tests must not mill except recovery. Punish flash-only seed via hold-out plus rubric.

### Triviality Ledger

- Blank-import only LAN_FLASH_9C — blocked by held recipe still missing from codes and slots.
- Hand-written readout — blocked by readout rerun and corrupt-then-mill recovery.
- Source-only without mill — binary still sealed; R5 source_only.sh.
- Naive patch -i oracle — blocked by full-file writes in solve.sh.

### Per-gate Pitfall Inventory

- RC2: repair paths in ROUTE.txt name directories, not Clip/Pull/Spin.
- GX9: grade JSON codes/slots, not boolean flags.
- CR8: main dispatches; mill vs readout split.
- R5: tests do not mill except zz recovery.
- R3: every graded test fails on broken tree.
- P4: seed decoy punished by rubric.

### Initial Draft Commitments

- environment/oxbind/seal.go
- environment/packbay/fetch.go
- environment/packbay/bag.go
- environment/packbay/reg.go
- environment/packbay/reg.go
- environment/packbay/packs/warm01/pack.go
- environment/packbay/packs/beam44/pack.go
- environment/packbay/packs/flash9c/pack.go
- environment/packbay/packs/glow2b/pack.go
- environment/milldesk/main.go
- environment/milldesk/spin.go
- environment/milldesk/play.go
- environment/milldesk/Makefile
- environment/cardwell/*.card
- environment/lamps/*.lamp
- environment/notes/ROUTE.txt
- environment/notes/GRAMMAR.txt
- environment/go.mod
- environment/Dockerfile
- tests/test_outputs.py
- tests/test.sh
- solution/solve.sh
- task.toml
- instruction.md
- output_contract.toml
- construction_manifest.json
- rubric.txt
- preship/preship.json
- preship/source_only.sh
- preship/decoy_fix.sh
- preship/shortcut_fix.sh

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

- path: environment/oxbind/seal.go
  symbol: Clip
  kind: function
  signature: Clip(bag map[string]Spec) map[string]Spec
  purpose: copies the current pack bag into a chart
- path: environment/packbay/fetch.go
  symbol: Pull
  kind: function
  signature: Pull(tag string)
  purpose: fills packs for a requested tag
- path: environment/packbay/reg.go
  symbol: Fill
  kind: function
  signature: Fill()
  purpose: loads generated units into the bag
- path: environment/milldesk/spin.go
  symbol: Spin
  kind: function
  signature: Spin() int
  purpose: rewrites packs and binary
- path: environment/milldesk/main.go
  symbol: run
  kind: function
  signature: run(args []string) int
  purpose: CLI dispatch
- path: environment/milldesk/play.go
  symbol: Play
  kind: function
  signature: Play(lampPath string) int
  purpose: lamp readout writer

#### flipping_point_contract

locations:
  - id: A
    path: environment/oxbind/seal.go
    controls_tests: [test_lx02_anchor_pair, test_lx03_held_pair, test_lx04_prior_pair, test_lx07_json_shape, test_lx10_held_second, test_lx11_twice_stable]
  - id: B
    path: environment/packbay/fetch.go
    controls_tests: [test_lx01_id_parity, test_lx06_gap_abort, test_lx09_cross_bind]
  - id: C
    path: environment/milldesk/spin.go
    controls_tests: [test_lx00_native_mill, test_lx05_alien_exit, test_lx08_slot_width, test_lx_zz_corrupt_recover]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

[]

#### code_forbidden_tokens

code_forbidden_tokens: [lanternix, cardwell, glowbank, candela, dwell_s, LAN_FLASH_9C, flash9c, void, slots, readout]
