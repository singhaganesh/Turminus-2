### Decision
GO — Attempt 1. Debugging repair: content-addressed decoder emit keyed only on sheet bytes plus a frozen stamp, so GROUP handling never lands in `/app/incpit` while `bake` logs `served` and exits 0. Three loci: inner GROUP emit, mill identity in the urn key, refuse a `served` hit when emitter sources moved.

### Metadata
- version: 2
- Task name: moldwire-cask
- Title: Stale decoder cask
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["java", "c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["java", "c", "decoder-emit", "content-address", "wire-groups"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/moldwire bake` refreshes `/app/incpit/*.inc` from `/app/sheetpit/*.sheet`.
- `/app/bin/moldwire skim` writes `/app/jsonpit/skim.json` from `/app/duskpit/dusk.bin` (optional extra frame path under `/app/duskpit` is in sheet.rules).
- `/app/bin/moldwire` remains compiled ELF.
- Inner GROUP fields decode to packed integer values as decimal strings.
- `bake` logging `served` after emitter sources moved must exit non-zero.
- New sheet after the last bake appears as a new `.inc` after one bake process.
- Source fixes under `/app` required. Static `.inc` or JSON will not survive bake.
- Grammar in `/app/dockotes/sheet.rules`. Module trees in `/app/dockotes/tree.map`.

### platform_files

- path: task.toml
  role: metadata; must set `[environment] allow_internet = false`
- path: instruction.md
  role: natural public task prompt
- path: output_contract.toml
  role: local output declaration
- path: tests/test.sh
  role: verifier entrypoint; invoke pre-installed tools only
- path: tests/test_outputs.py
  role: domain verifier
- path: solution/solve.sh
  role: oracle
- path: environment/Dockerfile
  role: gcc+JDK+pytest offline image
- path: construction_manifest.json
  role: local authoring artifact

### task_files

- path: environment/slagbin/SlotEmit.java
  role: GROUP/field C emit
- path: environment/piturn/Dig.java
  role: urn identity mix
- path: environment/dockcli/Gate.java
  role: served-hit status
- path: environment/dockcli/Bake.java
  role: bake orchestration
- path: environment/ribwire/run.c
  role: skim runtime
- path: environment/dockcli/main.c
  role: ELF trampoline

### fix_frontier

- count: 3
- distribution: slagbin, piturn, dockcli (Gate)
- naming_policy: opaque op_inner / mix_id / n_hit
- forbidden_stems: moldwire, bake, served, cache, version
- helpers_policy: SheetScan/Store co-residents; cold.note is ops log
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON artifacts, exit codes, ELF magic, generated .inc presence
- forbidden_assertion_styles: boolean answer keys

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: wipe urn once or bump a stamp string

### category_profile

- challenge_family: generated_artifact_cache_identity
- bug_family: generated_artifact_cache_identity
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: commands, paths, ELF rule, served-hit fail, inner keys, new .inc
- forbidden_instruction_leaks: stamp constant, mill digest, length-prefix recipe, wipe-urn workaround
- category_specific_hardness_bar: lockfiles/generated artifacts/build graph/cache invalidation coordinate
- category_specific_verifier_risks: pin-one-stamp, delete-urn, hand-written .inc
- coverage_role: debugging C2 rebuild-before-claim with content-addressed emit

### difficulty_mechanism_plan

- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI, sheet.rules/tree.map visible
- mechanism: false_green_intermediate_states
  placement: bake exits 0 and logs served while inner JSON keys stay empty
  why_model_misses_it: agents trust bake success
  fairness_guardrail: instruction names empty inner keys and served
- mechanism: deceptive_but_valid_local_evidence
  placement: cold.note wipe-urn note; rel-3 stamp looks like a version
  why_model_misses_it: clearing the urn regenerates once
  fairness_guardrail: second mill-identity change still served unless mix_id binds emitter sources
- mechanism: cross_file_cross_format_invariants
  placement: sheets vs generated C vs dusk.bin vs skim JSON
  why_model_misses_it: edits JSON only
  fairness_guardrail: grader reruns skim; corrupt-then-bake recovery
- mechanism: stateful_multi_step_dependencies
  placement: Java source then riv.sh javac+gcc+bake
  why_model_misses_it: skip riv.sh
  fairness_guardrail: ELF at /app/bin/moldwire required

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert binds mill sources into urn identity, emits GROUP length prefix, riv.sh
- shortcut_audit: wipe urn, bump rel-3, hand skim.json, shell replace ELF
- ablation_plan: revert each of three Java loci
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
- sidecar_or_protocol_notes: sheets, vault frame, and urn bundled

### satisfiability_risk

- rc2_planned_name_risk: low — slagbin/piturn/dockcli
- gx9_contract_risk: low — no scenario-value tables in instruction
- cr1_symbol_frontier_risk: low — op_inner mix_id n_hit
- hidden_contract_risk: low — sheet.rules schema

### actionability_plan

- verifier_command_visible: moldwire bake and skim
- source_fix_intent_visible: Java and C trees from tree.map
- generated_output_rule_visible: incpit incs, jsonpit skim.json, ELF
- exact_formula_home: packed integers as decimal strings in sheet.rules
- schema_home: instruction.md and sheet.rules

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- justification_if_none: no promoted reference for a Java emitter plus C trampoline with a content-addressed decoder cask

### realism_source

- source_type: real_bug
- evidence_basis: protobuf/codegen caches keyed on .proto bytes but not protoc plugin identity; nested message length prefix omitted after a "nested fields" patch that never rebuilt
- upstream_or_synthetic_rationale: minimized from common codegen-cache misses (protoc plugins, flatbuffers generators) without shipping those trees
- minimization_preserves: green bake, unchanged generated units, nested decode empty, wipe-cache decoy
- synthetic_exception_review: not required

### Failure topology
Bake reports served and exits 0 while GROUP fields on a sealed frame skim as empty strings. Sheet files are untouched so a description-only urn key never misses. A frozen stamp string looks like the mill identity. Wiping the urn once regenerates and hides the next emitter change. Inner wire layout (u16be group length then fields) is independent of the urn mix.

### Environment shape
Java emit core, urn identity mix, bake gate, C trampoline and skim runtime, sheetpit sheets, incpit generated incs, duskpit frames, dockotes sheet.rules/tree.map/cold.note, riv.sh.

### Required artifacts
instruction, tests, Dockerfile with JDK copied onto gcc plus pytest/tmux, solve.sh, task.toml allow_internet false, construction_manifest, rubric.txt, preship probes.

### Test plan
- elf plus skim of dusk.bin inner values
- holdout sheet + frame
- served hit after emitter source move must fail (or miss and rewrite incs)
- corrupt incs then bake recovers
- added sheet creates .inc
- JSON keys
- empty inner rejected
- second bake stable
- pair inner fields
- fault sheet exit
- incs differ after mill identity change

### Drafting guardrails
Do not name stamp bump, mill digest, length-prefix, or wipe-urn as the fix. No # BUG. Oracle comments stay neutral.

### Triviality Ledger

- Wipe `/app/piturn/store` — blocked by a second emitter-source move that still `served` unless mix_id binds slagbin.
- Bump `rel-3` only — nested emit still empty; decoy probe.
- Hand-write skim.json / .inc — corrupt-then-bake plus held-out frame.
- Shell replace ELF — ELF magic after riv.sh.
- Skip javac/gcc — source_only R5.

### Per-gate Pitfall Inventory

- RC1: oracle rewrites three Java bodies, not a delete.
- RC2: fix dirs slagbin/piturn/dockcli; no broken_* names.
- RC3: domain JSON values and exits, not existence only.
- RC4: expected integers live in tests, not goldens.
- RC5: no answer-shaped fixtures.
- RC6: symptoms-only instruction.
- RC7/GX3: oracle Java rewrites well over 30 LOC.
- CR1: symbols op_inner mix_id n_hit.
- CR2: three roots, cap 0.5.
- GX6: no causal patch recipe in instruction.
- GX9: no scenario-value recital.

### Initial Draft Commitments

- tasks/moldwire-cask/instruction.md
- tasks/moldwire-cask/task.toml
- tasks/moldwire-cask/output_contract.toml
- tasks/moldwire-cask/construction_manifest.json
- tasks/moldwire-cask/rubric.txt
- tasks/moldwire-cask/tests/test.sh
- tasks/moldwire-cask/tests/test_outputs.py
- tasks/moldwire-cask/solution/solve.sh
- tasks/moldwire-cask/preship/preship.json
- tasks/moldwire-cask/preship/source_only.sh
- tasks/moldwire-cask/preship/decoy_fix.sh
- tasks/moldwire-cask/preship/shortcut_fix.sh
- tasks/moldwire-cask/environment/Dockerfile
- tasks/moldwire-cask/environment/.dockerignore
- tasks/moldwire-cask/environment/riv.sh
- tasks/moldwire-cask/environment/Makefile
- tasks/moldwire-cask/environment/slagbin/SlotEmit.java
- tasks/moldwire-cask/environment/slagbin/SheetScan.java
- tasks/moldwire-cask/environment/piturn/Dig.java
- tasks/moldwire-cask/environment/piturn/Store.java
- tasks/moldwire-cask/environment/dockcli/Gate.java
- tasks/moldwire-cask/environment/dockcli/Bake.java
- tasks/moldwire-cask/environment/dockcli/main.c
- tasks/moldwire-cask/environment/ribwire/run.c
- tasks/moldwire-cask/environment/ribwire/skip.c
- tasks/moldwire-cask/environment/sheetpit/pond.sheet
- tasks/moldwire-cask/environment/sheetpit/lake.sheet
- tasks/moldwire-cask/environment/dockotes/sheet.rules
- tasks/moldwire-cask/environment/dockotes/tree.map
- tasks/moldwire-cask/environment/dockotes/cold.note
- tasks/moldwire-cask/environment/duskpit/dusk.bin
- tasks/moldwire-cask/environment/rivdrop/

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

```
- path: slagbin/SlotEmit.java
  symbol: op_inner
  kind: function
  signature: String op_inner(String sheet)
  purpose: Writes a C skim unit for one sheet.
- path: piturn/Dig.java
  symbol: mix_id
  kind: function
  signature: String mix_id(byte[] sheet)
  purpose: Builds the urn lookup token for a sheet.
- path: dockcli/Gate.java
  symbol: n_hit
  kind: function
  signature: int n_hit(byte[] stored)
  purpose: Returns bake status when an urn row is reused.
```

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/slagbin/SlotEmit.java
    controls_tests: [test_mwc02_temp_slot, test_mwc03_holdout_leaf, test_mwc08_blank_temp, test_mwc10_pair_fields]
  - id: B
    path: environment/piturn/Dig.java
    controls_tests: [test_mwc04_served_fail, test_mwc06_added_leaf, test_mwc09_second_pass, test_mwc12_incs_shift]
  - id: C
    path: environment/dockcli/Gate.java
    controls_tests: [test_mwc01_elf_stock, test_mwc05_corrupt_incs, test_mwc07_json_keys, test_mwc11_fault_leaf]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

#### decoy_manifest

```
- path: environment/dockotes/cold.note
  kind: helper
  rhymes_with: mix_id
  non_fix_purpose: Suggests deleting the urn store when bake logs served.
```

#### code_forbidden_tokens

```
code_forbidden_tokens: [moldwire, sheetpit, incpit, duskpit, jsonpit, skim.json, dusk.bin, dockotes, tree.map, sheet.rules]
```
