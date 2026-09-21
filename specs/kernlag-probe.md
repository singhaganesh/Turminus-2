### Decision
GO — Debugging repair of C kernscribe synctab pipeline silently using snaparchive layout one release behind benchkern export; three cooperating modules; held-out capture; rebuild lever on `/app/bin/kernscribe`.

### Metadata
- version: 2
- Task name: kernlag-probe
- Title: Bundled types one release behind
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "kernel-types", "offsets", "probe"]
- Milestones: 0

## Authoring Brief

### Triviality Ledger
- Pinning snaparchive default.pin to newest release still ignores benchkern live export.
- Hand-written synctab_out files fail when inspect still uses stale offsets in ELF.
- Source-only edits without synctab leave prebuilt artifacts wrong.

### Per-gate Pitfall Inventory
- RC2: repair modules off instruction nouns; route map in fieldnotes only.
- GX9: grade inspect JSON and procance.tag, not boolean keys.
- CR1: oracle symbols choose_layout, write_types_tab, permit_tag off CLI nouns in patch sentences.
- R5: tests never call synctab or make.
- R3: every graded test fails on shipped tree.

### Initial Draft Commitments
- environment/relc/input.c — prefers bundled snapshot over livekern export
- environment/lagpipe/tblw/emit_writer.c — emits layout.tbl from picked table
- environment/lagpipe/tagc/gate.c — allows bundle fallback silently
- environment/snapvault/policy.conf — decoy pin bump
- tests/test_outputs.py — stamp line, reference cards, table line order, held-out capture

### Public contract
- `/app/bin/kernscribe synctab` writes `/app/lagpipe/synctab_out/layout.tbl` and `/app/lagpipe/synctab_out/procance.tag`, rebuilds `/app/bin/kernscribe`.
- procance.tag must be `live:` + `/app/livekern/running.release` on this image.
- synctab exits non-zero when source would be `bundle:`.
- `/app/bin/kernscribe inspect <sample>` JSON for sched_entity fields; samples match sibling cards under `/app/memvault/cards/`.

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
  role: behavioral verifier
- path: solution/solve.sh
  role: oracle
- path: environment/Dockerfile
  role: image build
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/lagpipe/synclink/driver.c
  role: CLI
- path: environment/relc/input.c
  role: table source selection
- path: environment/lagpipe/tblw/emit_writer.c
  role: layout.tbl writer
- path: environment/lagpipe/tagc/gate.c
  role: bundle fallback exit policy
- path: environment/lagpipe/synclink/field_emit.c
  role: sample JSON emitter
- path: environment/snapvault/policy.conf
  role: decoy pin bump
- path: environment/lagpipe/fieldnotes/ROUTE_MAP.txt
  role: repair path map

### fix_frontier
- count: 3
- distribution: relc, tblw, tagc
- naming_policy: opaque module roots
- forbidden_stems: bundle, migration, fallback
- helpers_policy: livekern/snapvault folklore
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: inspect JSON, procance.tag, layout.tbl line
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis + rebuild
- collapse_risk: pin bump without live export path

### category_profile
- challenge_family: stale_generated_artifacts
- profile_name: kernel_type_lag
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: choose_layout, permit_tag, patch files
- category_specific_hardness_bar: regen on target image vs dev machine
- category_specific_verifier_risks: plausible wrong offsets
- coverage_role: debugging rebuild-before-claim

### satisfiability_risk
- rc2_planned_name_risk: low opaque module roots
- gx9_contract_risk: low json/tag
- cr1_symbol_frontier_risk: low thin oracle
- hidden_contract_risk: low public cards

### actionability_plan
- verifier_command_visible: synctab and inspect named
- source_fix_intent_visible: C modules listed in fieldnotes route map
- generated_output_rule_visible: layout.tbl and procance.tag rules public
- exact_formula_home: instruction field names
- schema_home: instruction.md

### waiver_plan
- waivers_expected: false
- waiver_rationale: none

### reference_pattern
- justification_if_none: no promoted reference matches kernel type lag with live-vs-bundle source tagging

### realism_source
- source_type: synthetic_exception
- evidence_basis: bpf/probe tooling falling back to bundled BTF when live kernel headers unavailable
- upstream_or_synthetic_rationale: container simulates analysis image without exposed kernel types
- minimization_preserves: livekern export path, snapvault archives, offset table regen
- synthetic_exception_review: bundled pin decoy is plausible ops note

### difficulty_mechanism_plan
- mechanisms: buried_local_constraints, deceptive_but_valid_local_evidence, false_green_intermediate_states, cross_file_cross_format_invariants, rebuild_lever
- adversarial_layers_count: 5
- fairness_guardrails: all local deterministic
- mechanism: buried_local_constraints
  placement: pick order prefers snaparchive pin
  why_model_misses_it: looks like intentional offline default
  fairness_guardrail: livekern export exists locally
- mechanism: deceptive_but_valid_local_evidence
  placement: pid/weight still plausible
  why_model_misses_it: agents stop after two fields match
  fairness_guardrail: cards name all four fields
- mechanism: false_green_intermediate_states
  placement: pin bump to 6.8.12 in snaparchive
  why_model_misses_it: newest bundle feels correct
  fairness_guardrail: live source contract public
- mechanism: cross_file_cross_format_invariants
  placement: layout.tbl, procance.tag, inspect JSON
  why_model_misses_it: editing tag without regen leaves inspect stale
  fairness_guardrail: schemas public
- mechanism: rebuild_lever
  placement: synctab rebuilds binary
  why_model_misses_it: source patch without synctab
  fairness_guardrail: instruction requires synctab before grade

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert regen on image vs pin bump
- shortcut_audit: pin bump, hand-written tab, source-only
- ablation_plan: fix pick only, expect policy or inspect fail
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Opus 5 / GPT-5.6

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: reward 1 only when all tests pass

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: memvault samples bundled
