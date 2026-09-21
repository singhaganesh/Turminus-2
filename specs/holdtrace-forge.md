### Decision
GO — Attempt 2. Debugging repair of a spec-driven forge where writer and corpus regenerate but consume template lags; held-out archive trace; agent must forge before grading.

### Metadata
- version: 2
- Task name: holdtrace-forge
- Title: Both sides from one spec
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["python"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["python", "codegen", "binary-traces", "forge"]
- Milestones: 0

## Authoring Brief

### Triviality Ledger
- Hand-editing runtime ingest module is wiped when agent reruns forge; template and driver fixes required.
- Regenerating corpus alone leaves archive undecodable and emit/consume magic misaligned.
- Corpus size smoke passes on broken tree but decode tests fail on archive and corpus.
- Layout-only hardcode of pkgc/rdr.tpl without pkga/pkgb fixes still fails source inspection tests.

### Per-gate Pitfall Inventory
- RC2: forge repair paths live in layout notes, not instruction nouns.
- GX9: grade decode JSON and magic agreement, not boolean answer keys.
- R5: tests do not invoke forge; agent must forge after source repair.
- R3: every graded test fails on broken tree without agent forge.
- P4: corpus_len smoke decoy punished by rubric and size_probe test.

### Initial Draft Commitments
- environment/pkgc/rdr.tpl — stale consume template with substitution slots
- environment/pkgb/sync.py — copies consume template without rendering
- environment/pkga/vars.py — schema context missing legacy_magic
- environment/pkgc/wrt.tpl — schema-driven emit template
- environment/archive/deployed/lane_ops.trc — held-out legacy trace
- environment/tracekit/smoke/corpus_len.py — decoy smoke
- environment/tracekit/notes/layout.txt — absolute forge repair paths
- tests/test_outputs.py — archive decode, round-trip, magic agreement, pkga/pkgb source checks

### Public contract
- `/app/bin/holdtrace forge` regenerates runtime modules and corpus from `/app/tracekit/schema/span.json`.
- `/app/bin/holdtrace decode` prints JSON with event, lane_id, grams or error bad_trace.
- Archive `/app/archive/deployed/lane_ops.trc` must decode to lane_open / 7 / 1250.
- Fresh record round-trip and emit/consume magic agreement required.
- Forge repair paths listed in `/app/tracekit/notes/layout.txt`.
- Agent must run forge after source fixes; verifier does not re-forge.

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
  role: offline image
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/pkgb/sync.py
  role: forge orchestration
- path: environment/pkgc/rdr.tpl
  role: stale consume template
- path: environment/pkgc/wrt.tpl
  role: emit template
- path: environment/pkga/vars.py
  role: schema context builder
- path: environment/pkgb/step_b.py
  role: schema loader helper
- path: environment/tracekit/corpus/refresh.py
  role: corpus refresh helper
- path: environment/tracekit/runtime/pack.py
  role: wire helpers
- path: environment/archive/deployed/lane_ops.trc
  role: held-out archive
- path: environment/tracekit/smoke/corpus_len.py
  role: decoy smoke
- path: environment/tracekit/notes/layout.txt
  role: forge repair path index

### fix_frontier
- count: 3
- distribution: pkga context, pkgb driver render path, pkgc consume template
- naming_policy: opaque forge internals
- forbidden_stems: spec, generator, template
- helpers_policy: step_b, refresh_pool, and render_tpl are co-resident helpers declared in symbol_table
- symbol_thin_preferred: false

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: decode JSON, magic bytes, round-trip, source inspection
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: corpus-only regen or runtime hand-edit or layout-only hardcode

### category_profile
- challenge_family: codegen_fixture_divergence
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, wire layout, archive fields, layout notes
- forbidden_instruction_leaks: stale constant location, oracle patch recipe
- category_specific_hardness_bar: archive outside generator corpus
- category_specific_verifier_risks: smoke-only green path, test-side auto-forge
- coverage_role: debugging rebuild-before-claim

### satisfiability_risk
- rc2_planned_name_risk: low
- gx9_contract_risk: low json fields
- cr1_symbol_frontier_risk: low
- hidden_contract_risk: low public wire format

### actionability_plan
- verifier_command_visible: holdtrace forge/decode/record
- source_fix_intent_visible: layout notes name forge sources
- generated_output_rule_visible: forge regenerates runtime and corpus
- exact_formula_home: instruction wire layout
- schema_home: span.json fields in instruction

### waiver_plan
- waivers_expected: false
- waiver_rationale: none

### reference_pattern
- justification_if_none: no promoted reference for codegen emit-consume holdout pattern

### realism_source
- source_type: synthetic_exception
- evidence_basis: common spec drift between generated emit/consume pairs
- upstream_or_synthetic_rationale: mirrors real forge pipelines with stale templates
- minimization_preserves: cancel-out on generated corpus vs independent archive
- synthetic_exception_review: stale template is plausible engineer mistake

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: all local deterministic
- mechanism: false_green_intermediate_states
  placement: corpus smoke passes while archive fails
  why_model_misses_it: agents trust local smoke
  fairness_guardrail: instruction names archive path
- mechanism: deceptive_but_valid_local_evidence
  placement: corpus regenerated with emit module
  why_model_misses_it: corpus bytes look current
  fairness_guardrail: archive is separate path
- mechanism: cross_file_cross_format_invariants
  placement: emit HLT2 vs consume HLT1 vs archive HLT1
  why_model_misses_it: partial template edit
  fairness_guardrail: magic rules in instruction
- mechanism: stateful_multi_step_dependencies
  placement: template fix then agent-run forge
  why_model_misses_it: runtime-only patch
  fairness_guardrail: instruction requires forge before grading

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert syncs consume template then forge
- shortcut_audit: corpus regen, runtime hand-edit, smoke-only, layout-only
- ablation_plan: drop archive test and difficulty collapses
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
- sidecar_or_protocol_notes: archive bundled read-only

### Failure topology
Operators see green corpus smoke while deployment archive traces fail decode after a schema header revision. The emit module and corpus regenerate from the updated schema but the consume template stayed on the prior wire assumptions, so generated fixtures and the emit side agree while independent archived bytes do not.

### Environment shape
Python forge with JSON schema, substitution templates under pkga/pkgb/pkgc, generated runtime modules, regression corpus, smoke helper decoy, layout notes with repair paths, and a read-only archive tree outside the generator output path.

### Test plan
- test_span_ctx_exports_legacy_magic
- test_forge_renders_consume_template
- test_vault_payload_fields
- test_live_emit_roundtrip
- test_pipeline_magic_alignment
- test_pool_samples_decode
- test_size_probe_insufficient
- test_junk_rejected_valid_persists
- test_first_sample_fields
- test_second_sample_fields
- test_name_width_sixteen
- test_emit_nonempty_blob
- test_revision_tag_two

### Drafting guardrails
Do not name stale magic constant in instruction. Do not mention pytest or verifier forge rerun. Keep archive fields in instruction for GX9 grounding. Tests must not call forge.

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table
- path: environment/pkgc/rdr.tpl
  symbol: ingest_blob
  kind: function
  signature: ingest_blob(blob: bytes) -> tuple[int, str, int]
  purpose: decode wire bytes to lane, event, grams
- path: environment/pkgb/sync.py
  symbol: emit_runtime
  kind: function
  signature: emit_runtime() -> None
  purpose: render templates and refresh corpus
- path: environment/pkga/vars.py
  symbol: span_ctx
  kind: function
  signature: span_ctx(schema: dict) -> dict
  purpose: build substitution context from schema
- path: environment/pkgb/render.py
  symbol: render_tpl
  kind: function
  signature: render_tpl(name: str, ctx: dict) -> str
  purpose: substitute template placeholders

#### flipping_point_contract
locations:
  - id: A
    path: environment/pkgc/rdr.tpl
    controls_tests: [test_vault_payload_fields, test_name_width_sixteen]
  - id: B
    path: environment/pkgb/sync.py
    controls_tests: [test_pipeline_magic_alignment, test_pool_samples_decode]
  - id: C
    path: environment/pkga/vars.py
    controls_tests: [test_live_emit_roundtrip, test_junk_rejected_valid_persists]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest
- path: environment/tracekit/smoke/corpus_len.py
  kind: helper
  rhymes_with: corpus emit
  non_fix_purpose: checks corpus file sizes only

#### code_forbidden_tokens
code_forbidden_tokens: [holdtrace, lane_open, dock_idle, lift_done, sort_gate, weigh_in]
