### Decision
GO — Attempt 1. Debugging repair: gasket hopper codegen plus a compiled hop table. Self-check and knit stay green while poke of a new card WIRE falls through. Three loci: slot span, sequential fill, seal that trusts the shadow roster.

### Metadata
- version: 2
- Task name: wirehop-gasket
- Title: Hopper still misses new wire
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "dispatcher", "gasket-hopper", "opcode-table"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/gasketd` is a compiled ELF.
- `bind` refreshes `/app/mistwell/roster.json` from `/app/buscards`.
- `jab N` prints `{"wire":N,"reply":S}` from the hopper already inside gasketd.
- `cork` writes `/app/corkbay/seal.json` with `served` (LABEL values in card order) and `status`.
- Cards already under `/app/buscards` at start return their REPLY; unknown integers print `fallthrough`.
- After bind rewrites the roster, jab of a WIRE that only exists on a card added later still prints `fallthrough`; cork then exits non-zero and `status` is not `sealed`.
- Source fixes under `/app`; modules named in `/app/opscribe/MAP.txt`.
- Hand-copied roster or seal files are not enough. Verifier reruns bind, jab, and cork.

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
  role: Rust+python offline image
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/rimcap/span.rs
  role: compiled slot span
- path: environment/hopmat/table.rs
  role: WIRE replies used by jab
- path: environment/lidpit/plug.rs
  role: seal writer

### fix_frontier
- count: 3
- distribution: rimcap, hopmat, lidpit
- naming_policy: opaque rib_a rib_b rib_c
- forbidden_stems: wirehop, poke, wax, knit, span, table
- helpers_policy: tally.rs decoy off frontier
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON poke objects, wax exit codes, seal status strings
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: bump a span constant or count emit.lst lines

### category_profile
- challenge_family: generated_lut_slot_drift
- bug_family: generated_lut_slot_drift
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: slot span, sequential fill, shadow-vs-live seal
- category_specific_hardness_bar: knit and wax green while new WIRE falls through
- category_specific_verifier_risks: test-side rustc, hand seal, script mill
- coverage_role: debugging C2 rebuild-before-claim

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: knit and wax exit 0 while poke prints fallthrough
  why_model_misses_it: agents trust knit and wax
  fairness_guardrail: instruction names the fallthrough symptom
- mechanism: deceptive_but_valid_local_evidence
  placement: COUNT_SRC emit.lst line count
  why_model_misses_it: source list looks complete
  fairness_guardrail: live poke still wrong
- mechanism: cross_file_cross_format_invariants
  placement: cards vs compiled table vs seal.json
  why_model_misses_it: edit seal only
  fairness_guardrail: verifier reruns poke and wax
- mechanism: stateful_multi_step_dependencies
  placement: source fix then stoke.sh
  why_model_misses_it: skip rustc
  fairness_guardrail: ELF required after sources

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert pokes WIRE values then rebuilds
- shortcut_audit: emit.lst count, hand seal, script bin
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
- sidecar_or_protocol_notes: spec cards bundled

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs are slotcap/hullfw/waxdesk
- gx9_contract_risk: low JSON objects
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan
- verifier_command_visible: gasketd bind/jab/cork
- source_fix_intent_visible: pipeline modules in ROUTE.txt
- generated_output_rule_visible: roster.json seal.json poke JSON
- exact_formula_home: poke reply equals card REPLY
- schema_home: instruction.md and ROUTE.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Rust gasket hopper whose compiled hop table truncates while a shadow roster stays complete

### realism_source
- source_type: synthetic_exception
- evidence_basis: firmware jump tables sized by a header the generator does not rewrite; self-test walks a companion list
- upstream_or_synthetic_rationale: cannot ship a vendor RTOS tree
- minimization_preserves: knit/wax green, newest WIRE fallthrough, skip rebuild
- synthetic_exception_review: emit.lst line-count is a realistic decoy

### Failure topology
Operators see knit and wax succeed after a new spec card, yet poke of that card's WIRE prints fallthrough. The generator writes a complete shadow roster. The compiled table fills sequential slots up to a stale span. Seal compares the shadow to the spec, not to the live table.

### Environment shape
Rust hopper CLI, slot span crate, hop table, seal desk, knit emitter, spec cards, decoy tally note, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, rustc stoke rebuild.

### Test plan
- test_g01_first_slot
- test_g02_second_slot
- test_g03_hole_miss
- test_g04_high_slot
- test_g05_newer_slot
- test_g06_mid_slot
- test_g07_open_exit
- test_g08_live_match
- test_g09_keys_obj
- test_g10_zz_restore
- test_g11_hdr_magic
- test_g12_once_pass

### Drafting guardrails
Do not name span, sequential fill, or shadow-vs-live. Tests must not rustc. Punish emit.lst counting via live poke plus rubric.

### Triviality Ledger
- Count emit.lst lines — blocked by live poke replies and wax-on-live.
- Hand-written seal.json — blocked by wax rerun and corrupt-then-wax recovery.
- Source-only without stoke — binary still truncated; R5 source_only.sh.
- Script mill replacing ELF — blocked by ELF magic in tests.

### Per-gate Pitfall Inventory
- RC2: repair paths in ROUTE.txt name directories, not rib_a/rib_b/rib_c.
- GX9: grade poke JSON and status strings, not boolean flags.
- CR8: boot dispatches; wax vs poke split.
- R5: tests do not stoke; zz recovery only reruns cork.
- R3: every graded test fails on broken tree.
- P4: COUNT_SRC decoy punished by rubric.

### Initial Draft Commitments
- environment/gaskcli/boot.rs
- environment/gaskcli/usage.txt
- environment/rimcap/span.rs
- environment/hopmat/table.rs
- environment/slipread/scan.rs
- environment/lidpit/plug.rs
- environment/lidpit/tally.rs
- environment/loomkit/loom.rs
- environment/opscribe/MAP.txt
- environment/opscribe/COUNT_SRC.txt
- environment/stoke.sh
- environment/buscards/a_fan.card
- environment/buscards/b_pump.card
- environment/buscards/c_valve.card
- environment/buscards/d_temp.card
- environment/buscards/e_press.card
- environment/buscards/f_latch.card
- environment/buscards/g_bias.card
- environment/buscards/h_watch.card
- environment/buscards/i_vent.card
- environment/cardbak/buscards/a_fan.card
- environment/cardbak/buscards/b_pump.card
- environment/cardbak/buscards/c_valve.card
- environment/cardbak/buscards/d_temp.card
- environment/cardbak/buscards/e_press.card
- environment/cardbak/buscards/f_latch.card
- environment/cardbak/buscards/g_bias.card
- environment/cardbak/buscards/h_watch.card
- environment/cardbak/buscards/i_vent.card
- environment/Dockerfile
- environment/.dockerignore
- instruction.md
- task.toml
- output_contract.toml
- construction_manifest.json
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- rubric.txt
- preship/preship.json
- preship/source_only.sh
- preship/decoy_fix.sh
- preship/shortcut_fix.sh

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table
- path: environment/rimcap/span.rs
  symbol: rib_a
  kind: function
  signature: rib_a() -> usize
  purpose: returns the compiled slot span
- path: environment/hopmat/table.rs
  symbol: rib_b
  kind: function
  signature: rib_b() -> Vec<Row>
  purpose: builds the live hop table
- path: environment/lidpit/plug.rs
  symbol: rib_c
  kind: function
  signature: rib_c() -> i32
  purpose: writes the seal object

#### flipping_point_contract
locations:
  - id: A
    path: environment/rimcap/span.rs
    controls_tests: [test_g04_high_slot, test_g05_newer_slot, test_g06_mid_slot, test_g11_hdr_magic]
  - id: B
    path: environment/hopmat/table.rs
    controls_tests: [test_g01_first_slot, test_g02_second_slot, test_g03_hole_miss, test_g12_once_pass]
  - id: C
    path: environment/lidpit/plug.rs
    controls_tests: [test_g07_open_exit, test_g08_live_match, test_g09_keys_obj, test_g10_zz_restore]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest
- path: environment/lidpit/tally.rs
  kind: helper
  rhymes_with: rib_c
  non_fix_purpose: counts emit.lst lines for an ops sidecar
- path: environment/opscribe/COUNT_SRC.txt
  kind: config-reader
  rhymes_with: rib_a
  non_fix_purpose: claims coverage is emit.lst line count

#### code_forbidden_tokens
code_forbidden_tokens: [ops, image, gasketd, bind, card, buscards, mistwell, roster.json, jab, integer, wire, reply, cork, corkbay, seal.json, served, LABEL, status, source, work, modules, directories, opscribe, MAP.txt, copying, hand, ELF, verifier, fallthrough, hopper, line, REPLY, WIRE, roster, seal]
