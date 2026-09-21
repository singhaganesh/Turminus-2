### Decision
GO — Attempt 1. Debugging repair: GNU-versioned crash-dump fold library plus mill. Ordinary sip still emits the retained fold while a named current node already emits the rework. Three loci: alias lines, home-node pick, card/SEAL writer.

### Metadata
- version: 2
- Task name: draughtpin-verndock
- Title: Ordinary sip keeps old fold
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "shared-object", "crash-fold", "abi-nodes"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/draughtpin` starts with the four-byte ELF header. `/app/lib/libdraught.so` is the shared object.
- `sip DUMP` opens the library without a slot argument and writes `/app/inkvat/card.json`.
- `mark DUMP SLOT` opens through a slot listed in `/app/abifolio/RULES.txt`.
- Ordinary sip still shows the pre-rework fold; mark of the current slot already shows the corrected fold; mark of the compatibility slot keeps the pre-rework fold.
- card.json keys slot, text, kind. After sip, kind is bare and slot is the current slot from RULES.txt. After mark, kind is named.
- Success writes `/app/inkvat/SEAL` containing ok. Zero-length dump or unlisted mark slot exits non-zero with SEAL absent.
- Source fixes under `/app`; directories in `/app/abifolio/WALK.txt`. Hand-written card.json is not enough. Verifier reruns sip and mark.

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
- path: environment/aliaspit/hue.S
  role: version alias lines
- path: environment/narbay/loom.rs
  role: home node pick
- path: environment/vatrib/qat.rs
  role: card and SEAL writer

### fix_frontier
- count: 3
- distribution: aliaspit, narbay, vatrib
- naming_policy: opaque hue knit qat
- forbidden_stems: sip, mark, fold, node, SEAL
- helpers_policy: DROP.txt decoy; weft/main.rs and cliurn/boot.rs are not oracle frontier
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON strings, exit codes, folded bytes
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: delete the retained body so only the new fold remains

### category_profile
- challenge_family: false_green_rehearsal_window
- bug_family: false_green_rehearsal_window
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: commands, paths, schemas, symptoms, fold rules
- forbidden_instruction_leaks: default marker, first-home pick, card kind raw
- category_specific_hardness_bar: mill green while ordinary open still emits the retained fold
- category_specific_verifier_risks: test-side rustc, hand card, script mill
- coverage_role: debugging C2 rebuild plus ABI bind

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: sip exits 0 with SEAL while text is still lowercase-only
  why_model_misses_it: agents trust a green mill and named-node mark
  fairness_guardrail: instruction names ordinary vs named mismatch
- mechanism: deceptive_but_valid_local_evidence
  placement: keepnote/DROP.txt
  why_model_misses_it: deleting the retained body makes ordinary bind look new
  fairness_guardrail: compatibility mark must keep the pre-rework fold
- mechanism: cross_file_cross_format_invariants
  placement: shared object vs card.json vs RULES.txt nodes
  why_model_misses_it: hand-written card.json
  fairness_guardrail: verifier reruns sip and mark
- mechanism: stateful_multi_step_dependencies
  placement: stoke.sh after sources
  why_model_misses_it: skip rustc/cc
  fairness_guardrail: ELF required after sources

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert compares ordinary sip text to RULES fold then rebuilds
- shortcut_audit: DROP.txt, hand card, script bin
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
- sidecar_or_protocol_notes: dump fixtures bundled

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs are aliaspit/narbay/vatrib
- gx9_contract_risk: low JSON objects
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan
- verifier_command_visible: draughtpin sip and draughtpin mark
- source_fix_intent_visible: WALK.txt directories
- generated_output_rule_visible: card.json SEAL libdraught.so
- exact_formula_home: RULES.txt plus instruction whitespace rules
- schema_home: instruction.md and RULES.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Rust no_std staticlib whose ordinary open still binds the retained dump fold while a named current node already yields the rework

### realism_source
- source_type: real_bug
- evidence_basis: GNU symbol-version default left on a compatibility node after a library reimplementation, plus a catalog picker that still takes the first home flag
- upstream_or_synthetic_rationale: glibc-style .symver default leftover is a documented ABI footgun
- minimization_preserves: ordinary bind old, named current new, retained body still callable
- synthetic_exception_review: not required

### Failure topology
Operators see sip succeed and mark of the current node print the corrected dump fold, yet an ordinary open of the shared object still emits the retained lowercase-only fold. The mill writes SEAL. A note suggests deleting the retained body.

### Environment shape
Rust mill CLI, no_std staticlib, GNU version script, alias lines, home-node catalog, dump fixtures, decoy drop note, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, stoke rebuild.

### Test plan
- test_vn01_reread_lib
- test_vn02_ws_run
- test_vn03_tail_cut
- test_vn04_json_tag
- test_vn05_void_n
- test_vn06_magic4
- test_vn07_alt_tag
- test_vn08_ghost_id
- test_vn09_fields
- test_vn10_rewait
- test_vn11_old_keep
- test_vn12_min_skip

### Drafting guardrails
Do not name the default marker, first-home catalog walk, or raw kind. Tests must not rustc. Punish DROP.txt via compatibility mark plus rubric.

### Triviality Ledger
- Delete wick_old — blocked by compatibility mark still needing the pre-rework fold.
- Hand-written card.json — blocked by sip rerun and stuffed-card recovery.
- Source-only without stoke — library still binds the retained fold; R5 source_only.sh.
- Script mill replacing ELF — blocked by ELF magic in tests plus ctypes of libdraught.so.

### Per-gate Pitfall Inventory
- RC2: repair paths in WALK.txt name directories, not hue/knit/qat.
- GX9: grade fold strings and kind words, not boolean flags.
- CR8: boot dispatches qat only among fix symbols.
- R5: tests do not stoke; rewait recovery only reruns sip.
- R3: every graded test fails on broken tree.
- P4: DROP.txt decoy punished by rubric.

### Initial Draft Commitments
- environment/cliurn/boot.rs
- environment/vatrib/qat.rs
- environment/narbay/loom.rs
- environment/weft/main.rs
- environment/aliaspit/hue.S
- environment/stemcask/wick.rs
- environment/gluebox/glue.rs
- environment/abifolio/WALK.txt
- environment/abifolio/RULES.txt
- environment/keepnote/DROP.txt
- environment/keepnote/MIN.txt
- environment/rawspan/alpha.raw
- environment/rawspan/beta.raw
- environment/gnuverse/cask.map
- environment/lidmath/note.rs
- environment/lidmath/skip.c
- environment/quarryc/hold.toml
- environment/spanmod/skip.rs
- environment/stoke.sh
- environment/offdebs/wheels
- environment/offdebs/debs
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
- preship/alt_solution.sh

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

- path: environment/aliaspit/hue.S
  symbol: hue
  kind: constant
  signature: hue
  purpose: records .symver lines for fold_frame nodes
- path: environment/narbay/loom.rs
  symbol: knit
  kind: function
  signature: knit() -> String
  purpose: picks a home node name from hold.toml
- path: environment/vatrib/qat.rs
  symbol: qat
  kind: function
  signature: qat(a: &str, b: Option<&str>) -> i32
  purpose: writes card.json and SEAL for sip and mark

#### flipping_point_contract

locations:
  - id: A
    path: environment/aliaspit/hue.S
    controls_tests: [test_vn01_reread_lib, test_vn02_ws_run, test_vn03_tail_cut, test_vn06_magic4]
  - id: B
    path: environment/narbay/loom.rs
    controls_tests: [test_vn04_json_tag, test_vn07_alt_tag, test_vn09_fields, test_vn10_rewait]
  - id: C
    path: environment/vatrib/qat.rs
    controls_tests: [test_vn05_void_n, test_vn08_ghost_id, test_vn11_old_keep, test_vn12_min_skip]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/keepnote/DROP.txt
  kind: config-reader
  rhymes_with: hue
  non_fix_purpose: suggests dropping wick_old from the archive
- path: environment/lidmath/skip.c
  kind: helper
  rhymes_with: qat
  non_fix_purpose: binds wick_new by symbol name for a leftover C probe

#### code_forbidden_tokens

code_forbidden_tokens: [draughtpin, sip, libdraught, dump, inkvat, card.json, mark, slot, RULES, ELF, header, WALK, verifier, library, fold, current, compatibility, SEAL, Whitespace, slash, kind, bare, text, named, ok, zero, Source, Programs, Desk, native]
