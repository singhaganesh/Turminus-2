### Decision
GO — Attempt 1. Debugging repair: time-partition snapshot mill plus a compiled clasp path. Ledger and rehearsal stay green while the newest populated calendar file is absent from the unpack. Three loci: day window, baked check kind, last-shard unpack.

### Metadata
- version: 2
- Task name: dewkiln-hopper
- Title: Newest day missing from unpack
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "snapshot-mill", "partition-window", "rehearsal-check"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/dewkiln` is a compiled ELF. A script or interpreter is not enough.
- `clasp` loads `/app/daywell`, writes `/app/bloturn/ledger.json` and `/app/bloturn/check.json`, packs `/app/packbay/stage`, unpacks `/app/packbay/latest`.
- After `clasp`, the most recently populated calendar file's restored row count equals a count from `/app/daywell` that does not read `ledger.json`.
- `check.json` has `probe`, `matched`, `taken`. `probe` is the string `live`. `matched` and `taken` equal the live daywell row total at or before the wall.
- A check that never opened `/app/daywell` must exit non-zero and must not write `/app/bloturn/GUARD`.
- Success writes GUARD containing `ok`.
- Empty `/app/daywell` exits non-zero with GUARD absent.
- Day files are `dYYYYMMDD.tbl`. Wall integer is `/app/opstext/WALL`.
- Source fixes under `/app`; crates named in `/app/opstext/LIST.txt`.
- Hand-written ledger or check files are not enough. Verifier reruns `/app/bin/dewkiln clasp`.

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
- path: environment/hopcue/rim.rs
  role: day window pick
- path: environment/millrib/gait.rs
  role: check kind
- path: environment/restpit/soak.rs
  role: unpack walk

### fix_frontier
- count: 3
- distribution: hopcue, millrib, restpit
- naming_policy: opaque rim gait soak
- forbidden_stems: clasp, probe, live, ledger, snapshot
- helpers_policy: corkpit/floor.rs decoy off frontier
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON probe strings, row counts, exit codes
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: raise floorcue minimum so a truncated pack still looks green

### category_profile
- challenge_family: false_green_rehearsal_window
- bug_family: false_green_rehearsal_window
- profile_name: filesystem_state_reconstruction
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: exclusive wall day, ledger-only check kind, drop-last unpack
- category_specific_hardness_bar: clasp green while newest calendar file absent from unpack
- category_specific_verifier_risks: test-side rustc, hand ledger, script mill
- coverage_role: debugging C1 end-to-end plus C2 rebuild

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: clasp exits 0 with a non-empty ledger while newest day is missing
  why_model_misses_it: agents trust ledger totals
  fairness_guardrail: instruction names the missing newest day
- mechanism: deceptive_but_valid_local_evidence
  placement: floorcue/MIN.txt CI floor
  why_model_misses_it: truncated taken still clears the floor
  fairness_guardrail: probe must be live and newest day rows must match daywell
- mechanism: cross_file_cross_format_invariants
  placement: daywell vs stage pack vs latest unpack vs check.json
  why_model_misses_it: edit check.json only
  fairness_guardrail: verifier reruns clasp
- mechanism: stateful_multi_step_dependencies
  placement: source fix then wick.sh
  why_model_misses_it: skip rustc
  fairness_guardrail: ELF required after sources

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert compares newest daywell file to packbay/latest then rebuilds
- shortcut_audit: MIN.txt floor, hand ledger, script bin
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
- sidecar_or_protocol_notes: daywell fixtures bundled

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs are hopcue/millrib/restpit
- gx9_contract_risk: low JSON objects
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan
- verifier_command_visible: dewkiln clasp
- source_fix_intent_visible: pipeline crates in LIST.txt
- generated_output_rule_visible: ledger.json check.json packbay/latest GUARD
- exact_formula_home: newest restored count equals daywell count
- schema_home: instruction.md and LIST.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Rust snapshot mill whose rehearsal check stays green while the newest populated calendar file is dropped from the unpack

### realism_source
- source_type: synthetic_exception
- evidence_basis: backup tools that skip the current partition as if it were future, plus CI defaulting verify to manifest presence
- upstream_or_synthetic_rationale: cannot ship a vendor warehouse dump appliance
- minimization_preserves: clasp green, newest day missing, skip rebuild
- synthetic_exception_review: MIN.txt floor is a realistic decoy

### Failure topology
Operators see clasp succeed after every scheduled run, yet unpack of packbay/latest is missing the most recently populated calendar file. The ledger total matches whatever days were packed. The compiled check kind only confirms the ledger is non-empty. Unpack also drops the last packed shard as if it were an open buffer.

### Environment shape
Rust clasp CLI, day window crate, check-kind crate, unpack crate, daywell fixtures, decoy floor note, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, rustc wick rebuild.

### Test plan
- test_dk01_twice_blob
- test_dk02_held_extra
- test_dk03_cur_pack
- test_dk04_kind_word
- test_dk05_solo_today
- test_dk06_hdr_magic
- test_dk07_stamp_text
- test_dk08_ahead_omit
- test_dk09_keys_obj
- test_dk10_zz_corrupt
- test_dk11_once_pass
- test_dk12_floor_ignored

### Drafting guardrails
Do not name exclusive wall bounds, ledger-only kind, or drop-last unpack. Tests must not rustc. Punish MIN.txt floor via live newest-day counts plus rubric.

### Triviality Ledger
- Raise floorcue minimum — blocked by probe live and newest-day daywell parity.
- Hand-written ledger.json — blocked by clasp rerun and corrupt-then-clasp recovery.
- Source-only without wick — binary still drops the newest day; R5 source_only.sh.
- Script mill replacing ELF — blocked by ELF magic in tests.

### Per-gate Pitfall Inventory
- RC2: repair paths in LIST.txt name directories, not rim/gait/soak.
- GX9: grade probe strings and row counts, not boolean flags.
- CR8: fold wraps rim+soak; boot dispatches fold then gait.
- R5: tests do not wick; zz recovery only reruns clasp.
- R3: every graded test fails on broken tree.
- P4: floorcue/MIN.txt decoy punished by rubric.

### Initial Draft Commitments
- environment/wickmill/boot.rs
- environment/wickmill/usage.txt
- environment/hopcue/rim.rs
- environment/millrib/gait.rs
- environment/millrib/sheet.tpl
- environment/restpit/soak.rs
- environment/shardfold/read.rs
- environment/urncue/fold.rs
- environment/corkpit/floor.rs
- environment/corkpit/NOTE.txt
- environment/lidcue/skip.rs
- environment/opstext/LIST.txt
- environment/opstext/WALL
- environment/opstext/SHIFT.txt
- environment/floorcue/MIN.txt
- environment/daywell/d20260910.tbl
- environment/daywell/d20260911.tbl
- environment/daywell/d20260912.tbl
- environment/daywell/d20260913.tbl
- environment/seed/daywell/d20260910.tbl
- environment/seed/daywell/d20260911.tbl
- environment/seed/daywell/d20260912.tbl
- environment/seed/daywell/d20260913.tbl
- environment/wick.sh
- environment/siltbin/wheels
- environment/siltbin/debs
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

- path: environment/hopcue/rim.rs
  symbol: rim
  kind: function
  signature: rim(a: i32, b: Vec<(i32, String)>) -> Vec<(i32, String)>
  purpose: filters calendar files against the wall integer
- path: environment/millrib/gait.rs
  symbol: gait
  kind: function
  signature: gait(a: i32, b: &[(i32, String)]) -> i32
  purpose: writes check.json and GUARD
- path: environment/restpit/soak.rs
  symbol: soak
  kind: function
  signature: soak(a: &[(i32, String)], b: &str) -> Result<(), i32>
  purpose: copies packed shards into latest

#### flipping_point_contract

locations:
  - id: A
    path: environment/hopcue/rim.rs
    controls_tests: [test_dk02_held_extra, test_dk03_cur_pack, test_dk05_solo_today, test_dk08_ahead_omit]
  - id: B
    path: environment/millrib/gait.rs
    controls_tests: [test_dk04_kind_word, test_dk07_stamp_text, test_dk09_keys_obj, test_dk12_floor_ignored]
  - id: C
    path: environment/restpit/soak.rs
    controls_tests: [test_dk01_twice_blob, test_dk06_hdr_magic, test_dk10_zz_corrupt, test_dk11_once_pass]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/corkpit/floor.rs
  kind: helper
  rhymes_with: gait
  non_fix_purpose: compares taken against floorcue/MIN.txt
- path: environment/lidcue/skip.rs
  kind: helper
  rhymes_with: rim
  non_fix_purpose: sorts packed path strings when operators dump a name-order view

#### code_forbidden_tokens

code_forbidden_tokens: [dewkiln, clasp, daywell, bloturn, ledger.json, check.json, packbay, latest, pipeline, crates, opstext, LIST.txt, script, interpreter, ledger, verifier, rows, row, count, probe, matched, taken, live, GUARD, ok, wall, WALL, snapshot, desk, native, ELF]
