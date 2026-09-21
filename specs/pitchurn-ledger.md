### Decision
GO — Attempt 1. Debugging repair: Java gear mill whose anneal walk stays green while a second stow of an unchanged reel stores the stream again. Three loci: bound digest emit, signed window emit, cold-index merge.

### Metadata
- version: 2
- Task name: pitchurn-ledger
- Title: Unchanged reel stored twice
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["java"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["java", "gear-mill", "silo-tally", "content-store"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/pitchurn` is the mill. `anneal` reads `/app/gearpit/live.gear` and walks `/app/urnbay`. `stow` writes objects under `/app/urnbay`. `draw` writes destination bytes. `census` rewrites `/app/urnbay/tally.json`.
- After a second stow of a reel whose bytes already sit in the silo, `reuse_frac` is at or above `0.80`.
- Mean piece length for a never-seen reel is at or below `2048`.
- A stow that writes a full new copy of already-siloed bytes exits non-zero.
- `draw DEST` writes the same bytes as the source reel.
- `tally.json` card: `reel`, `bytes_in`, `bytes_stored`, `reuse_frac`, `mean_piece`, `piece_count`. Numeric values are base-10 strings.
- Source fixes under `/app` for modules named in `/app/deskfold/ROUTE.txt`. Hand-written tally files are not enough. Verifier reruns mill verbs in `/app/deskfold/BUILD.txt`.

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
  role: Java+python offline image
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/oxemit/RibGen.java
  role: digest emit
- path: environment/nincut/VatGen.java
  role: window emit
- path: environment/coldrib/DuskGen.java
  role: silo walk emit

### fix_frontier
- count: 3
- distribution: oxemit, nincut, coldrib
- naming_policy: opaque weld tint loom
- forbidden_stems: anneal, stow, tally, reuse
- helpers_policy: corkpit Floor off frontier
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON decimal strings, exit codes, byte equality
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: copy packurn/legacy.gear over live.gear

### category_profile
- challenge_family: false_green_rehearsal_window
- bug_family: false_green_rehearsal_window
- profile_name: filesystem_state_reconstruction
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: bound digest, signed window, cold-only walk
- category_specific_hardness_bar: anneal walked while second stow stores the unchanged reel
- category_specific_verifier_risks: test-side javac, hand tally
- coverage_role: debugging C2 rebuild plus reuse outcome

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: anneal prints walked and draw stays byte-correct
  why_model_misses_it: restore green hides store growth
  fairness_guardrail: reuse_frac named
- mechanism: deceptive_but_valid_local_evidence
  placement: packurn/legacy.gear plus millcue note
  why_model_misses_it: old gear restores reuse
  fairness_guardrail: mean_piece cap
- mechanism: cross_file_cross_format_invariants
  placement: live.gear vs generated Seal/Slice/Span vs silobay idx
  why_model_misses_it: edit tally.json only
  fairness_guardrail: verifier reruns stow
- mechanism: stateful_multi_step_dependencies
  placement: source fix then stoke.sh anneal
  why_model_misses_it: skip rebuild
  fairness_guardrail: generated classes overwritten on anneal

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: restow unchanged reel and compare object growth
- shortcut_audit: legacy.gear, hand tally, skip stoke
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
- sidecar_or_protocol_notes: reels bundled under reelwell

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs are oxemit/nincut/coldrib
- gx9_contract_risk: low JSON decimal strings
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan
- verifier_command_visible: pitchurn anneal stow draw census
- source_fix_intent_visible: pipeline modules in ROUTE.txt
- generated_output_rule_visible: tally.json silobay objects
- exact_formula_home: reuse_frac 0.80 and mean_piece 2048 in instruction
- schema_home: instruction.md and SCHEMA.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Java gear mill whose anneal walk stays green while a second stow of an unchanged reel stores the stream again

### realism_source
- source_type: synthetic_exception
- evidence_basis: content-defined backup stores that retile after a gear change but keep restores green
- upstream_or_synthetic_rationale: cannot ship a vendor dedup appliance
- minimization_preserves: anneal walked, reuse near zero, restore correct
- synthetic_exception_review: legacy.gear is a realistic ops revert

### Failure topology
Operators see anneal finish and draw stay byte-correct after a gear tighten, yet a second stow of an unchanged reel writes almost every byte again. The silo index is internally consistent. Storage growth reads as ordinary intake.

### Environment shape
Java mill CLI, three emit roots, live and legacy gear packs, silobay objects, reelwell fixtures, decoy floor note, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, stoke rebuild.

### Test plan
- test_pu01_twice_blob
- test_pu02_held_frac
- test_pu03_fresh_span
- test_pu04_sink_match
- test_pu05_dirty_exit
- test_pu06_card_keys
- test_pu07_hi_bit
- test_pu08_cold_keep
- test_pu09_once_pass
- test_pu10_zz_corrupt
- test_pu11_card_obj
- test_pu12_floor_ignored

### Drafting guardrails
Do not name bound digest, signed window, or cold-only walk. Tests must not javac. Punish legacy.gear via mean_piece plus rubric.

### Triviality Ledger
- Copy legacy.gear over live.gear — blocked by mean_piece cap on never-seen intake.
- Hand-written tally.json — blocked by stow rerun and corrupt-then-stow recovery.
- Source-only without stoke — generated classes stay stale; R5 source_only.sh.
- Floor.java MIN.txt — blocked by reuse_frac 0.80 not the floor file.

### Per-gate Pitfall Inventory
- RC2: repair paths in ROUTE.txt name directories, not weld/tint/loom.
- GX9: grade decimal strings and exits, not boolean flags.
- CR8: StowRun wraps Seal+Slice; WalkRun wraps Span; Main dispatches.
- R5: tests do not stoke; zz recovery only reruns stow.
- R3: every graded test fails on broken tree.
- P4: legacy.gear decoy punished by rubric.

### Initial Draft Commitments
- environment/oxemit/RibGen.java
- environment/nincut/VatGen.java
- environment/coldrib/DuskGen.java
- environment/maltcli/Main.java
- environment/maltcli/StowRun.java
- environment/maltcli/WalkRun.java
- environment/maltcli/Gear.java
- environment/maltcli/DrawRun.java
- environment/maltcli/CardRun.java
- environment/corkpit/Floor.java
- environment/stoke.sh
- environment/packurn/live.gear
- environment/packurn/legacy.gear
- environment/millcue/ROUTE.txt
- environment/millcue/SCHEMA.txt
- environment/millcue/NOTE.txt
- environment/millcue/MIN.txt
- environment/reelwell/stable.bin
- environment/reelwell/plain.bin
- environment/reelwell/brine.bin
- environment/silobay/hot/.keep
- environment/Dockerfile
- environment/.dockerignore
- environment/offpack/wheels
- environment/offpack/debs
- instruction.md
- task.toml
- output_contract.toml
- construction_manifest.json
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- rubric.txt
- preship/preship.json
- preship/source_only.sh
- preship/decoy_fix.sh
- preship/shortcut_fix.sh
- preship/alt_solution.sh

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

- path: environment/oxemit/RibGen.java
  symbol: weld
  kind: function
  signature: weld(PrintWriter a) throws Exception
  purpose: writes Seal.java
- path: environment/nincut/VatGen.java
  symbol: tint
  kind: function
  signature: tint(PrintWriter a) throws Exception
  purpose: writes Slice.java
- path: environment/coldrib/DuskGen.java
  symbol: loom
  kind: function
  signature: loom(PrintWriter a) throws Exception
  purpose: writes Span.java

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/oxemit/RibGen.java
    controls_tests: [test_pu02_held_frac, test_pu04_sink_match, test_pu09_once_pass, test_pu11_card_obj]
  - id: B
    path: environment/nincut/VatGen.java
    controls_tests: [test_pu03_fresh_span, test_pu06_card_keys, test_pu07_hi_bit, test_pu12_floor_ignored]
  - id: C
    path: environment/coldrib/DuskGen.java
    controls_tests: [test_pu01_twice_blob, test_pu05_dirty_exit, test_pu08_cold_keep, test_pu10_zz_corrupt]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

#### decoy_manifest

- path: environment/corkpit/Floor.java
  kind: helper
  rhymes_with: weld
  non_fix_purpose: compares reuse against millcue/MIN.txt
- path: environment/packurn/legacy.gear
  kind: config-reader
  rhymes_with: tint
  non_fix_purpose: stores the prior gear pack

#### code_forbidden_tokens

```
code_forbidden_tokens: [pitchurn, anneal, packurn, live.gear, mill, silobay, stow, reel, objects, draw, destination, census, tally.json, intake, pieces, reuse_frac, bytes_stored, bytes_in, walked, millcue, ROUTE.txt, SCHEMA.txt, silo, mean_piece, piece_count, DEST]
```
