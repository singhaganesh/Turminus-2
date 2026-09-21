### Decision
GO — Attempt 1. Debugging repair: Java crash-report silo whose power-loss drill leaves a pin row for a blob that never landed. Three loci: recipe emit order for stable-storage pushes, wake completeness walk, pull padding slice.

### Metadata
- version: 2
- Task name: crumbark-silo
- Title: Pin lands before blob
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["java"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["java", "silo", "durability", "wake"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/crumbark` is the mill. `tamp` rebuilds classes `lade`, `wake`, `pull`, and `nick` run.
- Clean `lade` of `/app/inbox` slip then `wake` exits 0; id appears in `held`; `pull` returns slip bytes.
- Durability: a listed id must pull byte-complete; otherwise wake omits it, exits non-zero, and the record is void. CARD.txt states pin layout and held-id encoding.
- `wake.json` keys `held`, `note`, `kind` per `/app/fieldslip/CARD.txt`.
- Source fixes under `/app` for trees in `/app/fieldslip/LINKS.txt`. Static silo files are not enough. Verifier reruns tamp, lade, wake, pull, nick.

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

- path: environment/recipit/LoomCue.java
  role: recipe emit for ForceSeq names
- path: environment/markwell/HueWalk.java
  role: wake completeness
- path: environment/siltpage/MistSpan.java
  role: pull slice

### fix_frontier

- count: 4
- distribution: recipit, markwell, siltpage, hitchbay
- naming_policy: opaque rib_q orb_n tint_k
- forbidden_stems: crumbark, tamp, lade, wake, pull, nick, held, blob, pin
- helpers_policy: PauseCue off frontier
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON arrays, exit codes, byte equality
- forbidden_assertion_styles: boolean answer keys

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: sleep-retry on pull; skip tamp

### category_profile

- challenge_family: state_recovery_crash_consistency
- bug_family: state_recovery_crash_consistency
- profile_name: state_recovery_crash_consistency
- allowed_instruction_disclosures: crash drill, durability outcome, wake/pull commands, wake.json schema, source-fix trees
- forbidden_instruction_leaks: force order, compute-rank sort, fsync, CRC, padding, generator emit
- category_specific_hardness_bar: nick reports committed id whose pull is zeros unless emit order, wake check, and pull slice all hold
- category_specific_verifier_risks: flaky kill, test-side javac, hand-written silo
- coverage_role: debugging C2 rebuild plus crash-injected silo

### difficulty_mechanism_plan

- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: wake exits 0 while pull of held is zeros
  why_model_misses_it: clean lade is fine
  fairness_guardrail: nick drill is a public verb
- mechanism: deceptive_but_valid_local_evidence
  placement: retrycue PauseCue sleep then pull again
  why_model_misses_it: looks like a flaky read
  fairness_guardrail: zeros never appear later
- mechanism: cross_file_cross_format_invariants
  placement: pin row vs blob extent vs wake.json held
  why_model_misses_it: edit wake.json only
  fairness_guardrail: verifier reruns wake and pull
- mechanism: stateful_multi_step_dependencies
  placement: tamp regenerates ForceSeq then javac
  why_model_misses_it: skip rebuild
  fairness_guardrail: packed classes consulted after tamp

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: tamp then lade then nick then wake then pull
- shortcut_audit: PauseCue retry, hand wake.json, skip tamp
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
- sidecar_or_protocol_notes: inbox slips bundled

### satisfiability_risk

- rc2_planned_name_risk: low — fix dirs recipit/markwell/siltpage
- gx9_contract_risk: low JSON arrays and exits
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan

- verifier_command_visible: crumbark tamp lade wake pull nick
- source_fix_intent_visible: trees in LINKS.txt
- generated_output_rule_visible: wake.json blob.bin pin.bin
- exact_formula_home: CARD.txt kind live vs void
- schema_home: instruction.md and CARD.txt

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- justification_if_none: no promoted reference for a Java silo whose commit pin is pushed stable before data pages, with a recipe-emitted force sequence and wake that trusts the pin

### realism_source

- source_type: real_bug
- evidence_basis: WAL/commit-marker vs data fsync order (PostgreSQL/InnoDB class of bugs)
- upstream_or_synthetic_rationale: durability ordering plus torn-write checks
- minimization_preserves: pin durable while blob pending, wake trusts pin, pull pads zeros
- synthetic_exception_review: not required

### Failure topology
Operators see nick then wake list a new id while pull of that id is zeros or short. Older records that finished both pushes stay readable. Wake still exits 0. A leftover PauseCue retry makes the short read look transient.

### Environment shape
Java mill CLI, recipe hearth that emits ForceSeq, blob page walker, pin wake walker, retry helper, silo notes, inbox slips, offline wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier venv, solve.sh, task.toml allow_internet false, brimvat rebuild.

### Test plan
- test_vx01_full_copy — clean lade then pull matches slip
- test_vx02_tide_gap — nick then wake 0 and held all complete
- test_vx03_short_rc — planted short blob, wake non-zero
- test_vx04_pack_len — pull length equals slip length
- test_vx05_seed_keep — prior slip still readable
- test_vx06_tag_set — kind and note from CARD.txt
- test_vx07_omit_bad — torn id absent from held
- test_vx08_extra_oak — grade-time slip
- test_vx09_obj_keys — wake.json keys
- test_vx10_span_len — no pad tail
- test_vx11_hue_gap — pin without blob
- test_vx12_keep_old — older ids survive nick
- test_vx13_void_span — zero-filled body rejected for held

### Drafting guardrails
Do not name force order, compute rank, fsync, CRC, or padding. Tests must not tamp except they must not tamp at all. Punish PauseCue via suite plus rubric.

### Triviality Ledger

- PauseCue sleep-retry — blob never lands; zeros stay; rubric names retrycue.
- Hand-written wake.json — wake rerun and corrupt-then-wake recovery.
- Source-only without tamp — ForceSeq.class stays pin-first; R5 source_only.sh.
- Trust pin only — torn fixture still listed in held.

### Per-gate Pitfall Inventory

- RC2: repair paths in LINKS.txt name directories, not rib_q/orb_n/tint_k.
- GX9: grade JSON arrays and exits, not boolean flags.
- CR8: StowRun wraps rib_q via ForceSeq; StirRun wraps orb_n; YankRun wraps tint_k.
- R5: tests do not tamp.
- R3: every graded test fails on broken tree.
- P4: PauseCue decoy punished by rubric.

### Initial Draft Commitments

- environment/recipit/LoomCue.java
- environment/recipit/steps.loom
- environment/recipit/ForceSeq.java
- environment/markwell/HueWalk.java
- environment/siltpage/MistSpan.java
- environment/hitchbay/StowRun.java
- environment/hitchbay/StirRun.java
- environment/hitchbay/YankRun.java
- environment/hitchbay/CutRun.java
- environment/hitchbay/DeskMain.java
- environment/hitchbay/RibChan.java
- environment/hitchbay/Crc.java
- environment/retrycue/PauseCue.java
- environment/fieldslip/LINKS.txt
- environment/fieldslip/VERBS.txt
- environment/fieldslip/CARD.txt
- environment/fieldslip/NOTE.txt
- environment/inbox/seed.slip
- environment/inbox/prior.slip
- environment/brimvat.sh
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

- path: environment/recipit/LoomCue.java
  symbol: rib_q
  kind: function
  signature: rib_q(Path a) throws Exception
  purpose: emits ordered channel names for ForceSeq
- path: environment/markwell/HueWalk.java
  symbol: orb_n
  kind: function
  signature: orb_n(Path a, Path b, Path c) throws Exception
  purpose: writes wake.json and returns status
- path: environment/siltpage/MistSpan.java
  symbol: tint_k
  kind: function
  signature: tint_k(Path a, byte[] b) throws Exception
  purpose: returns payload bytes for an id

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/recipit/LoomCue.java
    controls_tests: [test_vx01_full_copy, test_vx02_tide_gap, test_vx08_extra_oak, test_vx12_keep_old]
  - id: B
    path: environment/markwell/HueWalk.java
    controls_tests: [test_vx03_short_rc, test_vx07_omit_bad, test_vx09_obj_keys, test_vx11_hue_gap]
  - id: C
    path: environment/siltpage/MistSpan.java
    controls_tests: [test_vx04_pack_len, test_vx05_seed_keep, test_vx06_tag_set, test_vx10_span_len, test_vx13_void_span]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

#### decoy_manifest

- path: environment/retrycue/PauseCue.java
  kind: helper
  rhymes_with: tint_k
  non_fix_purpose: sleeps then reads again
- path: environment/hitchbay/Crc.java
  kind: helper
  rhymes_with: orb_n
  non_fix_purpose: crc32 of a byte span

#### code_forbidden_tokens

```
code_forbidden_tokens: [crumbark, silo, CLI, power-loss, drill, sources, trees, LINKS.txt, copies, blob.bin, pin.bin, wake.json, tamp, classes, lade, wake, pull, nick, verifier, VERBS.txt, Schema, CARD.txt, slip, inbox, held, disk, pin, row, blob, grade, note, kind, body, fieldslip, overnight]
```
