### Decision
GO — Attempt 1. Debugging repair of a C census mill that preprocesses weld sources under a single recipe; three cooperating loci (walk, recipe load, miss exit); held-out salvage-gated marks; rebuild lever on `/app/bin/pinweld`.

### Metadata
- version: 2
- Task name: pinweld-solder
- Title: Census misses salvage marks
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "census", "preprocessor", "hooks"]
- Milestones: 0

## Authoring Brief

### Triviality Ledger
- Hoisting one salvage mark into the always-on block registers that mark and leaves every other recipe-gated mark invisible; held-out salvage-gated names plus a LAB_ONLY ghost that must stay out block the hoist.
- Hand-written `points.reg` / `runtime.lst` fail when grade reruns `census` and `poke` on a fresh declaration.
- Source-only edits leave the prebuilt `/app/bin/pinweld` still walking the default recipe.

### Per-gate Pitfall Inventory
- RC2: fix files stay `walk.c` / `load.c` / `gap.c` with opaque symbols; no broken_* names.
- GX9: grade registry lines, poke stdout, and exit codes, not boolean answer keys.
- CR1: oracle symbols `op_fill`, `cfg_open`, `n_miss` stay off CLI nouns in the same patch-verb sentence.
- R5: tests never rebuild; they invoke `/app/bin/pinweld`.
- R3: every graded test fails on the shipped tree.

### Initial Draft Commitments
- environment/inkmill/walk.c — preprocess walk uses a hardcoded core recipe
- environment/inkmill/load.c — recipe loader returns the first flags file only
- environment/runtdesk/gap.c — miss exit treats a non-empty scan log as success
- environment/inkmill/hoist.c — plausible hoist decoy
- tests/test_outputs.py — union coverage, held-out guard, short-set exit, poke, regen

### Public contract
- `/app/bin/pinweld` is a compiled ELF mill.
- `/app/bin/pinweld census` mints `/app/wellbin/points.reg` and `/app/wellbin/runtime.lst` from `WELD_HOOK` names under `/app/weldkit` across every recipe in `/app/shipcfgs`, and writes `/app/wellbin/scan.log`.
- Registry names equal the union of `WELD_HOOK` names visible under shipped recipes.
- `/app/bin/pinweld poke NAME` fires a salvage-path mark once that name is in the registry.
- Census exits non-zero when a declared shipped name is missing from `points.reg`.
- Grammar in `/app/notes/forms.txt`. Bay map in `/app/notes/BAYMAP.txt`.
- Hand writes of wellbin files are not enough.

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
- path: environment/inkmill/driver.c
  role: CLI entry
- path: environment/inkmill/walk.c
  role: preprocess walk
- path: environment/inkmill/load.c
  role: recipe loader
- path: environment/runtdesk/gap.c
  role: miss exit
- path: environment/inkmill/hoist.c
  role: decoy hoist helper
- path: environment/notes/forms.txt
  role: format notes
- path: environment/notes/BAYMAP.txt
  role: bay map

### fix_frontier
- count: 3
- distribution: walk, load, gap across inkmill and runtdesk
- naming_policy: opaque mill symbols
- forbidden_stems: pinweld, census, poke, salvage, wellbin, weldkit, shipcfgs, WELD_HOOK
- helpers_policy: hoist rhymes with ops folklore, not the fix
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: artifacts, poke stdout, process exit
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: hoist one mark out of a guarded block without unioning recipes

### category_profile
- challenge_family: generated artifact completeness
- bug_family: stale generator view
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: census/poke commands, registry paths, union-across-shipped-recipes rule, ELF mill, fail-on-missing
- forbidden_instruction_leaks: default cpp flags, first-flags-only loader, scan-log-as-success exit, hoist recipe
- category_specific_hardness_bar: generated registry, recipe matrix, and miss-exit must coordinate
- category_specific_verifier_risks: hand-written registry, hoist one mark, wrapper mill
- coverage_role: C preprocessor census mill vs existing decoder/symmap mills

### difficulty_mechanism_plan
- mechanisms: [false_green_intermediate_states, buried_local_constraints, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants]
- adversarial_layers_count: 4
- fairness_guardrails: symptoms and public union rule are visible; cpp/loader/exit are not
- mechanism: false_green_intermediate_states
  placement: census exits 0 while salvage marks are absent
  why_model_misses_it: scan.log names the file so the mill looks healthy
  fairness_guardrail: instruction states the missing-mark fail rule
- mechanism: buried_local_constraints
  placement: recipe files under shipcfgs vs hardcoded core flags in walk
  why_model_misses_it: core marks appear so the walk looks complete
  fairness_guardrail: union-across-shipped-recipes is public
- mechanism: deceptive_but_valid_local_evidence
  placement: hoist helper and handbook note about older always-on salvage marks
  why_model_misses_it: hoisting the visible salvage mark makes poke pass on that one name
  fairness_guardrail: held-out gated names and LAB_ONLY ghost
