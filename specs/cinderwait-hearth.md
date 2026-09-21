### Decision
GO — Attempt 1. Debugging repair: Java diagnostic mill whose draft jar records a gather word while the ship jar stores 0. Three loci: wait observation, hopper publish onto the wait word, ship runner stamp and mute exit.

### Metadata
- version: 2
- Task name: cinderwait-hearth
- Title: Ship mill stores zero
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["java"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["java", "ship-mill", "gather-word", "kindle-jar"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/cinderwait` is the mill. `kindle` writes `/app/jarhearth/ship.jar` and `/app/jarhearth/draft.jar`. `watch` writes `/app/jarhearth/watch.json`. `peek` prints a decimal gather word.
- After `kindle`, ship `watch` of a published bag stores the wait-board integer the packed mill gathers (not `0`, not the first-line token).
- `peek` of a published bag prints the same gather word.
- A bag whose gatherer never publishes makes `watch` exit non-zero and leaves no success watch.json.
- watch.json keys: seen, bag, note.
- Source fixes under `/app` for modules named from `/app/opslip/ROUTE.txt`. Hand-written watch.json is not enough. Verifier reruns kindle, watch, peek.
- After kindle, MARK.txt stamp must sit inside ship.jar. Missing stamp makes watch exit non-zero.

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
- path: environment/tarnpit/Tarn.java
  role: wait observation
- path: environment/hopcue/Hopper.java
  role: publish onto wait word
- path: environment/watchbay/ShipMain.java
  role: mute exit and stamp gate

### fix_frontier
- count: 3
- distribution: tarnpit, hopcue, watchbay
- naming_policy: opaque mira feed rib_n
- forbidden_stems: watch, peek, kindle, seen, gather
- helpers_policy: Pacer and Rill off frontier
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON integers, exit codes, peek stdout
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: nap in the wait loop or gutting the ship kiln

### category_profile
- challenge_family: false_green_rehearsal_window
- bug_family: false_green_rehearsal_window
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: commands, paths, schemas, symptoms, stamp home
- forbidden_instruction_leaks: volatile, hoist, LICM, sleep workaround
- category_specific_hardness_bar: draft jar records the gather word while ship jar stores 0 and kindle still exits 0
- category_specific_verifier_risks: test-side javac, hand-written watch.json
- coverage_role: debugging C2 rebuild plus ship mill outcome

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: kindle exits 0 while ship watch stores 0
  why_model_misses_it: draft jar is green
  fairness_guardrail: ship watch named
- mechanism: deceptive_but_valid_local_evidence
  placement: softmill Pacer.nap
  why_model_misses_it: pause looks like it wakes a hang
  fairness_guardrail: ship mill still stores 0
- mechanism: cross_file_cross_format_invariants
  placement: keld publish vs wait vs stamp
  why_model_misses_it: edit watch.json only
  fairness_guardrail: verifier reruns watch
- mechanism: stateful_multi_step_dependencies
  placement: source fix then kindle
  why_model_misses_it: skip rebuild
  fairness_guardrail: packed mill consulted after kindle

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: kindle then watch alpha.bag
- shortcut_audit: Pacer.nap, hand watch.json, skip kindle
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
- sidecar_or_protocol_notes: hopbags bundled

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs are tarnpit/hopcue/watchbay
- gx9_contract_risk: low JSON integers and exits
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan
- verifier_command_visible: cinderwait kindle watch peek
- source_fix_intent_visible: pipeline modules in ROUTE.txt
- generated_output_rule_visible: watch.json ship.jar
- exact_formula_home: CARD.txt gather word equals bag first integer
- schema_home: instruction.md and CARD.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Java mill whose draft jar records a background gather word while the ship jar stores the opening zero after a high-optimisation kiln pass

### realism_source
- source_type: real_bug
- evidence_basis: compiler as-if LICM of a non-volatile poll in a wait loop; Java JMM volatile publication
- upstream_or_synthetic_rationale: classic debug-vs-release wait-loop; kiln models release LICM deterministically
- minimization_preserves: draft observes the word, ship stores 0, nap does not count as a fix
- synthetic_exception_review: not required

### Failure topology
Operators see draft watch finish with the bag word while ship watch stores 0 or hangs. Kindle can still exit 0. A mute bag must fail closed. Peek must still print the published word even when watch is wrong, so the publish path and the wait path can disagree.

### Environment shape
Java mill CLI, ship kiln, draft jar, wait board, hopper, ship runner, hop bags, opslip notes, Pacer decoy, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, kindle rebuild.

### Test plan
- test_cw01_oak_hit
- test_cw02_elm_hit
- test_cw03_ash_hit
- test_cw04_seal_jar
- test_cw05_mute_rc
- test_cw06_mute_vat
- test_cw07_held_hit
- test_cw08_held_list
- test_cw09_elm_list
- test_cw10_seal_rc
- test_cw11_corrupt_vat
- test_cw12_side_hit

### Drafting guardrails
Do not name volatile, hoist, LICM, or nap-as-fix. Tests must not kindle for ordinary scoring. Punish Pacer via suite plus rubric.

### Triviality Ledger
- Pacer.nap in the wait body — ship kiln still drops the reload; ship watch stays 0.
- Hand-written watch.json — blocked by watch rerun and corrupt-then-watch recovery.
- Source-only without kindle — packed mill stays hoisted; R5 source_only.sh.
- Gutting KilnShip — rill rewrite plus MARK stamp missing, watch exits non-zero.

### Per-gate Pitfall Inventory
- RC2: repair paths in ROUTE.txt name directories, not mira/feed/rib_n.
- GX9: grade JSON integers and exits, not boolean flags.
- CR8: Glue wraps mira+feed; ShipMain wraps rib_n only.
- R5: tests do not kindle except stamp/mute fault injection.
- R3: every graded test fails on broken tree.
- P4: Pacer nap decoy punished by rubric.

### Initial Draft Commitments
- environment/tarnpit/Tarn.java
- environment/hopcue/Hopper.java
- environment/watchbay/ShipMain.java
- environment/watchbay/Glue.java
- environment/draftcue/DraftMain.java
- environment/peekcue/PeekMain.java
- environment/kilnrib/KilnShip.java
- environment/rillcue/Rill.java
- environment/softmill/Pacer.java
- environment/opslip/ROUTE.txt
- environment/opslip/VERBS.txt
- environment/opslip/CARD.txt
- environment/opslip/MARK.txt
- environment/opslip/NOTES.txt
- environment/hopbags/alpha.bag
- environment/hopbags/elm.bag
- environment/hopbags/mute.bag
- environment/kindle.sh
- environment/Dockerfile
- environment/.dockerignore
- environment/pkgdrop/wheels (copied)
- environment/pkgdrop/debs (copied)
- instruction.md
- task.toml
- output_contract.toml
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- construction_manifest.json
- rubric.txt
- preship/preship.json
- preship/source_only.sh
- preship/decoy_fix.sh
- preship/shortcut_fix.sh
- preship/alt_solution.sh

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

- path: environment/tarnpit/Tarn.java
  symbol: mira
  kind: function
  signature: mira()
  purpose: spins on the board word then returns it
- path: environment/hopcue/Hopper.java
  symbol: feed
  kind: function
  signature: feed(Tarn t, int w)
  purpose: publishes a word onto the board
- path: environment/watchbay/ShipMain.java
  symbol: rib_n
  kind: function
  signature: rib_n(String[] a) throws Exception
  purpose: runs ship watch, writes json, returns status

#### flipping_point_contract

locations:
  - id: A
    path: environment/tarnpit/Tarn.java
    controls_tests: [test_cw01_oak_hit, test_cw02_elm_hit, test_cw07_held_hit, test_cw11_corrupt_vat]
  - id: B
    path: environment/hopcue/Hopper.java
    controls_tests: [test_cw03_ash_hit, test_cw12_side_hit, test_cw09_elm_list, test_cw08_held_list]
  - id: C
    path: environment/watchbay/ShipMain.java
    controls_tests: [test_cw05_mute_rc, test_cw06_mute_vat, test_cw04_seal_jar, test_cw10_seal_rc]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/softmill/Pacer.java
  kind: helper
  rhymes_with: mira
  non_fix_purpose: optional pause helper leftover from hang drills
- path: environment/rillcue/Rill.java
  kind: helper
  rhymes_with: mira
  non_fix_purpose: kiln self probe loop the ship pass must still tighten

#### code_forbidden_tokens

code_forbidden_tokens: [cinderwait, pipeline, ROUTE.txt, jarhearth, watch.json, watch, mill, ship.jar, kindle, peek, VERBS.txt, opslip, CARD.txt, hopbags, alpha.bag, draft.jar, gather, seen, gatherer, MARK.txt, bag, stamp, handwritten, stdout]
