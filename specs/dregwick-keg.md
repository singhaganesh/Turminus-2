### Decision
GO — Attempt 1. Debugging repair: Java log mill whose exploded loom still claims kmsg while the packed mill after knit falls through to fallback. Three loci: packed reachability roots, live-table knit exit, packed-jar ceiling exit.

### Metadata
- version: 2
- Task name: dregwick-keg
- Title: Packed mill drops booth
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["java"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["java", "log-mill", "packed-jar", "booth-table"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/dregwick` is the mill. `knit` writes `/app/jarwell/husk.jar`. `loom` and `taste` write `/app/jarwell/taste.json`. `booth` prints live handler names.
- After `knit`, `taste` of `/app/slipcards/kmsg.card` claims booth `kmsg` and kind `own`. Same own-handler rule for json.card and syslog.card.
- After `knit`, every name in `/app/desknote/NAMES.txt` appears in the `booth` listing. A shorter live listing makes `knit` exit non-zero.
- `/app/jarwell/husk.jar` stays at or below the integer in `/app/desknote/CAP.txt`. A jar above that ceiling makes `knit` exit non-zero.
- taste.json keys: booth, kind, note.
- Source fixes under `/app` for modules named from `/app/desknote/ROUTE.txt`. Hand-written taste.json is not enough. Verifier reruns knit, loom, taste, booth.

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
- path: environment/rootwalk/ReachWalk.java
  role: packed class reachability
- path: environment/namelock/TallyGate.java
  role: live listing vs roster exit
- path: environment/bytecue/CapGate.java
  role: packed jar ceiling exit

### fix_frontier
- count: 3
- distribution: rootwalk, namelock, bytecue
- naming_policy: opaque weld_set tint_span rib_n
- forbidden_stems: knit, taste, booth, mill, roster, fallback
- helpers_policy: gildbox SkipCue and HexDump off frontier
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON strings, exit codes, jar size
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: SKIP_SHRINK packs every exploded class

### category_profile
- challenge_family: false_green_rehearsal_window
- bug_family: false_green_rehearsal_window
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: commands, paths, schemas, symptoms, ceiling integer home
- forbidden_instruction_leaks: bytecode reachability, static registrar, skip shrink
- category_specific_hardness_bar: loom claims kmsg while packed taste falls to fallback and knit still exits 0
- category_specific_verifier_risks: test-side javac, hand-written taste.json
- coverage_role: debugging C2 rebuild plus packed mill outcome

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: knit exits 0 while packed taste is fallback
  why_model_misses_it: clean knit plus working loom
  fairness_guardrail: own-handler named for kmsg
- mechanism: deceptive_but_valid_local_evidence
  placement: brim.sh SKIP_SHRINK leftover plus gildbox HexDump
  why_model_misses_it: packing every class restores kmsg
  fairness_guardrail: CAP.txt ceiling
- mechanism: cross_file_cross_format_invariants
  placement: husk.jar vs booth listing vs roster vs taste.json
  why_model_misses_it: edit taste.json only
  fairness_guardrail: verifier reruns taste
- mechanism: stateful_multi_step_dependencies
  placement: source fix then brim.sh knit
  why_model_misses_it: skip rebuild
  fairness_guardrail: packed mill consulted after knit

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: knit then taste kmsg.card
- shortcut_audit: SKIP_SHRINK, hand taste.json, skip hull
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
- sidecar_or_protocol_notes: slipcards bundled

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs are rootwalk/namelock/bytecue
- gx9_contract_risk: low JSON strings and exits
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan
- verifier_command_visible: dregwick knit loom taste booth
- source_fix_intent_visible: pipeline modules in ROUTE.txt
- generated_output_rule_visible: taste.json husk.jar
- exact_formula_home: CAP.txt integer; kind own vs fallback rule in instruction
- schema_home: instruction.md and CARD.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for a Java log mill whose packed knit drops a self-registered booth while exploded loom still claims it

### realism_source
- source_type: real_bug
- evidence_basis: GC sections / R8 unused-class strip dropping static plugin registration
- upstream_or_synthetic_rationale: classic --gc-sections plus static constructor plugin pattern
- minimization_preserves: debug/exploded works, packed mill fallback, shrink still required
- synthetic_exception_review: not required

### Failure topology
Operators see loom still claim kmsg while a successful knit leaves packed taste on fallback. The booth listing after knit is short versus the roster. Unused pretty printers still sit in the exploded tree, so turning off packing looks like an ops shortcut and then blows the packed mill ceiling.

### Environment shape
Java mill CLI, three packer-gate roots, exploded loom tree, packed mill jar, roster and ceiling notes, log cards, gildbox decoy classes, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, hull rebuild.

### Test plan
- test_dw01_ring_claim
- test_dw02_leaf_claim
- test_dw03_auth_claim
- test_dw04_table_span
- test_dw05_short_exit
- test_dw06_mass_bound
- test_dw07_mass_exit
- test_dw08_held_ring
- test_dw09_corrupt_vat
- test_dw10_miss_fb
- test_dw11_obj_shape
- test_dw12_pair_parity

### Drafting guardrails
Do not name bytecode reachability, static registrar, or skip shrink. Tests must not javac. Punish SKIP_SHRINK via ceiling plus rubric.

### Triviality Ledger
- SKIP_SHRINK / copy every exploded class — blocked by CAP.txt ceiling and husk.jar size test.
- Hand-written taste.json — blocked by taste rerun and corrupt-then-knit recovery.
- Source-only without hull — packed mill stays stale; R5 source_only.sh.
- SkipCue.java — blocked by ceiling, not by deleting gildbox from source.

### Per-gate Pitfall Inventory
- RC2: repair paths in ROUTE.txt name directories, not weld_set/tint_span/rib_n.
- GX9: grade JSON strings and exits, not boolean flags.
- CR8: KnitMain wraps weld_set; TallyGate wraps tint_span; CapGate wraps rib_n.
- R5: tests do not hull; zz recovery only reruns knit.
- R3: every graded test fails on broken tree.
- P4: SKIP_SHRINK decoy punished by rubric.

### Initial Draft Commitments
- environment/rootwalk/ReachWalk.java
- environment/namelock/TallyGate.java
- environment/bytecue/CapGate.java
- environment/hitchrun/Main.java
- environment/hitchrun/KnitMain.java
- environment/hitchrun/TasteRun.java
- environment/hitchrun/BoothRun.java
- environment/hitchrun/Rib.java
- environment/fmtcells/JsonBooth.java
- environment/fmtcells/SysBooth.java
- environment/fmtcells/KmsgBooth.java
- environment/fmtcells/FallBooth.java
- environment/gildbox/HexDump.java
- environment/gildbox/TracePad.java
- environment/gildbox/SkipCue.java
- environment/floorcue/Floor.java
- environment/brim.sh
- environment/desknote/ROUTE.txt
- environment/desknote/VERBS.txt
- environment/desknote/CARD.txt
- environment/desknote/CAP.txt
- environment/desknote/NAMES.txt
- environment/desknote/NOTE.txt
- environment/slipcards/kmsg.card
- environment/slipcards/json.card
- environment/slipcards/syslog.card
- environment/Dockerfile
- environment/.dockerignore
- environment/vrfypkgs/wheels
- environment/vrfypkgs/debs
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

- path: environment/rootwalk/ReachWalk.java
  symbol: weld_set
  kind: function
  signature: weld_set(Path a) throws Exception
  purpose: collects packed class names
- path: environment/namelock/TallyGate.java
  symbol: tint_span
  kind: function
  signature: tint_span(Path a, Path b, Path c) throws Exception
  purpose: returns knit status for listing length
- path: environment/bytecue/CapGate.java
  symbol: rib_n
  kind: function
  signature: rib_n(Path a, Path b) throws Exception
  purpose: returns knit status for packed length

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/rootwalk/ReachWalk.java
    controls_tests: [test_dw01_ring_claim, test_dw02_leaf_claim, test_dw08_held_ring, test_dw12_pair_parity]
  - id: B
    path: environment/namelock/TallyGate.java
    controls_tests: [test_dw04_table_span, test_dw05_short_exit, test_dw10_miss_fb, test_dw11_obj_shape]
  - id: C
    path: environment/bytecue/CapGate.java
    controls_tests: [test_dw03_auth_claim, test_dw06_mass_bound, test_dw07_mass_exit, test_dw09_corrupt_vat]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

#### decoy_manifest

- path: environment/gildbox/SkipCue.java
  kind: helper
  rhymes_with: weld_set
  non_fix_purpose: leftover local pack switch
- path: environment/gildbox/HexDump.java
  kind: helper
  rhymes_with: rib_n
  non_fix_purpose: unused pretty printer padding

#### code_forbidden_tokens

```
code_forbidden_tokens: [dregwick, knit, loom, taste, booth, jarwell, taste.json, husk.jar, slipcards, kmsg.card, json.card, syslog.card, kmsg, fallback, own, ROUTE.txt, VERBS.txt, CARD.txt, CAP.txt, NAMES.txt, desknote, pipeline, modules, verifier, packed, mill, handler, roster, ceiling, kind, note]
```
