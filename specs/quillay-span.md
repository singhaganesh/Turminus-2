### Decision
GO — Attempt 1. Debugging repair of a C++ sampling mill whose layout ledger keys a mapped ELF by identity while tamp rewrites that ELF in place; three cooperating loci (bind, halt, span); held-out wave symbols; rebuild lever on `/app/bin/quillay`.

### Metadata
- version: 2
- Task name: quillay-span
- Title: Sampler keeps prior names
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c++"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c++", "elf", "sampling", "layout"]
- Milestones: 0

## Authoring Brief

### Triviality Ledger
- Keying the layout row on modification time still hits after tamp because stamps are clamped; tests change WAVE and require live symbol names plus SHA-256 match.
- Hand-written `layout.qmap` / `flame.qprf` fail when grade reruns `scribe` after corruption and after a WAVE tamp.
- Source-only edits leave the prebuilt `/app/bin/quillay` still serving the prior generation.

### Per-gate Pitfall Inventory
- RC2: fix files stay `op_bind.cc` / `op_halt.cc` / `op_mesh.cc` with opaque symbols; no broken_* names.
- GX9: grade flame names and weigh exit codes, not boolean answer keys.
- CR1: oracle symbols `op_bind`, `op_halt`, `op_mesh` stay off CLI nouns in the same patch-verb sentence.
- R5: tests never rebuild the mill; they invoke `/app/bin/quillay`.
- R3: every graded test fails on the shipped tree.

### Initial Draft Commitments
- environment/millhull/op_bind.cc — layout row reuse uses identity only
- environment/cuewell/op_halt.cc — weigh treats identity plus stamp as clean
- environment/wickdesk/op_mesh.cc — flame copy on reuse
- environment/offpack/stamp.cc — clamped timestamp helper decoy
- tests/test_outputs.py — live names, weigh dirty, hold-out wave, regen

### Public contract
- `/app/bin/quillay` is a compiled ELF mill.
- `/app/bin/quillay tamp` rewrites `/app/hearthbin/span.elf` from `/app/spanhearth`.
- `/app/bin/quillay scribe` writes `/app/wickbin/layout.qmap` and `/app/wickbin/flame.qprf`.
- QMAP1 rows: path device inode text_vma text_off text_sz
- `/app/bin/quillay weigh` exits non-zero when the mapped file's contents changed under the same device and inode
- QPRF1 lines: pc_hex name matching live span.elf for every PC in `/app/spanhearth/pc.lst`.
- Grammar in `/app/baycue/forms.txt`. Bay map in `/app/baycue/BAYMAP.txt`.
- Hand writes of wickbin files are not enough.

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
- path: environment/millhull/main.cc
  role: CLI entry
- path: environment/millhull/drive.cc
  role: scribe driver
- path: environment/millhull/op_bind.cc
  role: layout bind
- path: environment/cuewell/op_halt.cc
  role: weigh status
- path: environment/wickdesk/op_mesh.cc
  role: flame emit
- path: environment/millhull/elfbits.cc
  role: ELF helpers
- path: environment/millhull/bind.h
  role: bind header
- path: environment/millhull/lay.h
  role: layout record
- path: environment/millhull/elfbits.h
  role: ELF helper header
- path: environment/cuewell/halt.h
  role: halt header
- path: environment/wickdesk/mesh.h
  role: mesh header
- path: environment/offpack/stamp.cc
  role: decoy stamp helper
- path: environment/baycue/forms.txt
  role: format notes
- path: environment/baycue/BAYMAP.txt
  role: bay map

### fix_frontier
- count: 3
- distribution: bind, halt, span across millhull, cuewell, wickdesk
- naming_policy: opaque mill symbols
- forbidden_stems: quillay, scribe, tamp, weigh, wickbin, flame, layout, spanhearth, digest
- helpers_policy: stamp rhymes with identity folklore, not the fix
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: artifacts, process exit
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: key layout on mtime or always copy flame

### category_profile
- challenge_family: stale generator view
- bug_family: stale generator view
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: tamp/scribe/weigh commands, qmap/qprf paths, SHA-256 digest rule, ELF mill, fail-on-disagreement
- forbidden_instruction_leaks: inode reuse, clamped timestamps as the key, copy-old-flame on hit
- category_specific_hardness_bar: generated layout, flame names, and weigh-exit must coordinate
- category_specific_verifier_risks: hand-written wickbin, mtime key, wrapper mill
- coverage_role: C++ ELF layout mill vs existing C census/symmap mills

### difficulty_mechanism_plan
- mechanisms: [false_green_intermediate_states, buried_local_constraints, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants]
- adversarial_layers_count: 4
- fairness_guardrails: symptoms and public digest/name/weigh rules are visible; identity-only bind is not
- mechanism: false_green_intermediate_states
  placement: scribe and weigh exit 0 while flame names are prior-generation
  why_model_misses_it: layout.qmap still lists the elf and names are real symbols
  fairness_guardrail: instruction states live-symbol and digest rules
- mechanism: buried_local_constraints
  placement: bind reuses a row on identity while tamp rewrites bytes
  why_model_misses_it: restarting the mill appears to be the operator workaround
  fairness_guardrail: grade requires repaired mill plus regenerated wickbin
