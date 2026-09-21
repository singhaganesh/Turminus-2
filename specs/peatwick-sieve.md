### Decision
GO — Attempt 1. Debugging repair: a Ruby desk sieve refreshes a binary ledger plus pick JSON from coverage cards, but the mill walks consecutive seals, joins coverage by basename, and treats an empty pick as success. Agent must repair three mill roots then re-run kindle.

### Metadata
- version: 2
- Task name: peatwick-sieve
- Title: Desk sieve skips unsaved bytes
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["ruby"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["ruby", "desk-sieve", "coverage-join", "stamp-seals"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/peatwick kindle` walks `/app/livefold` against the newest tree under `/app/snapurn/seals`, refreshes `/app/inkvat/sieve.bin` and `/app/inkvat/pick.json` from `/app/lutcards` sheets.
- Differing desk bytes appear as `live:<relpath>`.
- Each such path pulls every `ASSAY` for that relative path. Rows omit paths with no assays.
- `pick.json` is `{"rows":[{"path":"live:<relpath>","assays":["..."]}]}` with sorted assay names.
- `kindle` exits non-zero when the desk differs from the newest seal and `rows` is empty. Matching the newest seal with empty rows may exit 0.
- Sheets: `REL` then `ASSAY` lines. `sieve.bin` records: uint16be path length, UTF-8 `live:` token, uint16be count, uint16be-length assay names.
- Verifier reruns `/app/bin/peatwick kindle`. Hand-written ledgers are not enough. Source fixes under `/app` required. Modules named in `/app/fieldnotes/LAYOUT.txt`.

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
  role: Ruby+python offline image
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/gaitmod/stride.rb
  role: change-set walk
- path: environment/joincue/latch.rb
  role: coverage join
- path: environment/stillbay/vale.rb
  role: empty-pick gate

### fix_frontier
- count: 3
- distribution: gaitmod, joincue, stillbay
- naming_policy: opaque loom/hitch/vale
- forbidden_stems: peatwick, kindle, livefold
- helpers_policy: SEAL_FIRST decoy sidecar
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON artifacts, exit codes, binary records
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: copy the dirty desk into a new seal then kindle

### category_profile
- challenge_family: stale_index_ignores_live_tree
- bug_family: stale_index_ignores_live_tree
- profile_name: filesystem_state_reconstruction
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: seal-pair diff, basename join, vacuous success
- category_specific_hardness_bar: unsaved bytes ignored while seal history still looks consistent
- category_specific_verifier_risks: test-side kindle for every case, hand ledger
- coverage_role: debugging C2 regen-before-claim

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: kindle exits 0 with empty rows while the desk is dirty
  why_model_misses_it: empty pick looks like a docs-only pass
  fairness_guardrail: instruction requires non-zero when desk differs and rows empty
- mechanism: deceptive_but_valid_local_evidence
  placement: SEAL_FIRST sidecar
  why_model_misses_it: sealing then kindling makes the last pair include the edit
  fairness_guardrail: tests require live tokens while desk still differs from newest seal
- mechanism: cross_file_cross_format_invariants
  placement: desk vs seals vs sieve.bin vs pick.json vs sheets
  why_model_misses_it: edits JSON only
  fairness_guardrail: verifier reruns kindle and parses sieve.bin
- mechanism: stateful_multi_step_dependencies
  placement: source fix then kindle regen
  why_model_misses_it: skip kindle
  fairness_guardrail: stale emberwell remains after source-only

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert diffs desk to newest seal then kindle
- shortcut_audit: seal-first, hand pick.json, skip kindle
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
- sidecar_or_protocol_notes: seals and sheets bundled

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs are walkbay/bindpit/hushgate
- gx9_contract_risk: low JSON objects
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan
- verifier_command_visible: peatwick kindle
- source_fix_intent_visible: pipeline modules in LAYOUT.txt
- generated_output_rule_visible: sieve.bin pick.json
- exact_formula_home: live token plus sheet ASSAY lists
- schema_home: instruction.md and LAYOUT.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Ruby desk sieve that joins coverage cards to unsaved tree bytes against sealed snapshots

### realism_source
- source_type: synthetic_exception
- evidence_basis: test-impact tools that key a change set by the last two commits and treat an empty selection as no-impact success
- upstream_or_synthetic_rationale: cannot ship a private CI impact-analyser tree
- minimization_preserves: kindle green, empty pick, unsaved bytes ignored, skip regen
- synthetic_exception_review: seal-first is a realistic decoy

### Failure topology
Operators see kindle succeed with an empty pick while unsaved desk files still differ from the newest seal. Consecutive seals only disagree on a docs file, coverage join keys by basename so a colliding short name can steal assays, and an empty row list is treated as a legitimate docs-only pass even on a dirty desk. Copying the desk into a new seal makes the last pair look current without ever walking live bytes.

### Environment shape
Ruby mill with three roots, sealed snapshot pair, live desk, coverage cards, ops decoy, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, kindle regen after source work.

### Test plan
- test_ds01_token_form
- test_ds02_overlay_listed
- test_ds03_sieve_has_token
- test_ds04_no_pair_token
- test_ds05_full_rel
- test_ds06_alias_holdout
- test_ds07_sorted_names
- test_ds08_json_shape
- test_ds09_empty_dirty
- test_ds10_unmapped_exit
- test_ds11_zz_corrupt
- test_ds12_once_pass

### Drafting guardrails
Do not name seal-pair diffs, basename joins, or vacuous success. Tests must not kindle except recovery, holdout, and fault injection. Punish SEAL_FIRST via remaining desk/seal byte mismatch plus rubric.

### Triviality Ledger
- Seal the dirty desk then kindle — blocked by asserting desk bytes still differ from the newest seal while live tokens appear.
- Hand-written pick.json — blocked by kindle rerun and corrupt-then-kindle recovery.
- Source-only without kindle — emberwell stays stale; R5 source_only.sh.
- Naive patch -i oracle — blocked by full-file writes in solve.sh.

### Per-gate Pitfall Inventory
- RC2: repair paths in LAYOUT.txt name directories, not loom/hitch/vale.
- GX9: grade JSON path/assays and binary records, not boolean flags.
- CR8: kindle is a shell dispatcher; each ruby runner touches one fix symbol.
- R5: tests do not kindle for ordinary scoring; zz recovery only reruns kindle.
- R3: every graded test fails on broken tree.
- P4: SEAL_FIRST decoy punished by rubric.

### Initial Draft Commitments
- environment/gaitmod/stride.rb
- environment/gaitmod/run_loom.rb
- environment/gaitmod/treeio.rb
- environment/joincue/latch.rb
- environment/joincue/run_hitch.rb
- environment/joincue/sheets.rb
- environment/stillbay/vale.rb
- environment/stillbay/run_vale.rb
- environment/stillbay/dust.rb
- environment/fieldnotes/LAYOUT.txt
- environment/fieldnotes/DESK.txt
- environment/opside/SEAL_FIRST.txt
- environment/opside/pairhint.rb
- environment/snapurn/INDEX.txt
- environment/snapurn/seals/n0/lib/fee.rb
- environment/snapurn/seals/n0/lib/tax.rb
- environment/snapurn/seals/n0/doc/fee.rb
- environment/snapurn/seals/n0/notes.md
- environment/snapurn/seals/n1/lib/fee.rb
- environment/snapurn/seals/n1/lib/tax.rb
- environment/snapurn/seals/n1/doc/fee.rb
- environment/snapurn/seals/n1/notes.md
- environment/livefold/lib/fee.rb
- environment/livefold/lib/tax.rb
- environment/livefold/doc/fee.rb
- environment/livefold/notes.md
- environment/lutcards/fee.map
- environment/lutcards/tax.map
- environment/inkvat/.keep
- environment/knit.sh
- environment/Dockerfile
- environment/.dockerignore
- environment/cratepit/wheels
- environment/cratepit/debs
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- instruction.md
- task.toml
- output_contract.toml
- construction_manifest.json
- rubric.txt
- preship/preship.json
- preship/source_only.sh
- preship/decoy_fix.sh
- preship/shortcut_fix.sh

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

```
- path: environment/gaitmod/stride.rb
  symbol: loom
  kind: function
  signature: loom()
  purpose: writes delta.lst from the live desk versus the newest seal
- path: environment/joincue/latch.rb
  symbol: hitch
  kind: function
  signature: hitch()
  purpose: writes sieve.bin and pick.json from delta tokens and sheets
- path: environment/stillbay/vale.rb
  symbol: vale
  kind: function
  signature: vale() -> Integer
  purpose: returns kindle status from pick.json and desk dirt
```

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/gaitmod/stride.rb
    controls_tests: [test_ds01_token_form, test_ds02_overlay_listed, test_ds03_sieve_has_token, test_ds04_no_pair_token]
  - id: B
    path: environment/joincue/latch.rb
    controls_tests: [test_ds05_full_rel, test_ds06_alias_holdout, test_ds07_sorted_names, test_ds08_json_shape]
  - id: C
    path: environment/stillbay/vale.rb
    controls_tests: [test_ds09_empty_dirty, test_ds10_unmapped_exit, test_ds11_zz_corrupt, test_ds12_once_pass]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

#### decoy_manifest

```
- path: environment/opside/SEAL_FIRST.txt
  kind: helper
  rhymes_with: loom
  non_fix_purpose: suggests minting a new seal from the desk before kindle
```

#### code_forbidden_tokens

```
code_forbidden_tokens: [peatwick, livefold, snapurn, inkvat, lutcards, kindle, sieve.bin, pick.json]
```
