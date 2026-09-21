### Decision
GO — Attempt 1. Debugging repair: sanitiser kind catalog is regenerated as an ordered list while the severity LUT stays positional; a newly added kind looks right and older findings shift. Agent must rebuild the native mill after source repair.

### Metadata
- version: 2
- Task name: kindspill-docket
- Title: Consumer indexes the generated list
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "sanitiser", "kind-catalog", "severity-lut"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/kindspill brew` reads `/app/sanitdesc` sheets and refreshes `/app/spillbay/kinds.ord`, `/app/rankbin/ranks.bin`, `/app/docket/filed.bin`.
- `/app/bin/kindspill peek` prints `{"findings":[{"token":"<id>","severity":N},...]}`.
- Each kind's filed severity equals the sheet RANK; a newly added kind is filed at its declared RANK.
- `brew` exits non-zero when any filed severity would not match its sheet.
- Hyphen/case variants are the same kind.
- Record layout: u16be length, UTF-8 name, u8 rank.
- Verifier reruns brew and peek. Hand-written artifacts are not enough. Native binary after source work.

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
- path: environment/kindmill/roster.rs
  role: name list emit
- path: environment/kindmill/kread.rs
  role: sheet parser helper
- path: environment/emberkit/bake.rs
  role: rank LUT bake
- path: environment/filewell/stamp.rs
  role: docket stamp

### fix_frontier
- count: 3
- distribution: kindmill, emberkit, filewell
- naming_policy: opaque spill/hearth/mark
- forbidden_stems: kindspill, index, sorted
- helpers_policy: KEEP_TAIL decoy; kindmill/kread.rs is a co-resident parser helper, not a named frontier
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON artifacts, exit codes, binary records
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: append the new kind at the tail of the roster

### category_profile
- challenge_family: generated_lut_slot_drift
- bug_family: generated_lut_slot_drift
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: sort order, cache bypass, positional zip
- category_specific_hardness_bar: new kind right versus old findings wrong
- category_specific_verifier_risks: test-side hull, hand-written docket
- coverage_role: debugging C2 rebuild-before-claim

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: brew exits 0 while old tokens carry neighbour ranks
  why_model_misses_it: agents trust brew success and the new kind
  fairness_guardrail: instruction names older findings wrong
- mechanism: deceptive_but_valid_local_evidence
  placement: KEEP_TAIL note and new kind looking right
  why_model_misses_it: appending the new kind appears to freeze slots
  fairness_guardrail: holdout mid token plus every sheet RANK
- mechanism: cross_file_cross_format_invariants
  placement: sheets vs kinds.ord vs named rank records vs peek JSON
  why_model_misses_it: edits JSON only
  fairness_guardrail: verifier reruns brew and peek
- mechanism: stateful_multi_step_dependencies
  placement: source fix then agent hull rebuild
  why_model_misses_it: skip hull
  fairness_guardrail: instruction requires native binary after sources

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert joins by folded id then hull
- shortcut_audit: tail append, hand docket, skip hull
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
- sidecar_or_protocol_notes: sheets and cache bundled

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs are kindmill/emberkit/filewell
- gx9_contract_risk: low JSON objects
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan
- verifier_command_visible: kindspill brew/peek
- source_fix_intent_visible: pipeline modules in LAYOUT.txt
- generated_output_rule_visible: kinds.ord ranks.bin filed.bin
- exact_formula_home: filed severity equals sheet RANK
- schema_home: instruction.md and LAYOUT.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Rust sanitiser kind catalog with a compiled positional severity LUT

### realism_source
- source_type: synthetic_exception
- evidence_basis: sorted generated catalogs paired with declaration-order LUTs after a kind insert
- upstream_or_synthetic_rationale: cannot ship a private sanitiser compiler tree
- minimization_preserves: brew green, new kind right, old ranks shifted, skip rebuild
- synthetic_exception_review: tail-append is a realistic decoy

### Failure topology
Operators see brew succeed and the newly added kind filed at its RANK while older findings pick neighbour severities. The name list is ordered independently of sheet scan order, the LUT is a byte vector plus a stale token cache that special-cases unseen names, and stamp never folds hyphen/case aliases. Tail-appending the new kind in KEEP_TAIL still leaves the next mid-sort insert broken.

### Environment shape
Rust mill, rank bake, docket stamp, sanitiser sheets, stale cache, tail decoy, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, rustc hull rebuild.

### Test plan
- test_ks01_rank_parity
- test_ks02_holdout_mid
- test_ks03_ord_lines
- test_ks04_unique_ids
- test_ks05_named_records
- test_ks06_shift_visible
- test_ks08_mismatch_exit
- test_ks09_fold_hyphen
- test_ks11_peek_schema
- test_ks12_zz_corrupt
- test_ks13_brew_once
- test_ks14_cold_ignored

### Drafting guardrails
Do not name sort, cache, or slot zip. Tests must not hull. Punish tail-append via holdout plus rubric.

### Triviality Ledger
- Append new kind at roster tail — blocked by holdout mid token and sheet parity.
- Hand-written docket — blocked by brew rerun and corrupt-then-brew recovery.
- Source-only without hull — binary still positional; R5 source_only.sh.
- Naive patch -i oracle — blocked by full-file writes in solve.sh.

### Per-gate Pitfall Inventory
- RC2: repair paths in LAYOUT.txt name directories, not spill/hearth/mark.
- GX9: grade JSON token/severity, not boolean flags.
- CR8: main dispatches; brew vs peek split.
- R5: tests do not hull; zz recovery only reruns brew.
- R3: every graded test fails on broken tree.
- P4: KEEP_TAIL decoy punished by rubric.

### Initial Draft Commitments
- environment/kindmill/roster.rs
- environment/kindmill/kread.rs
- environment/emberkit/bake.rs
- environment/filewell/stamp.rs
- environment/cratebin/main.rs
- environment/Makefile
- environment/notes/LAYOUT.txt
- environment/endpin/KEEP_TAIL.txt
- environment/sanitdesc/*.kind
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

- path: environment/kindmill/roster.rs
  symbol: spill
  kind: function
  signature: spill() -> Vec<String>
  purpose: writes kinds.ord
- path: environment/emberkit/bake.rs
  symbol: hearth
  kind: function
  signature: hearth(names: &[String]) -> Vec<u8>
  purpose: writes ranks.bin
- path: environment/filewell/stamp.rs
  symbol: mark
  kind: function
  signature: mark() -> i32
  purpose: writes filed.bin and returns brew status

#### flipping_point_contract

locations:
  - id: A
    path: environment/kindmill/roster.rs
    controls_tests: [test_ks01_rank_parity, test_ks02_holdout_mid, test_ks03_ord_lines, test_ks04_unique_ids]
  - id: B
    path: environment/emberkit/bake.rs
    controls_tests: [test_ks05_named_records, test_ks06_shift_visible, test_ks08_mismatch_exit, test_ks12_zz_corrupt]
  - id: C
    path: environment/filewell/stamp.rs
    controls_tests: [test_ks09_fold_hyphen, test_ks11_peek_schema, test_ks13_brew_once, test_ks14_cold_ignored]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

[]

#### code_forbidden_tokens

code_forbidden_tokens: [kindspill, sanitdesc, spillbay, rankbin, docket, kinds.ord, ranks.bin, filed.bin]
