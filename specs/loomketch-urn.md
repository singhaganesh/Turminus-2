### Decision
GO — Attempt 1. Debugging repair: a Rust mill binds AddressSanitizer worker journals into a numbered bound file and a desk sheet. Finding bodies look stable while issue numbers drift across binds, directory layouts, and worker-file renames. Agent must rebuild the native mill after source repair.

### Metadata
- version: 2
- Task name: loomketch-urn
- Title: Journals bound with drifting issues
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "asan-journals", "issue-identity", "desk-sheet"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/loomketch` is a compiled ELF mill.
- `bind` reads `/app/vatlogs` and refreshes `/app/inkbay/bound.json` plus `/app/inkbay/desk.tsv`.
- Two binds of the same journal texts are byte-identical across processes, directory layouts, and worker-file renames.
- Desk rows that cite an issue stay attached to the same `body`.
- Finding set matches the journals.
- Schema: `{"findings":[{"issue":N,"kind":"<kind>","frames":["<sym>",...],"body":"<text>"}]}` with `issue` starting at 1.
- `desk.tsv` header `issue	kind	body`.
- Success writes `/app/inkbay/GUARD` with `ok`. Empty or truncated journals exit non-zero and omit GUARD. Paths outside `/app/vatlogs` fail.
- Verifier reruns `/app/bin/loomketch bind`. Hand-placed JSON/TSV is not enough. Native ELF after source work.

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

- path: environment/parselot/tally.rs
  role: journal parse and issue assignment
- path: environment/foldrib/clip.rs
  role: frame clip helper
- path: environment/deskemit/sheet.rs
  role: desk sheet emit

### fix_frontier

- count: 3
- distribution: parselot, foldrib, deskemit
- naming_policy: opaque tally/clip/emit
- forbidden_stems: bind, sort, glob, index, stack
- helpers_policy: walkcue alpha-path decoy is not a frontier
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON artifacts, TSV rows, exit codes, ELF magic
- forbidden_assertion_styles: boolean answer keys

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: enable alpha-path sort then still number as threads finish

### category_profile

- challenge_family: concurrency_ordering
- bug_family: concurrency_ordering
- profile_name: concurrency_ordering
- allowed_instruction_disclosures: concurrent-looking bind runs, public identity invariant, commands, journal paths, durable bound/desk outputs
- forbidden_instruction_leaks: race window, thread join, glob order, interceptor-fold recipe, patch files
- category_specific_hardness_bar: two schedulers (thread completion and dirent order) plus durable desk identity must coordinate
- category_specific_verifier_risks: sleeps, single-run traces, tests that pass by sorting filenames
- coverage_role: debugging C3 prove-it-twice on numbered sanitizer merge
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: parallel numbering, interceptor skip list, positional desk zip

### difficulty_mechanism_plan

- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: bind exits 0 with a complete finding set while issue numbers move
  why_model_misses_it: content assertions look green
  fairness_guardrail: instruction names desk citations drifting
- mechanism: deceptive_but_valid_local_evidence
  placement: KETCH_ALPHA / walkcue path sort
  why_model_misses_it: sorted paths look like a stability fix
  fairness_guardrail: rename and holdout journals still fail
- mechanism: cross_file_cross_format_invariants
  placement: bound.json issue field vs desk.tsv rows vs folded frames
  why_model_misses_it: edits JSON only
  fairness_guardrail: verifier reruns bind
- mechanism: stateful_multi_step_dependencies
  placement: source fix then hearth rebuild then bind
  why_model_misses_it: skip hearth
  fairness_guardrail: instruction requires native ELF after sources

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert clips interceptor frames, assigns after join, emits desk by issue
- shortcut_audit: alpha-path env, hand JSON, skip hearth, python mill
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
- sidecar_or_protocol_notes: worker journals bundled

### satisfiability_risk

- rc2_planned_name_risk: low — fix dirs are parselot/foldrib/deskemit
- gx9_contract_risk: low JSON objects and TSV rows
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan

- verifier_command_visible: loomketch bind
- source_fix_intent_visible: pipeline modules in MAP.txt
- generated_output_rule_visible: bound.json desk.tsv GUARD
- exact_formula_home: issue starts at 1; GUARD is ok
- schema_home: instruction.md and MAP.txt

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- justification_if_none: no promoted reference for a Rust AddressSanitizer journal binder with drifting issue numbers and a coupled desk sheet

### realism_source

- source_type: synthetic_exception
- evidence_basis: parallel sanitizer log merge numbered during parse; triage sheets bind to issue ids
- upstream_or_synthetic_rationale: cannot ship a private sanitizer CI merger tree
- minimization_preserves: complete finding set, moving issue numbers, alpha-path decoy, skip rebuild
- synthetic_exception_review: path-sort decoy is a realistic ops workaround

### Failure topology
Operators see bind succeed with every finding present, yet a second bind or a renamed worker file moves issue numbers so the desk sheet cites a different body. Path sorting looks like a fix. Interceptor frames and hex PCs still split one bug across workers. The desk emitter walks array order after a kind sort, so even a stable bound object can print a drifting sheet.

### Environment shape
Rust mill, journal walker, parallel tally, frame clip, desk emit, alpha-path decoy, template, worker journals, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, rustc hearth rebuild.

### Test plan
- test_lk02_dir_layout_twice
- test_lk03_rename_worker_files
- test_lk04_set_equals_corpus
- test_lk05_row_keeps_same_text
- test_lk06_ids_from_one
- test_lk07_empty_exit
- test_lk08_trunc_exit
- test_lk09_outside_refused
- test_lk10_marker_text
- test_lk12_unseen_corpus

### Drafting guardrails
Do not name glob order, thread join, interceptor lists, or alpha-path as the fix. Tests must not hearth. Punish KETCH_ALPHA via rename plus rubric.

### Triviality Ledger

- Enable KETCH_ALPHA path sort — blocked by rename/holdout journals whose names do not match identity.
- Hand-written bound.json — blocked by bind rerun in the graded suite.
- Source-only without hearth — binary still races; R5 source_only.sh.
- Python mill replacing ELF — blocked by ELF magic plus held-out journals.

### Per-gate Pitfall Inventory

- RC2: repair paths in MAP.txt name directories, not tally/clip/emit.
- GX9: grade JSON issue/body pairs, not boolean flags.
- CR8: main dispatches tally then emit only.
- R5: tests do not hearth; suite reruns bind only.
- R3: every graded test fails on broken tree.
- P4: walkcue/KETCH_ALPHA decoy punished by rubric.

### Initial Draft Commitments

- environment/ketchcli/main.rs
- environment/urnwalk/walk.rs
- environment/parselot/tally.rs
- environment/foldrib/clip.rs
- environment/deskemit/sheet.rs
- environment/walkcue/alpha.rs
- environment/deskcue/MAP.txt
- environment/opsfold/SHIFT.txt
- environment/tplbay/bound.tpl
- environment/vatlogs/*.asan
- environment/hearth.sh
- environment/Dockerfile
- environment/.dockerignore
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

- path: environment/parselot/tally.rs
  symbol: tally
  kind: function
  signature: tally(a: &str) -> Result<Vec<Rec>, i32>
  purpose: parses journals into numbered records
- path: environment/foldrib/clip.rs
  symbol: clip
  kind: function
  signature: clip(a: &[String]) -> Vec<String>
  purpose: reduces frame lists
- path: environment/deskemit/sheet.rs
  symbol: emit
  kind: function
  signature: emit(a: &[Rec]) -> i32
  purpose: writes desk.tsv

#### flipping_point_contract

locations:
  - id: A
    path: environment/parselot/tally.rs
    controls_tests: [test_lk02_dir_layout_twice, test_lk03_rename_worker_files, test_lk06_ids_from_one]
  - id: B
    path: environment/foldrib/clip.rs
    controls_tests: [test_lk04_set_equals_corpus, test_lk12_unseen_corpus, test_lk07_empty_exit, test_lk08_trunc_exit]
  - id: C
    path: environment/deskemit/sheet.rs
    controls_tests: [test_lk05_row_keeps_same_text, test_lk09_outside_refused, test_lk10_marker_text]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/walkcue/alpha.rs
  kind: helper
  rhymes_with: tally
  non_fix_purpose: sorts journal paths when KETCH_ALPHA=1

#### code_forbidden_tokens

code_forbidden_tokens: [loomketch, vatlogs, inkbay, deskcue, bound.json, desk.tsv, GUARD, AddressSanitizer, bind]