- mechanism: deceptive_but_valid_local_evidence
  placement: stamp helper and clamped utime on tamp
  why_model_misses_it: adding mtime to the row still hits
  fairness_guardrail: WAVE change plus SHA-256 public rule
- mechanism: cross_file_cross_format_invariants
  placement: qmap digest, flame names, weigh status
  why_model_misses_it: filling one artifact leaves weigh or names wrong
  fairness_guardrail: forms.txt names both products

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert tamp then compares nm of span.elf to flame and sha256sum to qmap
- shortcut_audit: mtime key, hand-write wickbin, script mill, source-only
- ablation_plan: drop bind, drop halt, drop span each separately and expect residual fails
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Claude Opus 5 and GPT-5.6 worst-model floor

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: all graded tests pass after tamp/scribe/weigh on the rebuilt mill

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: none; local C++ mill and ELF only
- long_context_token_floor: 0

### satisfiability_risk
- rc2_planned_name_risk: low — opaque bind/halt/span names
- gx9_contract_risk: low — no scenario-key-value tables
- cr1_symbol_frontier_risk: medium — keep CLI nouns off fix symbols
- hidden_contract_risk: low — digest, names, and weigh are public

### actionability_plan
- verifier_command_visible: `/app/bin/quillay tamp`, `/app/bin/quillay scribe`, `/app/bin/quillay weigh`
- source_fix_intent_visible: source fixes under `/app` in modules named from BAYMAP.txt
- generated_output_rule_visible: layout.qmap, flame.qprf
- exact_formula_home: `/app/baycue/forms.txt`
- schema_home: `/app/baycue/forms.txt`

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected; canonical gcc image, offline wheels, no multi-container

### reference_pattern
- justification_if_none: no promoted reference matches in-place ELF rewrite with identity-keyed layout ledger and digest-weigh

### realism_source
- source_type: real_system
- evidence_basis: long-lived profilers and symbolizers that cache module maps by st_dev/st_ino while linkers rewrite artifacts in place
- upstream_or_synthetic_rationale: minimized from perf/gdb module-cache invalidation misses under reproducible-build timestamps
- minimization_preserves: identity-only reuse, clamped stamps, silent success on stale maps
- synthetic_exception_review: not required

### Failure topology
Tamp rewrites span.elf in place. Scribe still exits 0 and layout.qmap still names that path. Flame names remain real symbols from the previous generation. Weigh still exits 0. Completeness of the mill requires bind to stop treating identity as content, span to emit names from the live ELF, and halt to fail when digest and bytes disagree.

### Environment shape
Workload C under spanhearth, mill under millhull, weigh helper under cuewell, flame emit under wickdesk, stamp decoy under offpack, grammar under baycue, products under wickbin and hearthbin.

### Required artifacts
Standard Harbor scaffold, digest-pinned gcc runtime with python verifier venv, C++ mill, oracle copies, pytest suite, rubric, preship probes.

### Test plan
- ELF mill magic
- qmap digest equals SHA-256 of span.elf
- flame names match live symbols
- weigh non-zero after bytes change
- held-out WAVE symbol lands
- corrupt wickbin then scribe recovers
- QPRF1 prefix and pc_hex name fields
- weigh 0 when bytes match
- second scribe stable
- dusk PC not attributed to neighbour
- clamped stamp still refreshes names after WAVE tamp
- one scribe writes both wickbin products
- tamp without scribe makes weigh dirty

### Drafting guardrails
Do not name inode reuse, clamped-mtime keys, or copy-old-flame as the fix. Keep handbook symptoms-only.

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table
- path: environment/millhull/op_bind.cc
  symbol: op_bind
  kind: function
  signature: int op_bind(const char *a, struct Lay *b)
  purpose: Fills a layout row for the mapped elf and writes layout.qmap.
- path: environment/cuewell/op_halt.cc
  symbol: op_halt
  kind: function
  signature: int op_halt(void)
  purpose: Returns weigh process status.
- path: environment/wickdesk/op_mesh.cc
  symbol: op_mesh
  kind: function
  signature: int op_mesh(const char *a, const struct Lay *b, int c)
  purpose: Writes flame.qprf for PCs in pc.lst.

#### flipping_point_contract
locations:
  - id: A
    path: environment/millhull/op_bind.cc
    controls_tests: [test_qs01_native_magic, test_qs02_row_sha, test_qs06_corrupt_then_mint, test_qs11_frozen_clock, test_qs12_one_pass_pair]
  - id: B
    path: environment/cuewell/op_halt.cc
    controls_tests: [test_qs04_dirty_status, test_qs08_vet_clean, test_qs09_second_mint, test_qs13_wave_swap]
  - id: C
    path: environment/wickdesk/op_mesh.cc
    controls_tests: [test_qs03_name_live, test_qs05_holdout_wave, test_qs07_sheet_prefix, test_qs10_neighbour_gap]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest
- path: environment/offpack/stamp.cc
  kind: helper
  rhymes_with: op_bind
  non_fix_purpose: Records and compares file modification stamps for tamp reproducibility notes.

#### code_forbidden_tokens
code_forbidden_tokens: [quillay, scribe, tamp, weigh, wickbin, flame, layout, spanhearth, digest]
