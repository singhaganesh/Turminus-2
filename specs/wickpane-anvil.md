### Decision
GO — Attempt 1. Debugging repair: etch ledger already matches the mill while two live takes of one fault split across panes. Agent must repair three pipeline loci, rebuild the native mill, then etch and bin. Re-etch before repair re-blesses the split.

### Metadata
- version: 2
- Task name: wickpane-anvil
- Title: Split panes after etch
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["go"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["wickpane", "vatmill", "loomwell", "shardops"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/wickpane` is native ELF.
- `etch` rewrites `/app/loomwell/etch.json` from `/app/crumbay`.
- `bin` rewrites `/app/shardops/bins.json` from `/app/shardops/live`.
- JSON maps take basename (no `.stk`) to pane `mod!fn` joined by `|`.
- `mod` stops before `+`; first field `i` folds; `[vdso]` and `[vsyscall]` omitted.
- `n7.stk` and `s7.stk` share one pane.
- First field `BAD` → `bin` non-zero; do not replace success bins.json.
- Source fixes under `/app`; hand-written JSON insufficient.
- Later checks rerun `bin` only.

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
  role: Go+python offline image
- path: construction_manifest.json
  role: local authoring artifact

### task_files

- path: environment/spoolkit/clip.go
  role: module token clip
- path: environment/spoolkit/scan.go
  role: take line scan helper
- path: environment/wicksrc/nest.go
  role: inlined row fold
- path: environment/pantryc/drop.go
  role: vsyscall/vdso omit
- path: environment/pantryc/join.go
  role: pane string join helper

### fix_frontier

- count: 3
- distribution: spoolkit, wicksrc, pantryc
- naming_policy: opaque Clip/Nest/Drop
- forbidden_stems: wickpane, pane, etch, bin, vdso
- helpers_policy: millhint Trim decoy; vatmill CLI split; spoolkit Scan/ErrReject and pantryc Join are co-resident non-fix helpers
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON artifacts, exit codes, recomputed panes
- forbidden_assertion_styles: boolean answer keys

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: re-etch with broken mill; nibble Trim decoy

### category_profile

- challenge_family: false_green_reference_refresh
- bug_family: false_green_reference_refresh
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, pane grammar, n7/s7 split symptom, BAD exit
- forbidden_instruction_leaks: ASLR offsets in keys, inlined-row keep, vdso keep, etch-as-oracle circularity
- category_specific_hardness_bar: green etch versus split live panes
- category_specific_verifier_risks: test-side mill, hand JSON, re-etch blessing
- coverage_role: debugging C2 rebuild-before-claim with stale ledger

### difficulty_mechanism_plan

- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: etch exits 0; ledger matches mill
  why_model_misses_it: agents trust the ledger
  fairness_guardrail: instruction names the n7/s7 split
- mechanism: deceptive_but_valid_local_evidence
  placement: millhint Trim zeros last hex nibble
  why_model_misses_it: looks like address cleanup
  fairness_guardrail: twins still must share one pane
- mechanism: cross_file_cross_format_invariants
  placement: clip, fold, omit must agree on one pane string
  why_model_misses_it: one locus still splits twins
  fairness_guardrail: grammar in GRAMMAR.txt
- mechanism: stateful_multi_step_dependencies
  placement: source fix then rebuild then etch then bin
  why_model_misses_it: skip rebuild or re-etch first
  fairness_guardrail: instruction requires etch then bin after sources

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert repairs three loci, ships mill, etches, bins
- shortcut_audit: re-etch only, Trim decoy, Python mill, hand JSON
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
- sidecar_or_protocol_notes: stk takes bundled

### satisfiability_risk

- rc2_planned_name_risk: low — fix dirs are spoolkit/wicksrc/pantryc
- gx9_contract_risk: low JSON string maps
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public grammar

### actionability_plan

- verifier_command_visible: wickpane etch and bin
- source_fix_intent_visible: LAYOUT.txt modules; /app source
- generated_output_rule_visible: etch.json bins.json pane grammar
- exact_formula_home: GRAMMAR.txt plus instruction pane rules
- schema_home: instruction.md and GRAMMAR.txt

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- justification_if_none: no promoted reference for Go stack-pane mill whose etch ledger was refreshed by the defective mill

### realism_source

- source_type: real_bug
- evidence_basis: crash-bucket pipelines that regenerate goldens from the same normaliser under test (Breakpad/Sentry-style signature drift after a regen)
- upstream_or_synthetic_rationale: minimized to text stack takes plus a Go mill; no vendor Breakpad tree
- minimization_preserves: green regen, stale ledger, split buckets, skip rebuild
- synthetic_exception_review: not required

### Failure topology
Operators see etch succeed and the ledger match mill output while two live takes of one fault land on different panes. Address tails remain in module tokens, inlined rows stay as frames, and vdso rows survive. The millhint trim helper looks like the address cleanup. Re-running etch without repairing the mill rewrites the ledger to the same split.

### Environment shape
Go mill desk, clip/fold/omit packages, decoy trim helper, crumbay takes, live takes, etch ledger, bind notes, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, Go modules, mill rebuild, preship probes, rubric.

### Test plan
- test_wp00_magic_head
- test_wp01_pair_same
- test_wp02_ledger_obj
- test_wp03_filed_obj
- test_wp04_plus_gone
- test_wp05_inner_gone
- test_wp06_clock_gone
- test_wp07_fault_keep
- test_wp08_obj_shape
- test_wp09_extra_copy
- test_wp10_solo_key
- test_wp11_twice_same
- test_wp_zz_ledger_redo

### Drafting guardrails
Do not name Clip, Nest, Drop, ASLR, or golden-refresh circularity. Tests must not mill except zz recovery. Punish Trim via twins plus rubric. Tests compute panes from public grammar, never from etch.json as authority.

### Triviality Ledger

- Re-etch on the broken mill — blocked by independent pane compute plus zz recovery after corrupt ledger.
- millhint Trim nibble — blocked by n7/s7 still splitting and a negative rubric.
- Hand-written JSON — blocked by bin rerun and zz etch recovery.
- Shell mill at `/app/bin/wickpane` — blocked by ELF magic on the rebuilt binary.
- Source-only without rebuild — old ELF remains; R5 source_only.sh.
- Naive `patch -i` oracle — blocked by full-file writes in solve.sh.

### Per-gate Pitfall Inventory

- RC2: repair paths in LAYOUT.txt name directories, not Clip/Nest/Drop.
- GX9: grade pane strings and exit codes, not boolean flags.
- CR8: vatmill stage.go names Clip+Nest; stage2.go names Drop.
- R5: tests do not ship except zz recovery.
- R3: every graded test fails on broken tree (ELF-only is paired with pane asserts).
- P4: Trim decoy punished by rubric.

### Initial Draft Commitments

- environment/spoolkit/clip.go
- environment/spoolkit/scan.go
- environment/wicksrc/nest.go
- environment/pantryc/drop.go
- environment/pantryc/join.go
- environment/celltyp/row.go
- environment/millhint/trim.go
- environment/vatmill/main.go
- environment/vatmill/etch.go
- environment/vatmill/bin.go
- environment/vatmill/stage.go
- environment/vatmill/stage2.go
- environment/bindnote/LAYOUT.txt
- environment/bindnote/GRAMMAR.txt
- environment/crumbay/n7.stk
- environment/crumbay/s7.stk
- environment/crumbay/p3.stk
- environment/crumbay/q9.stk
- environment/crumbay/r2.stk
- environment/shardops/live/n7.stk
- environment/shardops/live/s7.stk
- environment/shardops/live/p3.stk
- environment/shardops/live/q9.stk
- environment/shardops/live/r2.stk
- environment/loomwell/etch.json
- environment/shardops/bins.json
- environment/Makefile
- environment/go.mod
- environment/Dockerfile
- environment/.dockerignore
- environment/offpack/wheels
- environment/offpack/debs
- tests/test_outputs.py
- tests/test.sh
- tests/heldout/h8.stk
- solution/solve.sh
- solution/clip.go
- solution/nest.go
- solution/drop.go
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

- path: environment/spoolkit/clip.go
  symbol: Clip
  kind: function
  signature: Clip(rows []celltyp.Row) []celltyp.Row
  purpose: copies rows with module tokens cut at plus
- path: environment/wicksrc/nest.go
  symbol: Nest
  kind: function
  signature: Nest(rows []celltyp.Row) []celltyp.Row
  purpose: copies named rows and skips first-field i rows
- path: environment/pantryc/drop.go
  symbol: Drop
  kind: function
  signature: Drop(rows []celltyp.Row) []celltyp.Row
  purpose: copies rows whose module token is not vdso or vsyscall

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/spoolkit/clip.go
    controls_tests: [test_wp04_plus_gone, test_wp02_ledger_obj, test_wp10_solo_key, test_wp09_extra_copy]
  - id: B
    path: environment/wicksrc/nest.go
    controls_tests: [test_wp05_inner_gone, test_wp01_pair_same, test_wp08_obj_shape, test_wp11_twice_same]
  - id: C
    path: environment/pantryc/drop.go
    controls_tests: [test_wp06_clock_gone, test_wp07_fault_keep, test_wp03_filed_obj, test_wp00_magic_head, test_wp_zz_ledger_redo]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

#### decoy_manifest

- path: environment/millhint/trim.go
  kind: helper
  rhymes_with: Clip
  non_fix_purpose: zeros the last hex nibble of a plus tail

#### code_forbidden_tokens

```
code_forbidden_tokens: [wickpane, etch, loomwell, crumbay, shardops, bins, bindnote, LAYOUT, GRAMMAR, pane, n7, s7, vdso, vsyscall, ELF]
```
