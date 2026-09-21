### Decision
GO — Attempt 1. Debugging repair: a baked field puller plus a truncated octet take, a layout parser that bumps wide rows, and a writer that still emits on a short body. Small values look right. The live capture's spanning integer does not.

### Metadata
- version: 2
- Task name: weltquay-rib
- Title: Live capture one integer drifts
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "trace-decoder", "bit-packing", "rebuild"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/weltquay` is a compiled ELF.
- `pour` reads `/app/quaybag/night.bin` and writes `/app/blotbay/rows.json`.
- Keys are kind, lane, mode, welt, tail, mark; each an integer.
- On the shipped capture, five integers match the book and one does not until sources are repaired.
- A body shorter than the layout width exits non-zero and must not leave rows.json.
- Source fixes under `/app`; modules named in `/app/keepfold/TREE.txt`.
- Hand-copied rows objects are not enough. Verifier reruns `/app/bin/weltquay pour`.

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

- path: environment/octetkiln/take.rs
  role: bit take helper compiled into the mill
- path: environment/octetkiln/emit.rs
  role: kiln emit that bakes vaultbin/pull.rs
- path: environment/stitchbay/card.rs
  role: layout row parser used by the kiln emit
- path: environment/peekurn/ink.rs
  role: pour writer for rows.json

### fix_frontier

- count: 3
- distribution: octetkiln, stitchbay, peekurn
- naming_policy: opaque rib_a rib_b rib_c
- forbidden_stems: pour, welt, layout, rows
- helpers_policy: nudgepit/tally.rs decoy off frontier
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON integers, pour exit codes, ELF magic
- forbidden_assertion_styles: boolean answer keys

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: bump the welt start by one octet

### category_profile

- challenge_family: packed_record_decode
- bug_family: packed_record_decode
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: single-octet take, start bump, short-body write
- category_specific_hardness_bar: in-byte integers stay right while one live integer stays wrong until kiln+parser+writer cooperate
- category_specific_verifier_risks: test-side rustc, hand rows.json, script mill
- coverage_role: debugging C2 rebuild-before-claim

### difficulty_mechanism_plan

- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: in-byte integers already match
  why_model_misses_it: agents trust the five matching keys
  fairness_guardrail: instruction names one drifting integer
- mechanism: deceptive_but_valid_local_evidence
  placement: TREE.txt line-count cover story and start bump
  why_model_misses_it: widening the row start looks like a layout fix
  fairness_guardrail: live capture still disagrees
- mechanism: cross_file_cross_format_invariants
  placement: LAYOUT rows vs baked pull vs rows.json
  why_model_misses_it: edit rows.json only
  fairness_guardrail: verifier reruns pour
- mechanism: stateful_multi_step_dependencies
  placement: wick.sh after sources
  why_model_misses_it: skip rustc
  fairness_guardrail: ELF required after sources

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert compares live capture integers then rebuilds
- shortcut_audit: layout line count, hand rows.json, script bin
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
- sidecar_or_protocol_notes: layout card and live capture bundled

### satisfiability_risk

- rc2_planned_name_risk: low — fix dirs are kiln/parser/writer roots with opaque symbols
- gx9_contract_risk: low JSON objects without scenario tables
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan

- verifier_command_visible: weltquay pour
- source_fix_intent_visible: pipeline modules in TREE.txt
- generated_output_rule_visible: rows.json integers
- exact_formula_home: integers derived from the capture plus layout rows
- schema_home: instruction.md and TREE.txt

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- justification_if_none: no promoted reference for a Rust packed-record mill whose kiln take stops at one octet while a layout parser bumps wide rows

### realism_source

- source_type: synthetic_exception
- evidence_basis: packed flag words in telemetry records whose field take stays inside one octet
- upstream_or_synthetic_rationale: no vendor decoder tree shipped
- minimization_preserves: in-byte match plus one live miss plus short-body write
- synthetic_exception_review: start bump is a realistic layout workaround

### Failure topology
The mill prints six integers from a four-octet body. Five already match because those slices sit inside one octet. The remaining integer is assembled only after the kiln take walks past the first octet, the emit bake uses the layout start without bumping it, and pour refuses a truncated body. A start bump that moves the row into the next octet can look locally plausible and still miss the live capture.

### Environment shape
A CLI crate, a kiln take, a layout parser, an emit that bakes pull.rs, a pour writer, layout cards, a live capture, rebuild wick, and a line-count decoy note.

### Required artifacts
instruction, tests, Dockerfile with verifier deps, solve.sh, task.toml with allow_internet false, environment components listed in Initial Draft Commitments.

### Test plan
- test_wq01_first_num: live capture welt integer matches independent take
- test_wq02_second_num: held-out spanning body
- test_wq03_third_num: second held-out spanning body
- test_wq04_mid_num: live kind stays aligned while welt matches
- test_wq05_late_num: live mark stays aligned while welt matches
- test_wq06_hold_num: third held-out spanning body
- test_wq07_tiny_exit: short body non-zero exit
- test_wq08_map_doc: required keys present and welt matches
- test_wq09_pair_num: two live in-byte keys plus welt
- test_wq10_zz_restore: corrupt rows then pour recovers
- test_wq11_hdr_magic: ELF plus welt
- test_wq12_single_shot: one pour subprocess

### Drafting guardrails
Do not name octet crossing, masks, start bumps, or wick.sh in instruction.md. Keep TREE.txt as operator notes. No bug comments. Oracle full-file writes.

### Triviality Ledger

- Textbook rewrite of the in-octet kiln slice to the old-desk low-bit join greens neither the live in-byte keys nor the spanning integer because the five matching keys already fix the house packing.
- Widening a wide row's start still misses the live spanning integer once the kiln take joins leftover bits from the next octet.
- Hand-writing rows.json fails recovery because pour overwrites from the running mill.
- A script mill fails the ELF check on `/app/bin/weltquay`.

### Per-gate Pitfall Inventory

- RC2: fix paths stay under octetkiln, stitchbay, peekurn with source files only.
- GX9: instruction states keys and the one-integer symptom, not a scenario answer table.
- CR1: oracle symbols are rib_a, rib_b, rib_c.
- CR8: boot dispatches pour only; emit is a separate kiln binary.
- GX6: symptoms only; no causal patch recipe.
- R5: tests never call wick.sh; they grade the prebuilt mill.
- R7: ELF magic on the mill after the agent rebuild plus held-out bodies.

### Initial Draft Commitments

- task.toml
- instruction.md
- output_contract.toml
- construction_manifest.json
- rubric.txt
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- environment/Dockerfile
- environment/.dockerignore
- environment/wick.sh
- environment/weltcli/boot.rs
- environment/weltcli/usage.txt
- environment/octetkiln/take.rs
- environment/octetkiln/emit.rs
- environment/octetkiln/house.rs
- environment/octetkiln/lsb.rs
- environment/stitchbay/card.rs
- environment/peekurn/ink.rs
- environment/vaultbin/pull.rs
- environment/nudgepit/tally.rs
- environment/keepfold/TREE.txt
- environment/keepfold/COVER.txt
- environment/ribcards/LAYOUT.txt
- environment/quaybag/night.bin
- environment/crateoff/README.txt
- environment/crateoff/debs/
- environment/crateoff/wheels/
- preship/preship.json
- preship/source_only.sh
- preship/decoy_fix.sh
- preship/shortcut_fix.sh
- preship/alt_solution.sh
- preship/oracle/take.rs
- preship/oracle/card.rs
- preship/oracle/ink.rs

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

- path: environment/octetkiln/take.rs
  symbol: rib_a
  kind: function
  signature: rib_a(buf: &[u8], pos: u32, n: u32) -> u32
  purpose: reads n bits starting at pos from buf
- path: environment/stitchbay/card.rs
  symbol: rib_b
  kind: function
  signature: rib_b() -> Vec<Row>
  purpose: loads layout rows for the kiln emit
- path: environment/peekurn/ink.rs
  symbol: rib_c
  kind: function
  signature: rib_c() -> i32
  purpose: writes the rows object from the live capture

#### flipping_point_contract

locations:
  - id: A
    path: environment/octetkiln/take.rs
    controls_tests: [test_wq01_first_num, test_wq02_second_num, test_wq03_third_num, test_wq11_hdr_magic]
  - id: B
    path: environment/stitchbay/card.rs
    controls_tests: [test_wq04_mid_num, test_wq05_late_num, test_wq06_hold_num, test_wq12_single_shot]
  - id: C
    path: environment/peekurn/ink.rs
    controls_tests: [test_wq07_tiny_exit, test_wq08_map_doc, test_wq09_pair_num, test_wq10_zz_restore]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/nudgepit/tally.rs
  kind: helper
  rhymes_with: rib_c
  non_fix_purpose: counts LAYOUT.txt lines
- path: environment/octetkiln/emit.rs
  kind: helper
  rhymes_with: rib_a
  non_fix_purpose: bakes vaultbin/pull.rs from layout rows
- path: environment/keepfold/COVER.txt
  kind: config-reader
  rhymes_with: rib_b
  non_fix_purpose: claims coverage is the layout line count
- path: environment/octetkiln/house.rs
  kind: helper
  rhymes_with: rib_a
  non_fix_purpose: in-octet slice used by the kiln take
- path: environment/octetkiln/lsb.rs
  kind: helper
  rhymes_with: rib_a
  non_fix_purpose: old-desk low-bit join, unused by pour

#### code_forbidden_tokens

code_forbidden_tokens: [investigators, quaybag, night.bin, weltquay, pour, blotbay, rows.json, integer, kind, lane, mode, welt, tail, mark, mill, host, native, program, ELF, sources, keepfold, TREE.txt, rows, hand, substitute, edits, verifier, capture, image, book, body, layout, width, process]
