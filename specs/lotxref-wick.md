### Decision
GO — Attempt 1. Debugging repair of a C crash-lot xref mill: incremental atlas merge keeps vanished paths and stale spans; lookup takes the first symbol row; miss-exit stays green. Three loci plus a last-row decoy.

### Metadata
- version: 2
- Task name: lotxref-wick
- Title: Clip shows neighbour body
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "xref", "atlas", "crash"]
- Milestones: 0

## Authoring Brief

### Triviality Ledger
- Last-row symbol pick repairs a vanished-path neighbour clip and still mis-clips when two live files share a helper name; twin-origin dumps block that decoy.
- Hand-typed inkwell files fail when grade corrupts span.atlas and reruns reknit then clip.
- Source-only edits leave the prebuilt `/app/bin/lotxref` merging the old atlas.

### Per-gate Pitfall Inventory
- RC2: fix files stay scan.c / pick.c / gap.c with opaque symbols; no broken_* names.
- GX9: grade clip.out marks, atlas paths, and exit codes, not boolean answer keys.
- CR1: oracle symbols op_a, op_b, n_miss stay off CLI nouns in the same patch-verb sentence.
- R5: tests never rebuild; they invoke `/app/bin/lotxref`.
- R3: every graded test fails on the shipped tree.

### Initial Draft Commitments
- environment/slitmill/scan.c — merge atlas from a touch list and keep prior symbol spans
- environment/cupeel/pick.c — first matching symbol row, origin fopen fallback
- environment/drygate/gap.c — miss exit always success
- environment/cupeel/mtime.c — last-row decoy
- tests/test_outputs.py — own-body clip, twin helper, hide-origin fail, corrupt regen

### Public contract
- `/app/bin/lotxref` is a compiled ELF.
- `/app/bin/lotxref reknit` rewrites `/app/inkwell/span.atlas`.
- `/app/bin/lotxref clip DUMP` writes `/app/inkwell/clip.out`.
- Atlas rows name existing files under `/app/unitpit`.
- clip uses the dump origin file when helper names collide.
- reknit exits non-zero if a dump origin or atlas row would name a missing path.
- Grammar in `/app/baycard/forms.txt`. Map in `/app/baycard/BAY_NOTES.txt`.
- Hand-typed inkwell products do not count.

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
  role: build definition
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/slitmill/scan.c
  role: atlas rewrite
- path: environment/cupeel/pick.c
  role: clip lookup
- path: environment/drygate/gap.c
  role: miss exit
- path: environment/tblkit/hull_cli.c
  role: CLI
- path: environment/baycard/forms.txt
  role: grammar
- path: environment/baycard/BAY_NOTES.txt
  role: layout map

### fix_frontier
- count: 3
- distribution: scan, pick, gap across slitmill, cupeel, drygate
- naming_policy: opaque mill symbols
- forbidden_stems: lotxref, clip, reknit, lotbay, inkwell, atlas, dump, origin, helper, unitpit, neighbouring, ELF, span
- helpers_policy: last-row helper lives under sidecue; mill glue and headers under tblkit
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: artifacts, process exit, source marks
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: last-row symbol pick after a path change

### category_profile
- challenge_family: generated artifact completeness
- bug_family: stale generator view
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: reknit/clip commands, atlas and clip.out paths, existing-path rule, origin-file rule, ELF mill, fail-on-missing
- forbidden_instruction_leaks: touch-list merge, first-row lookup, always-zero miss exit, last-row decoy recipe
- category_specific_hardness_bar: atlas rewrite, origin lookup, and miss-exit must coordinate
- category_specific_verifier_risks: hand-written atlas, last-row pick, wrapper mill
- coverage_role: C source-atlas crash xref vs existing decoder/symmap mills

### difficulty_mechanism_plan
- mechanisms: [false_green_intermediate_states, buried_local_constraints, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants]
- adversarial_layers_count: 4
- fairness_guardrails: symptoms and public origin/path rules are visible; merge/lookup/exit are not
- mechanism: false_green_intermediate_states
  placement: reknit exits 0 while clip shows a neighbour body
  why_model_misses_it: mill returns success so the atlas looks healthy
  fairness_guardrail: instruction states the missing-path fail rule
- mechanism: buried_local_constraints
  placement: touch list vs full unitpit walk and span reparse
  why_model_misses_it: other dumps already clip cleanly
  fairness_guardrail: own-body and existing-path rules are public
- mechanism: deceptive_but_valid_local_evidence
  placement: last-row helper under cupeel
  why_model_misses_it: newest row can look like the vanished-path case
  fairness_guardrail: twin helper dumps
