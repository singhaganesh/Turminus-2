### Decision
GO — Attempt 1. Debugging repair: crash-upload mill bakes a sequence ribbon from a CLAT spool. Two mints permute `seq` while checksums and batch count stay green. Agent must repair cooperating walk/clock/group loci and rustc-rebuild the ELF.

### Metadata
- version: 2
- Task name: brinewell-clatter
- Title: Spool sequence permutes
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "minidump", "upload-manifest", "crash-timeline"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/clatter` is a compiled ELF. `tallow` then `pour` write `/app/kegbay/upload.json` and `/app/kegbay/batch.tsv`.
- Two process mints on unchanged `/app/dropwell` are byte-identical.
- Shared names keep last-good relative crash order; seq is 1..n for the current well. Last-good absent still follows dump crash chronology. Extra dumps stay beside their crash. MARK is absent on empty/outside failure.
- Every dropwell file appears once. `digest` is lowercase hex SHA-256 of the dump.
- `batch_count` is ceil(n/3). JSON/TSV schemas as in instruction. `MARK` is `ok` on success.
- Empty well or `pour` outside `/app/dropwell` exits nonzero without `MARK`.
- Source modules named in `/app/opsheet/ROUTE.txt`. Hand-written keg files are not enough. Verifier reruns `tallow` then `pour`.

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
- path: environment/walk.rs
  role: spool walk
- path: environment/stamp.rs
  role: per-dump clock key
- path: environment/fold.rs
  role: guid grouping
- path: environment/deskbin/main.rs
  role: CLI dispatch
- path: environment/fat.sh
  role: rustc rebuild glue; not a named frontier

### fix_frontier
- count: 3
- distribution: walk.rs, stamp.rs, fold.rs
- naming_policy: opaque rib_a/rib_b/rib_c
- forbidden_stems: clatter, seq, dump, guid
- helpers_policy: dropwalk mtime decoy is not a frontier; fat.sh is rebuild glue, not a named fix symbol; deskbin parse/sum/pipe/emit/main are co-resident CLI helpers
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON/TSV artifacts, exit codes, ELF magic
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: sort by mtime or by filename and call the mill twice

### category_profile
- challenge_family: generated_sequence_drift
- bug_family: generated_sequence_drift
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, schemas, symptoms, last-good recording
- forbidden_instruction_leaks: HashMap walk, FILETIME dword order, guid inherit, rustc line
- category_specific_hardness_bar: identical mint plus chronology vs last-good plus companions listed
- category_specific_verifier_risks: test-side rustc, hand keg files, script ELF
- coverage_role: debugging C3 prove-twice crash upload

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: checksums and batch_count stay correct while seq permutes
  why_model_misses_it: agents trust matching digests
  fairness_guardrail: instruction names permutation vs last-good
- mechanism: deceptive_but_valid_local_evidence
  placement: mtime sort already in dropwalk; header write_stamp tied
  why_model_misses_it: newest-mtime note looks like the fix
  fairness_guardrail: holdout dump plus last-good
- mechanism: cross_file_cross_format_invariants
  placement: CLAT streams vs ribbon vs json vs tsv vs last-good
  why_model_misses_it: edit json only
  fairness_guardrail: verifier reruns tallow and pour
- mechanism: stateful_multi_step_dependencies
  placement: source fix then fat.sh rustc
  why_model_misses_it: skip rebuild
  fairness_guardrail: compiled ELF required after sources

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert decodes CLAT clocks, groups guid, rustc, tallow+pour twice
- shortcut_audit: mtime sort, hand json, script binary, skip fat.sh
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
- sidecar_or_protocol_notes: CLAT dumps and last-good bundled

### satisfiability_risk
- rc2_planned_name_risk: low — walk in deskbin, stamp and fold at /app
- gx9_contract_risk: low JSON objects
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema plus FORMAT.txt

### actionability_plan
- verifier_command_visible: clatter tallow/pour
- source_fix_intent_visible: pipeline modules in ROUTE.txt
- generated_output_rule_visible: upload.json batch.tsv MARK
- exact_formula_home: digest SHA-256; batch_count ceil n/3
- schema_home: instruction.md and FORMAT.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Rust crash-spool sequencer that bakes a ribbon from CLAT streams

### realism_source
- source_type: synthetic_exception
- evidence_basis: Breakpad/Crashpad minidump TimeDateStamp vs FILETIME plus readdir upload manifests
- upstream_or_synthetic_rationale: cannot ship a private crash-server tree
- minimization_preserves: green checksums, permuted seq, mtime ties, skip rebuild
- synthetic_exception_review: mtime sort is a realistic decoy

### Failure topology
Operators see matching dumps and checksums with a stable batch count while sequence numbers permute across mints and disagree with the archived server recording. Walk drops dumps that lack an exception stream, the clock key uses swapped FILETIME dwords mixed with unix write stamps, and grouping never inherits a companion's key from its guid primary. Sorting by mtime is a no-op because the burst shares one stamp.

### Environment shape
Rust CLI, spool walk, clock key, guid fold, CLAT well, last-good recording, mtime decoy, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, rustc fat rebuild.

### Test plan
- test_bw01_repeat_pair
- test_bw02_arc_order
- test_bw03_pair_adj
- test_bw04_hold_extra
- test_bw05_empty_exit
- test_bw06_outside_exit
- test_bw07_schema_rows
- test_bw08_tsv_rows
- test_bw09_hex_body
- test_bw10_k_split
- test_bw11_zz_regen
- test_bw12_one_shot
- test_bw13_flag_gone
- test_bw14_seed_hide

### Drafting guardrails
Do not name HashMap, FILETIME, dword, or guid inherit. Tests must not rustc. Punish mtime sort via last-good plus holdout plus rubric.

### Triviality Ledger
- Sort by mtime — all stamps tied; last-good and holdout still fail.
- Filename sort — stable mint but wrong chronology.
- Hand-written keg — zz regen reruns tallow+pour.
- Source-only without fat.sh — ELF still wrong; R5.
- Script replacement of the binary — ELF magic and one-shot subprocess.

### Per-gate Pitfall Inventory
- RC2: repair paths in ROUTE.txt name directories, not rib_a.
- GX9: grade seq/name/digest, not boolean flags.
- CR8: pipe calls walk+stamp; emit calls fold.
- R5: tests do not fat.sh; zz recovery only reruns tallow/pour.
- R3: every graded test fails on broken tree.
- P4: MTIME_NOTE decoy punished by rubric.

### Initial Draft Commitments
- environment/walk.rs
- environment/stamp.rs
- environment/fold.rs
- environment/deskbin/main.rs
- environment/deskbin/parse.rs
- environment/deskbin/sum.rs
- environment/deskbin/pipe.rs
- environment/deskbin/emit.rs
- environment/dropwalk/mtime.rs
- environment/fat.sh
- environment/opsheet/ROUTE.txt
- environment/opsheet/FORMAT.txt
- environment/opsheet/MTIME_NOTE.txt
- environment/dropwell/*.clat
- environment/tidearc/lastgood.rec
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

- path: environment/walk.rs
  symbol: rib_a
  kind: function
  signature: rib_a() -> Result<Vec<String>, i32>
  purpose: lists spool paths
- path: environment/stamp.rs
  symbol: rib_b
  kind: function
  signature: rib_b(names: &[String]) -> Vec<(String, u64)>
  purpose: clock key per path
- path: environment/fold.rs
  symbol: rib_c
  kind: function
  signature: rib_c(pairs: &[(String, u64)], root: Option<&str>) -> Result<Vec<String>, i32>
  purpose: ordered names for the ribbon

#### flipping_point_contract

locations:
  - id: A
    path: environment/walk.rs
    controls_tests: [test_bw03_pair_adj, test_bw05_empty_exit, test_bw07_schema_rows, test_bw11_zz_regen, test_bw13_flag_gone]
  - id: B
    path: environment/stamp.rs
    controls_tests: [test_bw02_arc_order, test_bw04_hold_extra, test_bw09_hex_body, test_bw10_k_split, test_bw14_seed_hide]
  - id: C
    path: environment/fold.rs
    controls_tests: [test_bw01_repeat_pair, test_bw06_outside_exit, test_bw08_tsv_rows, test_bw12_one_shot]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/dropwalk/mtime.rs
  kind: helper
  rhymes_with: rib_a
  non_fix_purpose: sorts paths by mtime for a side listing

#### code_forbidden_tokens

code_forbidden_tokens: [clatter, dropwell, kegbay, tallow, pour, tidearc, lastgood, opsheet, digest, guid]
