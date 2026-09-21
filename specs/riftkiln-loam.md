### Decision
GO — Attempt 1. Debugging repair: SLR table mill for a loam recipe. Flat copybay sifts green while a gate after an inner bin close hangs on that inner bin. Three loci: postfix production in the recipe, mill that still ships tables after a quarrel, walker that annotates the last bin.

### Metadata
- version: 2
- Task name: riftkiln-loam
- Title: Nested latch hangs inner
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "slr-tables", "loam-mill", "nesting-cut"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/riftkiln` is a compiled ELF.
- `sift SRC DEST` writes DEST object text from a quern file.
- Schema: `yard` string, `members` array of `peg`/`pen`/`clip` objects as in instruction.md.
- A `clip` after an inner pen close, before the enclosing pen close, is a sibling `clip` object under the enclosing pen, not a property on the inner pen.
- Source fixes under `/app`; mill dirs in `/app/routenote/MAP.txt`.
- Hand-written destination object is not enough.
- If `/app/tblwell/quarrel.lst` still records an unresolved nesting cut and tables would still emit, the MAP helper must exit non-zero and existence of `/app/markcue/brew.ok` is false.
- After a clean mill, `/app/markcue/brew.ok` exists and `/app/tblwell/action.tbl` is what the driver loads.
- Verifier reruns `/app/bin/riftkiln sift`.

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
- path: environment/yghearth/card.yg
  role: mill recipe
- path: environment/tblbake/oven.rs
  role: table baker
- path: environment/nestwalk/cursor.rs
  role: reduce walker

### fix_frontier
- count: 3
- distribution: yghearth, tblbake, nestwalk
- naming_policy: opaque rib_a rib_b rib_c
- forbidden_stems: sift, gate, bin, quarrel, nest
- helpers_policy: rewire.rs decoy off frontier
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON member kinds, helper exit codes, ELF magic
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: post-process JSON to move one gate

### category_profile
- challenge_family: parser_table_association
- bug_family: parser_table_association
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: commands, paths, schemas, symptoms, mill policy on quarrel.lst
- forbidden_instruction_leaks: shift/reduce default, postfix production, walker merge
- category_specific_hardness_bar: copybay sift green while nested gate hangs inner
- category_specific_verifier_risks: test-side rustc, hand JSON, script mill
- coverage_role: debugging C2 rebuild-before-claim

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: copybay sift exit 0
  why_model_misses_it: agents trust the mill self-check
  fairness_guardrail: instruction names the hanging gate
- mechanism: deceptive_but_valid_local_evidence
  placement: nestwalk/rewire.rs plus FLAT_OK note
  why_model_misses_it: post-process looks like the one nested shape
  fairness_guardrail: held-out nested files and quarrel injection
- mechanism: cross_file_cross_format_invariants
  placement: recipe vs action.tbl vs JSON members
  why_model_misses_it: edit JSON only
  fairness_guardrail: verifier reruns sift and recovery brew
- mechanism: stateful_multi_step_dependencies
  placement: quarry.sh after sources
  why_model_misses_it: skip table bake
  fairness_guardrail: ELF plus held-out nested structure

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert sifts a nested loam then bakes
- shortcut_audit: rewire JSON, hand DEST, script bin
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
- sidecar_or_protocol_notes: copybay flat samples bundled

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs yghearth/tblbake/nestwalk
- gx9_contract_risk: low JSON objects
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan
- verifier_command_visible: riftkiln sift
- source_fix_intent_visible: MAP.txt mill dirs
- generated_output_rule_visible: DEST JSON, brew.ok, action.tbl, quarrel.lst
- exact_formula_home: sibling gate under enclosing bin
- schema_home: instruction.md

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Rust SLR mill whose default conflict resolution attaches a nested gate to the inner bin

### realism_source
- source_type: synthetic_exception
- evidence_basis: yacc/bison shift/reduce default on a postfix nesting cut; mill logs conflicts and still ships
- upstream_or_synthetic_rationale: cannot ship a full bison toolchain tree
- minimization_preserves: copybay green, nested gate hangs inner, skip bake
- synthetic_exception_review: rewire.rs post-process is a realistic ops workaround decoy

### Failure topology
Operators see flat copybay sift succeed after a recipe change that added an optional gate clause. A nested bin that closes and then writes a gate before its enclosing bin closes still loads. The mill writes tables and a quarrel ledger and exits zero. The JSON grows a gate field on the inner bin. The mill's own check never opens a nested file.

### Environment shape
Rust sift CLI, recipe hearth, table baker, reduce walker, copybay flats, actrib tables, okcue marker, deskfold map, decoy rewire helper, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, rustc quarry rebuild.

### Test plan
- test_k01_alpha
- test_k02_bravo
- test_k03_charlie
- test_k04_delta
- test_k05_echo
- test_k06_foxtrot
- test_k07_golf
- test_k08_hotel
- test_k09_india
- test_k10_juliet
- test_k11_kilo
- test_k12_lima

### Drafting guardrails
Do not name shift/reduce, postfix production, or walker merge. Tests must not rustc for grading. Punish rewire.rs via held-out nested shape plus rubric.

### Triviality Ledger
- Rewire JSON after sift — blocked by held-out files and recovery brew that reloads action.tbl.
- Hand-written DEST — blocked by corrupt-then-sift recovery.
- Source-only without quarry — stale tables; R5 source_only.sh.
- Script mill replacing ELF — blocked by ELF magic in tests.

### Per-gate Pitfall Inventory
- RC2: repair paths in MAP.txt name directories, not rib_a/rib_b/rib_c.
- GX9: grade JSON kinds and helper exits, not boolean flags.
- CR8: boot dispatches; baker vs walker split.
- R5: tests do not quarry for score; lima recovery only reruns MAP helper.
- R3: every graded test fails on broken tree.
- P4: rewire.rs decoy punished by rubric.

### Initial Draft Commitments
- environment/siftcli/boot.rs
- environment/siftcli/usage.txt
- environment/yghearth/card.yg
- environment/tblbake/oven.rs
- environment/nestwalk/cursor.rs
- environment/nestwalk/rewire.rs
- environment/deskfold/MAP.txt
- environment/deskfold/FLAT_OK.txt
- environment/copybay/flat.quern
- environment/quarry.sh
- environment/Dockerfile
- environment/.dockerignore
- environment/coldpkg/wheels (copied)
- environment/coldpkg/debs (copied)
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
- preship/alt_solution.sh

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

- path: environment/tblbake/oven.rs
  symbol: rib_a
  kind: function
  signature: rib_a(n: usize) -> i32
  purpose: returns whether a nonempty quarrel stops the mill
- path: environment/yghearth/card.yg
  symbol: rib_b
  kind: constant
  signature: rib_b
  purpose: marks the mill recipe the baker reads
- path: environment/nestwalk/cursor.rs
  symbol: rib_c
  kind: function
  signature: rib_c(acc: Node, neu: Node) -> Node
  purpose: joins a completed member onto the open member list

#### flipping_point_contract

locations:
  - id: A
    path: environment/yghearth/card.yg
    controls_tests: [test_k01_alpha, test_k02_bravo, test_k03_charlie, test_k04_delta]
  - id: B
    path: environment/tblbake/oven.rs
    controls_tests: [test_k05_echo, test_k06_foxtrot, test_k07_golf, test_k08_hotel]
  - id: C
    path: environment/nestwalk/cursor.rs
    controls_tests: [test_k09_india, test_k10_juliet, test_k11_kilo, test_k12_lima]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/nestwalk/rewire.rs
  kind: helper
  rhymes_with: rib_c
  non_fix_purpose: walks a JSON object and moves a gate onto the last bin
- path: environment/deskfold/FLAT_OK.txt
  kind: config-reader
  rhymes_with: rib_a
  non_fix_purpose: claims mill health is copybay sift count

#### code_forbidden_tokens

code_forbidden_tokens: [riftkiln, ELF, sift, quern, mill, directories, deskfold, MAP.txt, disk, verifier, copybay, yard, pen, clip, ident, members, peg, tag, mark, stem, kind, actrib, quarrel.lst, cut, tables, helper, okcue, brew.ok, action.tbl, driver]