- mechanism: cross_file_cross_format_invariants
  placement: span.atlas, clip.out, reknit status
  why_model_misses_it: filling one artifact leaves lookup or miss-exit wrong
  fairness_guardrail: grammar names both products

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert traces atlas rows vs unitpit then rebuilds
- shortcut_audit: last-row pick, hand-write inkwell, script mill, source-only
- ablation_plan: drop scan, drop pick, drop gap each separately and expect residual fails
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Claude Opus 5 and GPT-5.6 worst-model floor

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: all graded tests pass after reknit and clip on the rebuilt mill

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: none; local C mill and dumps only
- long_context_token_floor: 0

### satisfiability_risk
- rc2_planned_name_risk: low — opaque scan/pick/gap names
- gx9_contract_risk: low — no scenario-key-value tables
- cr1_symbol_frontier_risk: medium — keep CLI nouns off fix symbols
- hidden_contract_risk: low — origin and fail-on-missing are public

### actionability_plan
- verifier_command_visible: `/app/bin/lotxref reknit` and `/app/bin/lotxref clip`
- source_fix_intent_visible: C modules listed in BAY_NOTES.txt need source updates under /app
- generated_output_rule_visible: span.atlas, clip.out
- exact_formula_home: `/app/baycard/forms.txt`
- schema_home: `/app/baycard/forms.txt`

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected; canonical gcc image, offline wheels, no multi-container

### reference_pattern
- justification_if_none: no promoted reference matches incremental source-atlas xref with origin-bound clip and vanish-path miss exit

### realism_source
- source_type: real_system
- evidence_basis: crash viewers that rebuild symbol-to-span tables from VCS change lists and leave rename leftovers keyed by symbol
- upstream_or_synthetic_rationale: minimized from incremental ctags/cscope-style indexes used by postmortem panes
- minimization_preserves: touch-list merge, first-symbol lookup, success without path existence
- synthetic_exception_review: not required

### Failure topology
reknit returns success and clip of a dump whose origin recently moved prints a neighbour function that still exists in the tree. Shared helper names across two live files keep working for the first atlas row. Completeness never fails while vanished paths remain in the atlas.

### Environment shape
Srcbeds C units, crashlot dumps, atlas mill under slitmill, clip lookup under cupeel, miss exit under drygate, grammar under baycard, products under inkwell, optional touch list under touchbay.

### Required artifacts
Standard Harbor scaffold, digest-pinned gcc runtime with python verifier venv, C mill, oracle copies, pytest suite, rubric, preship probes.

### Test plan
- ELF mill plus origin function mark after reknit and clip
- atlas rows name existing files
- held-out unit lands
- missing dump origin forces non-zero reknit
- twin helper clips the origin file body
- corrupt atlas then reknit recovers
- padding source lines still clips the origin mark
- fail path leaves prior atlas bytes
- second dump origin hide also fails
- restore then reknit succeeds
- reknit twice stays stable
- holdout twin helper
- clip token from origin cu

### Drafting guardrails
Do not name touch-list merge, first-row lookup, or last-row pick as the fix. Keep handbook symptoms-only.

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table
- path: environment/slitmill/scan.c
  symbol: op_a
  kind: function
  signature: int op_a(void)
  purpose: Rebuilds the span table from unitpit units.
- path: environment/cupeel/pick.c
  symbol: op_b
  kind: function
  signature: int op_b(const char *p)
  purpose: Writes clip.out for one dump.
- path: environment/drygate/gap.c
  symbol: n_miss
  kind: function
  signature: int n_miss(void)
  purpose: Returns reknit process status.

#### flipping_point_contract
locations:
  - id: A
    path: environment/slitmill/scan.c
    controls_tests: [test_aa_binary_magic_own_fn, test_bb_cu_still_there, test_cc_holdout_unit, test_ff_corrupt_then_regen, test_gg_lead_moves_mark]
  - id: B
    path: environment/cupeel/pick.c
    controls_tests: [test_ee_twin_share_cu, test_hh_cu_body_token, test_ii_holdout_twin, test_rr_idle_absent]
  - id: C
    path: environment/drygate/gap.c
    controls_tests: [test_dd_absent_cu_dirty, test_nn_hidden_keeps_prior, test_pp_second_cu_dirty, test_qq_restore_then_clean]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest
- path: environment/cupeel/mtime.c
  kind: helper
  rhymes_with: op_b
  non_fix_purpose: Optional last-row walk used by an unused sidecar.

#### code_forbidden_tokens
code_forbidden_tokens: [lotxref, clip, reknit, lotbay, inkwell, atlas, dump, origin, helper, unitpit, neighbouring, ELF, span]
