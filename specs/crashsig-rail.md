### Decision
GO — Attempt 1. Debugging repair where tablegen skips rewriting a truncated routing map; router import failure falls back to platform-core; agent must compile after fixing guard.

### Metadata
- version: 2
- Task name: crashsig-rail
- Title: Partial output fails to import
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["python", "bash"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["routing", "crash-sigs", "relaydesk", "tablegen"]
- Milestones: 0

## Authoring Brief

### Triviality Ledger
- Hand-editing routing_map.py without tablegen fix leaves guard returning False on parse failure.
- compile exits zero while skipping write on unparseable map.
- file_present probe passes on broken tree but route falls back to default.
- Loader logging decoy documents import failure without restoring table routing.

### Per-gate Pitfall Inventory
- RC2: repair paths in ops_notes generically name codemill, not guard.py.
- GX9: grade route JSON team/source, not boolean answer keys.
- R5: tests do not invoke compile; agent must compile after source repair.
- R3: every graded test fails on broken tree.
- P4: file_present probe decoy punished by rubric and routing tests.

### Initial Draft Commitments
- environment/codemill/tablegen/guard.py — skip emit when parse fails
- environment/relaydesk/gen/routing_map.py — truncated generated map
- environment/relaydesk/switchboard/load_map.py — import catch returns empty map
- environment/faultdata/roster.toml — ownership roster
- environment/relaydesk/probes/file_present.py — decoy smoke
- tests/test_outputs.py — route JSON, map import, guard behavior

### Public contract
- `/app/bin/crashrail compile` rebuilds `/app/relaydesk/gen/routing_map.py` from `/app/faultdata/roster.toml`.
- `/app/bin/crashrail route --signature <SIG>` prints JSON with `team` and `source`.
- `SIG_NULL_DEREF_81c2` routes to `graphics-guild` with `source: table`.
- Every roster signature in generated map; map imports cleanly.
- Default fallback exits non-zero.
- Agent must compile after source fixes; verifier does not re-compile.

### platform_files
- path: task.toml
  role: metadata; allow_internet false
- path: instruction.md
  role: public prompt
- path: output_contract.toml
  role: local contract
- path: tests/test.sh
  role: verifier entry
- path: tests/test_outputs.py
  role: behavioral tests
- path: solution/solve.sh
  role: oracle
- path: environment/Dockerfile
  role: offline gcc+python image
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/codemill/tablegen/guard.py
  role: emit skip gate
- path: environment/codemill/tablegen/publish.py
  role: map writer
- path: environment/relaydesk/gen/routing_map.py
  role: truncated artifact
- path: environment/relaydesk/switchboard/load_map.py
  role: import loader
- path: environment/relaydesk/switchboard/direct.py
  role: route logic
- path: environment/faultdata/roster.toml
  role: roster input
- path: environment/relaydesk/probes/file_present.py
  role: decoy probe

### fix_frontier
- count: 14
- distribution: codemill tablegen guard
- naming_policy: opaque tablegen internals
- forbidden_stems: guard, diff, parse
- helpers_policy: publish, roster_read, ast_read are co-resident helpers
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: route JSON, import parse, guard callable
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: logging-only loader patch or hand-written map without guard fix

### category_profile
- challenge_family: codegen_skip_on_parse_failure
- profile_name: crash_routing_ownership
- allowed_instruction_disclosures: commands, paths, route JSON schema, roster anchor sig
- forbidden_instruction_leaks: guard return value, parse failure branch
- category_specific_hardness_bar: compile success with skipped write
- category_specific_verifier_risks: probe-only green, test-side compile
- coverage_role: debugging rebuild-before-claim

### satisfiability_risk
- rc2_planned_name_risk: low
- gx9_contract_risk: low json fields
- cr1_symbol_frontier_risk: low single locus
- hidden_contract_risk: low public route schema

### actionability_plan
- verifier_command_visible: crashrail compile/route
- source_fix_intent_visible: codemill tablegen pipeline
- generated_output_rule_visible: compile rebuilds routing_map.py
- exact_formula_home: instruction route JSON
- schema_home: roster.toml ids and owners

### waiver_plan
- waivers_expected: false
- waiver_rationale: none

### reference_pattern
- justification_if_none: no promoted reference for tablegen skip-on-parse crash routing

### realism_source
- source_type: synthetic_exception
- evidence_basis: interrupted codegen leaving truncated module; skip-if-unchanged treating parse error as noop
- upstream_or_synthetic_rationale: mirrors ownership table regen pipelines
- minimization_preserves: silent default routing on import failure
- synthetic_exception_review: plausible engineer mistake in diff gate

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: all local deterministic
- mechanism: false_green_intermediate_states
  placement: compile exits zero while skipping rewrite
  why_model_misses_it: agents trust compile success
  fairness_guardrail: instruction names route fallback symptom
- mechanism: deceptive_but_valid_local_evidence
  placement: file_present probe sees non-empty map file
  why_model_misses_it: file exists on disk
  fairness_guardrail: route JSON proves table import
- mechanism: cross_file_cross_format_invariants
  placement: truncated map vs roster rows vs route answers
  why_model_misses_it: focuses on loader not tablegen
  fairness_guardrail: roster ids must appear in map
- mechanism: stateful_multi_step_dependencies
  placement: guard fix then agent-run compile
  why_model_misses_it: hand-written map shortcut
  fairness_guardrail: instruction requires compile before grading

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert fixes guard then compile
- shortcut_audit: loader logging, hand-written map, probe-only, compile without guard fix
- ablation_plan: drop guard behavior test and difficulty collapses
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
- sidecar_or_protocol_notes: roster bundled read-only

### Failure topology
Operators see compile succeed while every signature routes to platform-core with source default because the generated map is truncated and tablegen skips rewriting unparseable files. The switchboard catches import failure and serves the default team without surfacing a hard compile error.

### Environment shape
Python relaydesk switchboard with codemill tablegen, TOML roster, truncated routing_map artifact, file_present decoy probe, gcc runtime image with offline pytest.

### Test plan
- test_generated_artifact_imports
- test_manifest_ids_in_table
- test_owner_pairs_match_table
- test_refresh_gate_on_bad_artifact
- test_anchor_sig_team_table
- test_hold_sig_team_table
- test_io_sig_team_table
- test_auth_sig_team_table
- test_net_sig_team_table
- test_manifest_sigs_exit_zero
- test_unknown_sig_fallback_exit
- test_probe_green_route_still_wrong
- test_table_row_count_matches_manifest

### Drafting guardrails
Do not name guard return branch in instruction. Tests must not call compile. Punish loader logging decoy via rubric.

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table
- path: environment/codemill/tablegen/guard.py
  symbol: should_emit
  kind: function
  signature: should_emit(path: Path, fresh_body: str) -> bool
  purpose: decide whether to rewrite routing map
- path: environment/codemill/tablegen/publish.py
  symbol: emit_map
  kind: function
  signature: emit_map(path: Path | None = None) -> bool
  purpose: render roster into routing_map.py
- path: environment/codemill/tablegen/roster_read.py
  symbol: load_pairs
  kind: function
  signature: load_pairs(path: Path | None = None) -> list[tuple[str, str]]
  purpose: co-resident roster loader helper
- path: environment/codemill/tablegen/ast_read.py
  symbol: read_map_literal
  kind: function
  signature: read_map_literal(text: str) -> Dict[str, str]
  purpose: co-resident parse helper
- path: environment/codemill/tablegen/driver.py
  symbol: run_tablegen
  kind: function
  signature: run_tablegen() -> int
  purpose: co-resident compile driver helper
- path: environment/relaydesk/switchboard/load_map.py
  symbol: fetch_map
  kind: function
  signature: fetch_map() -> Dict[str, str]
  purpose: co-resident import helper
- path: environment/relaydesk/switchboard/direct.py
  symbol: normalize
  kind: function
  signature: normalize(sig: str) -> str
  purpose: co-resident signature normalizer
- path: environment/relaydesk/switchboard/direct.py
  symbol: direct
  kind: function
  signature: direct(sig: str) -> tuple[str, str]
  purpose: route signature to team and source
- path: environment/codemill/tablegen/publish.py
  symbol: build_source
  kind: function
  signature: build_source(rows: list[tuple[str, str]]) -> str
  purpose: co-resident render helper
- path: environment/relaydesk/cli_entry.py
  symbol: main
  kind: function
  signature: main(argv: list[str] | None = None) -> int
  purpose: co-resident CLI helper
- path: environment/signkit/schema.py
  symbol: OwnershipRow
  kind: class
  signature: OwnershipRow(signature: str, team: str)
  purpose: co-resident roster row type
- path: environment/signkit/schema.py
  symbol: row_from_mapping
  kind: function
  signature: row_from_mapping(raw: dict) -> OwnershipRow
  purpose: co-resident schema helper
- path: environment/signkit/normalize.py
  symbol: canonical
  kind: function
  signature: canonical(sig: str) -> str
  purpose: co-resident normalize helper
- path: environment/relaydesk/probes/file_present.py
  symbol: main
  kind: function
  signature: main() -> int
  purpose: decoy probe helper

#### flipping_point_contract
locations:
  - id: A
    path: environment/codemill/tablegen/guard.py
    controls_tests: [test_refresh_gate_on_bad_artifact, test_anchor_sig_team_table]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest
- path: environment/relaydesk/probes/file_present.py
  kind: helper
  rhymes_with: compile success
  non_fix_purpose: checks map file exists only

#### code_forbidden_tokens
code_forbidden_tokens: [graphics-guild, platform-core, SIG_NULL_DEREF_81c2, memory-squad]
