### Decision
GO — Attempt 1. Debugging repair: support-kith mill knits a ustar member ledger then emits dual environment reports. Two brief processes flip configuration strings while cluster looks stable. Agent must repair cooperating ledger/overlay/emit loci and rustc-rebuild the ELF.

### Metadata
- version: 2
- Task name: siltcord-kith
- Title: Kith reports disagree
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "ustar", "support-kith", "offset-ledger"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/siltcord quarry` knits `/app/idxbay/members.idx` from `/app/sealwell/kestrel.kith`. Dual `brief` writes `/app/deskjson/pass-a.json` and `/app/deskjson/pass-b.json`.
- A pair of brief invocations parse to the same object.
- Desk keys live in `/app/treenotes/DESK.txt`. Apply order lives in `/app/yarnwell/APPLY.txt`. READY is `brief-ok` on success. Grade time may use `/app/sealwell/vane.kith`.
- Truncated or non-ustar input, or brief archive outside `/app/sealwell`, exits nonzero without READY.
- Pipeline crates named in `/app/treenotes/TREE.txt`. Static or manual desk files are not sufficient. The verifier invokes quarry and brief.

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
- path: environment/idxmill/shard.rs
  role: ledger knit
- path: environment/overlaypit/blend.rs
  role: payload fold
- path: environment/logbag/write.rs
  role: desk emit
- path: environment/siltcli/boot.rs
  role: CLI dispatch

### fix_frontier
- count: 3
- distribution: idxmill, overlaypit, logbag
- naming_policy: opaque rib_a/rib_b/rib_c
- forbidden_stems: siltcord, quarry, brief, timezone
- helpers_policy: keep_head decoy is not a frontier
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON artifacts, exit codes, ELF magic
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: keep_head first sys.conf and skip rebuild

### category_profile
- challenge_family: generated_sequence_drift
- bug_family: generated_sequence_drift
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: pid hash order, max header offset, path alias fold, rustc line
- category_specific_hardness_bar: identical brief plus later payload plus log join
- category_specific_verifier_risks: test-side rustc, hand JSON, script ELF
- coverage_role: debugging C3 prove-twice support kith

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: cluster agrees while timezone flips across processes
  why_model_misses_it: agents trust the internally consistent object
  fairness_guardrail: instruction names the flip
- mechanism: deceptive_but_valid_local_evidence
  placement: keep_head in keeppit plus FLICKER.txt
  why_model_misses_it: first-payload note looks like the fix
  fairness_guardrail: later payload plus log join
- mechanism: cross_file_cross_format_invariants
  placement: ustar vs idx vs json vs READY
  why_model_misses_it: edit json only
  fairness_guardrail: grading reruns quarry and brief
- mechanism: stateful_multi_step_dependencies
  placement: source fix then wick.sh rustc
  why_model_misses_it: skip rebuild
  fairness_guardrail: compiled ELF required after sources

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert reads ustar copies, folds aliases, rustc, quarry+brief twice
- shortcut_audit: keep_head, hand json, script binary, skip wick.sh
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
- sidecar_or_protocol_notes: sealed kestrel kith bundled

### satisfiability_risk
- rc2_planned_name_risk: low — TREE.txt names crates
- gx9_contract_risk: low JSON objects
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan
- verifier_command_visible: siltcord quarry/brief
- source_fix_intent_visible: pipeline crates in TREE.txt
- generated_output_rule_visible: pass-a.json pass-b.json READY
- exact_formula_home: walk_sig SHA-256 of applied names
- schema_home: instruction.md

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Rust ustar support-kith ledger mill

### realism_source
- source_type: synthetic_exception
- evidence_basis: support-bundle collectors that append a second config member after reload; tar last-member overlay
- upstream_or_synthetic_rationale: cannot ship a vendor collector tree
- minimization_preserves: two-process flip, first-copy decoy, skip rebuild
- synthetic_exception_review: keep_head is a realistic decoy

### Failure topology
Operators see two brief processes agree on timezone/cluster/log_events/member_count (UTC, staging, EVT_BOOT, count 2) while walk_sig disagrees. Overlay keeps the earliest sys.conf copy; emit writes walk_sig from a HashMap name bag and READY as ok. keep_head looks like a stability fix. Ledger knit uses a stable name hash and treats a failed scan as an empty ledger.

### Environment shape
Rust CLI, ustar scan, ledger knit, payload fold, desk emit, sealed kith, keep_head decoy, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, rustc wick rebuild.

### Test plan
- test_sc_twice_ident — two brief processes match
- test_sc_walk_hex — walk_sig from archive apply order
- test_sc_idx_recover — quarry rebuilds a corrupt ledger
- test_sc_trunc_exit — truncated input fails
- test_sc_cfg_string — later timezone
- test_sc_later_group — later cluster
- test_sc_event_join — both log lines
- test_sc_count_reg — regular-file count
- test_sc_guard_line — READY brief-ok
- test_sc_path_reject — outside sealwell
- test_sc_schema_keys — required keys
- test_sc_sig_len — 64 hex walk_sig

### Drafting guardrails
Do not name pid hash, max header offset, or path alias. Tests must not rustc. Punish keep_head via later payload plus rubric.

### Triviality Ledger
- keep_head first sys.conf — later payload plus log join still fail.
- Name-sort of members — stable brief but wrong walk_sig.
- Hand-written JSON — recovery reruns quarry+brief; ELF assert.
- Source-only without wick.sh — ELF still wrong; R5.
- Script replacement of the binary — ELF magic.

### Per-gate Pitfall Inventory
- RC2: TREE.txt names crates, not rib_a.
- GX9: grade parsed objects, not boolean flags.
- CR8: quarry calls rib_a; slate calls rib_b and rib_c.
- R5: tests do not wick.sh; recovery only reruns quarry/brief.
- R3: every graded test fails on broken tree.
- GX3: oracle replaces three modules with substantive bodies.
- CR1: symbol_table rib_a/rib_b/rib_c only.

### Initial Draft Commitments
- environment/siltcli/boot.rs
- environment/siltcli/quarry.rs
- environment/siltcli/slate.rs
- environment/siltcli/usage.txt
- environment/idxmill/shard.rs
- environment/ustarwalk/hdr.rs
- environment/overlaypit/blend.rs
- environment/cfgbag/alias.rs
- environment/logbag/write.rs
- environment/keeppit/first.rs
- environment/pidhash/seed.rs
- environment/paxcue/long.rs
- environment/offseturn/rank.rs
- environment/cfgbag/kv.rs
- environment/ustarwalk/block.rs
- environment/treenotes/TREE.txt
- environment/treenotes/USTAR.txt
- environment/treenotes/FLICKER.txt
- environment/sealwell/kestrel.kith
- environment/idxbay/README.txt
- environment/wick.sh
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

- path: environment/idxmill/shard.rs
  symbol: rib_a
  kind: function
  signature: rib_a(a: &str, b: &str) -> i32
  purpose: writes the member ledger
- path: environment/overlaypit/blend.rs
  symbol: rib_b
  kind: function
  signature: rib_b(a: &str, b: &str) -> Result<Pack, i32>
  purpose: folds payloads into a pack
- path: environment/logbag/write.rs
  symbol: rib_c
  kind: function
  signature: rib_c(p: &Pack, out: &str, a: &str) -> i32
  purpose: writes the desk object

#### flipping_point_contract

locations:
  - id: A
    path: environment/idxmill/shard.rs
    controls_tests: [test_sc_twice_ident, test_sc_walk_hex, test_sc_idx_recover, test_sc_trunc_exit]
  - id: B
    path: environment/overlaypit/blend.rs
    controls_tests: [test_sc_cfg_string, test_sc_later_group, test_sc_event_join, test_sc_count_reg]
  - id: C
    path: environment/logbag/write.rs
    controls_tests: [test_sc_guard_line, test_sc_path_reject, test_sc_schema_keys, test_sc_sig_len]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/keeppit/first.rs
  kind: helper
  rhymes_with: rib_b
  non_fix_purpose: keeps the first sys.conf payload

#### code_forbidden_tokens

code_forbidden_tokens: [siltcord, quarry, brief, idxbay, sealwell, kestrel, deskjson, timezone, cluster, walk_sig, treenotes, ustar, log_events, member_count, source_kith]
