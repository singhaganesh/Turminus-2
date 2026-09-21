### Decision
GO — Attempt 1. Debugging repair: freeze clones a bag handle, intern cells stay live, and the writer still treats an empty spool as success. Scalars in pair.json move. The bag lists do not.

### Metadata
- version: 2
- Task name: glazeurn-spool
- Title: Freeze bag still tracks live
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "session-freeze", "intern-table", "rebuild"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/glazeurn` is a compiled ELF.
- `bind` walks `/app/daycards` and refreshes mill pieces named in `/app/vatslip/TREE.txt`.
- `pair` reads `/app/spoolbay/shift.spool` and writes `/app/inkpit/pair.json`.
- Keys are tick, mark, frost_bag, live_bag.
- On a heat spool, frost_bag is the pre-kiln token list and live_bag is the post-kiln list.
- Heat adds one to tick and two to mark; peek leaves bags aligned and also adds those scalars.
- Identical bag lists after heat, or an empty spool, must exit non-zero without GUARD.
- Success writes GUARD containing ok.
- Source fixes under `/app`. Hand-written pair.json is not enough. Verifier reruns `/app/bin/glazeurn pair`.

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

- path: environment/foldrib/rim.rs
  role: freeze handle copy compiled into the mill
- path: environment/internpit/pool.rs
  role: intern cell copy plus pair object emit
- path: environment/restcue/ink.rs
  role: empty spool and GUARD writer
- path: environment/emitbay/hearth.rs
  role: bind emit of mill pieces
- path: environment/steerpit/boot.rs
  role: bind and pair entry

### fix_frontier

- count: 3
- distribution: foldrib, internpit, restcue
- naming_policy: opaque rim_a rim_b rim_c
- forbidden_stems: pair, bind, bag, frost, tick, mark, spool
- helpers_policy: coverpit/tally.rs decoy off frontier
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON lists, pair exit codes, ELF magic
- forbidden_assertion_styles: boolean answer keys

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: bump tick in tally so scalars look more alive

### category_profile

- challenge_family: state_snapshot_aliasing
- bug_family: state_snapshot_aliasing
- profile_name: state_recovery_crash_consistency
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: Rc clone, intern snapshot, empty-spool success
- category_specific_hardness_bar: scalars move while bag lists stay glued until freeze, intern, and GUARD cooperate
- category_specific_verifier_risks: test-side rustc, hand pair.json, script mill
- coverage_role: debugging C2 rebuild-before-claim

### difficulty_mechanism_plan

- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: tick and mark already follow the kiln
  why_model_misses_it: agents trust the scalars
  fairness_guardrail: instruction names glued bag lists
- mechanism: deceptive_but_valid_local_evidence
  placement: COVER.txt extra tick
  why_model_misses_it: raising tick looks like a freeze
  fairness_guardrail: bag lists still glued
- mechanism: cross_file_cross_format_invariants
  placement: freeze handle vs intern cells vs GUARD
  why_model_misses_it: edit pair.json only
  fairness_guardrail: verifier reruns pair
- mechanism: stateful_multi_step_dependencies
  placement: bake.sh after sources
  why_model_misses_it: skip rustc
  fairness_guardrail: ELF required after sources

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert compares pre/post bag lists then rebuilds
- shortcut_audit: tally tick, hand json, script bin
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
- sidecar_or_protocol_notes: shift.spool bundled

### satisfiability_risk

- rc2_planned_name_risk: low — opaque rim_* vs public pair.json keys
- gx9_contract_risk: low — no per-scenario answer table
- cr1_symbol_frontier_risk: low — three named symbols
- hidden_contract_risk: low — schema and spool lines in instruction

### actionability_plan

- verifier_command_visible: glazeurn pair
- source_fix_intent_visible: TREE.txt crates under /app
- generated_output_rule_visible: pair.json plus GUARD
- exact_formula_home: instruction.md heat and peek add one to tick and two to mark
- schema_home: instruction.md

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- justification_if_none: No promoted reference matches a Rust session mill whose freeze shares a bag handle while intern cells mutate in place and the writer still greens an empty spool.

### realism_source

- source_type: real_bug
- evidence_basis: shallow clone of a collection handle (Rc/Arc clone) plus interned payloads mutated in place, a recurring session-inspector defect
- upstream_or_synthetic_rationale: same class as UI freeze and debugger snapshot aliasing
- minimization_preserves: handle clone, intern mutate, empty success
- synthetic_exception_review: not required

### Failure topology
pair returns 0 and tick/mark move, so the mill looks healthy. frost_bag still lists the post-kiln tokens. A cover note that bumps tick does not split the lists. Empty input still writes GUARD.

### Environment shape
steerpit CLI, foldrib freeze, internpit cells, restcue GUARD, emitbay bind emit, spoolbay input, daycards, vatslip notes, coverpit decoy, bake.sh.

### Required artifacts
instruction, tests, Dockerfile with verifier deps, solve.sh, task.toml allow_internet false, small Rust mill, rubric.txt.

### Test plan
- first/second/third list: freeze length omits the pushed token
- hold/late/mid list: intern swap remains on frost_bag
- tiny_exit: empty spool nonzero, GUARD absent
- map_obj: schema keys
- seal_bit: GUARD ok on split rewrite
- zz_restore: corrupt pair.json then pair
- hdr_magic: ELF plus split lists
- single_shot: one pair subprocess

### Drafting guardrails
Do not name Rc, intern snapshot, or empty-success in instruction, comments, or test names. No rebuild command in instruction.

### Triviality Ledger

- tally tick bump moves scalars and still leaves glued bag lists
- hand pair.json fails zz_restore
- script mill fails ELF
- clone-only of ids without intern cells still leaks swap
- intern-only without id copy still leaks push

### Per-gate Pitfall Inventory

- RC1: oracle writes freeze, intern, and GUARD logic, not a delete
- RC2: opaque rim_* paths, no broken_* names
- RC3: tests check token lists, not file existence
- RC4: held-out spool bytes live in tests
- RC5: no golden pair.json in environment
- RC6: symptoms-only
- RC7: multi-file oracle
- GX9: no scenario answer table
- CR2: three roots, cap 0.5

### Initial Draft Commitments

- instruction.md
- task.toml
- output_contract.toml
- construction_manifest.json
- rubric.txt
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- environment/Dockerfile
- environment/.dockerignore
- environment/bake.sh
- environment/steerpit/boot.rs
- environment/steerpit/usage.txt
- environment/foldrib/rim.rs
- environment/sessbay/hold.rs
- environment/sessbay/load.rs
- environment/internpit/pool.rs
- environment/restcue/ink.rs
- environment/emitbay/hearth.rs
- environment/emitbay/main.rs
- environment/daycards/oak.card
- environment/daycards/elm.card
- environment/spoolbay/shift.spool
- environment/vatslip/TREE.txt
- environment/vatslip/ROUTE.txt
- environment/coverpit/tally.rs
- environment/coverpit/COVER.txt
- environment/noteurn/LAYOUT.txt
- environment/aptkeg/debs
- environment/pipurn/wheels

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

- path: environment/foldrib/rim.rs
  symbol: rim_a
  kind: function
  signature: rim_a(a: &hold::Sess, b: &hold::Pool) -> hold::Frost
  purpose: copies session handles into a frost record
- path: environment/internpit/pool.rs
  symbol: rim_b
  kind: function
  signature: rim_b(a: &mut hold::Frost, b: &hold::Pool)
  purpose: copies intern cells into the frost record
- path: environment/restcue/ink.rs
  symbol: rim_c
  kind: function
  signature: rim_c() -> i32
  purpose: runs pair, writes GUARD, returns the process code

#### flipping_point_contract

locations:
  - id: A
    path: environment/foldrib/rim.rs
    controls_tests: [test_gz01_first_list, test_gz02_second_list, test_gz03_third_list, test_gz11_hdr_magic]
  - id: B
    path: environment/internpit/pool.rs
    controls_tests: [test_gz04_keep_list, test_gz05_late_list, test_gz06_mid_list, test_gz12_single_shot]
  - id: C
    path: environment/restcue/ink.rs
    controls_tests: [test_gz07_tiny_exit, test_gz08_map_obj, test_gz09_seal_bit, test_gz10_zz_restore]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/coverpit/tally.rs
  kind: helper
  rhymes_with: rim_c
  non_fix_purpose: reads COVER.txt extra tick
- path: environment/coverpit/COVER.txt
  kind: config-reader
  rhymes_with: rim_b
  non_fix_purpose: claims a raised tick freezes the bag

#### code_forbidden_tokens

code_forbidden_tokens: [ops, mill, glazeurn, ELF, bind, daycards, vatslip, TREE.txt, pair, spoolbay, shift.spool, inkpit, pair.json, pipeline, modules, script, interpreter, verifier, frost_bag, live_bag, rewrite, kiln, spool, tick, mark, GUARD, Success, empty, arrays, strings, mode, peek, swap, push]