- mechanism: cross_file_cross_format_invariants
  placement: points.reg, runtime.lst, poke, exit status
  why_model_misses_it: filling one artifact leaves poke or miss-exit wrong
  fairness_guardrail: grammar names both products

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert traces census cpp flags vs shipcfgs then rebuilds
- shortcut_audit: hoist, hand-write wellbin, script mill, source-only
- ablation_plan: drop load, drop walk, drop gap each separately and expect residual fails
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Claude Opus 5 and GPT-5.6 worst-model floor

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: all graded tests pass after one census on the rebuilt mill

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: none; local C mill and flag files only
- long_context_token_floor: 0

### satisfiability_risk
- rc2_planned_name_risk: low — opaque walk/load/gap names
- gx9_contract_risk: low — no scenario-key-value tables
- cr1_symbol_frontier_risk: medium — keep CLI nouns off fix symbols
- hidden_contract_risk: low — union and fail-on-missing are public

### actionability_plan
- verifier_command_visible: `/app/bin/pinweld census` and `/app/bin/pinweld poke`
- source_fix_intent_visible: repair belongs in compiled C sources
- generated_output_rule_visible: points.reg, runtime.lst, scan.log
- exact_formula_home: `/app/notes/forms.txt`
- schema_home: `/app/notes/forms.txt`

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected; canonical gcc image, offline wheels, no multi-container

### reference_pattern
- justification_if_none: no promoted reference matches multi-recipe preprocessor census of hook marks

### realism_source
- source_type: real_system
- evidence_basis: annotation processors that run the preprocessor under one compile_commands recipe and miss conditionally compiled injection points
- upstream_or_synthetic_rationale: minimized from clang annotation / AOP-style scanners that cpp with default flags
- minimization_preserves: default-recipe preprocess, incomplete recipe load, success-on-scan-count
- synthetic_exception_review: not required

### Failure topology
Census succeeds and logs the salvage translation unit, yet the minted registry omits marks that only appear under non-core shipped recipes. Completeness treats a populated scan log as success. Poke reads the runtime list, so the salvage-path mark cannot fire until the walk, the recipe loader, and the miss exit agree.

### Environment shape
Annotated C units under weldkit, census mill under inkmill, miss/poke helpers under runtdesk, shipped recipe files under shipcfgs, grammar under notes, minted products under wellbin.

### Required artifacts
Standard Harbor scaffold, digest-pinned gcc runtime with python verifier venv, C mill, oracle patches, pytest suite, rubric, preship probes.

### Test plan
- ELF mill plus stock salvage mark present after census
- one census covers the shipped union
- held-out salvage-gated declaration lands
- short registry forces non-zero census
- poke fires the salvage-path mark
- corrupt wellbin then census recovers
- dusk/night recipe mark present
- scan.log lists the salvage unit
- runtime.lst matches points.reg
- two fresh gated declarations both land
- census twice is stable
- always-on core mark stays
- LAB_ONLY ghost omitted

### Drafting guardrails
Do not name default cpp flags, first-file loaders, or hoist-the-ifdef as the fix. Keep handbook symptoms-only.

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table
- path: environment/inkmill/walk.c
  symbol: op_fill
  kind: function
  signature: void op_fill(void)
  purpose: Walks weld sources through recipes and writes wellbin products.
- path: environment/inkmill/load.c
  symbol: cfg_open
  kind: function
  signature: int cfg_open(char out[][512], int max)
  purpose: Loads flag strings from shipped recipe files.
- path: environment/runtdesk/gap.c
  symbol: n_miss
  kind: function
  signature: int n_miss(int written, int expect)
  purpose: Returns census process status.

#### flipping_point_contract
locations:
  - id: A
    path: environment/inkmill/walk.c
    controls_tests: [test_aa_hull_bytes_and_stock_set, test_bb_once_covers_union, test_cc_held_out_guard_lands, test_ff_corrupt_then_regen, test_ll_always_on_stays]
  - id: B
    path: environment/inkmill/load.c
    controls_tests: [test_gg_dusk_decl_present, test_jj_two_fresh_both, test_kk_idempotent_twice, test_nn_ghost_omitted]
  - id: C
    path: environment/runtdesk/gap.c
    controls_tests: [test_dd_short_set_nonzero, test_ee_fire_guard_name, test_hh_seen_note_lists_file, test_ii_lst_matches_set]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest
- path: environment/inkmill/hoist.c
  kind: helper
  rhymes_with: op_fill
  non_fix_purpose: Optional copy of always-on marks into a sidecar note.

#### code_forbidden_tokens
code_forbidden_tokens: [pinweld, census, poke, salvage, wellbin, weldkit, shipcfgs, WELD_HOOK]
