### Decision
GO — Attempt 1. Debugging repair: Java incremental contract gate whose nudge stays green while flood reports an FQCN caller. Three loci: cite emit, schedule emit, blot code emit.

### Metadata
- version: 2
- Task name: seamwick-assay
- Title: Incremental gate skips caller
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["java", "bash"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["java", "incremental-gate", "type-cite", "blot-card"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/seamwick` is the desk. `nudge` writes `/app/blot/last.json`. `flood` walks `/app/corpus`. `sheet` reprints the blot.
- After a published type in `/app/corpus` is tightened, `nudge` must share findings with `flood` and return nonzero when findings exist.
- `last.json` keys: assayed, findings, code. findings objects: unit, kind, note. kind is `arity`. note is the call name. code is a decimal integer as text.
- assayed lists opened paths; it must include the FQCN caller flood would flag and must not include a path that does not name the tightened type.
- Source fixes under `/app` for units named in `/app/opsleaf/MAP.txt`. Hand-filled last.json is not enough. Verifier drives verbs in `/app/opsleaf/VERBS.txt`.

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
- path: environment/purlbox/PurlBox.java
  role: cite emit
- path: environment/knitwell/ops/KnitBox.java
  role: schedule emit
- path: environment/tintlag/core/TintBox.java
  role: blot code emit

### fix_frontier
- count: 3
- distribution: purlbox, knitwell, tintlag
- naming_policy: opaque purl knit tint
- forbidden_stems: nudge, flood, assayed, blot
- helpers_policy: Dump and Scan off frontier
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON keys, finding units, exit codes
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: wipe blot then flood once

### category_profile
- challenge_family: false_green_rehearsal_window
- bug_family: false_green_rehearsal_window
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: commands, paths, schemas, symptoms
- forbidden_instruction_leaks: import-only cites, reverse type index, FLOOR green
- category_specific_hardness_bar: nudge green while flood flags FQCN caller
- category_specific_verifier_risks: test-side javac, hand blot, wipe-then-flood
- coverage_role: debugging C2 incremental gate

### difficulty_mechanism_plan
- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: nudge exits 0 with empty findings
  why_model_misses_it: analyser works on flood
  fairness_guardrail: instruction names flood vs nudge disagreement
- mechanism: deceptive_but_valid_local_evidence
  placement: wipevat/Dump.java and hopnotes/FLOOR.txt
  why_model_misses_it: wipe then flood looks red once
  fairness_guardrail: holdout Kin change plus LocalAid not assayed
- mechanism: cross_file_cross_format_invariants
  placement: cite vs schedule vs blot code
  why_model_misses_it: hand last.json
  fairness_guardrail: verifier reruns nudge
- mechanism: stateful_multi_step_dependencies
  placement: assemble.bash after emit sources
  why_model_misses_it: skip javac
  fairness_guardrail: generated Cite/Sched/Seal overwritten on assemble

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: flood vs nudge on tightened Bond
- shortcut_audit: wipe blot, hand last.json, skip assemble
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
- sidecar_or_protocol_notes: corpus and warm blot bundled
- long_context_token_floor: 0

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs are purlbox/knitwell/tintlag
- gx9_contract_risk: low — observations on last.json
- cr1_symbol_frontier_risk: low — purl knit tint
- hidden_contract_risk: low — verbs and keys in instruction plus opsleaf

### actionability_plan
- verifier_command_visible: seamwick nudge flood sheet
- source_fix_intent_visible: MAP.txt units under /app
- generated_output_rule_visible: last.json
- exact_formula_home: kind arity
- schema_home: instruction.md and SHEET.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: No promoted reference matches a Java incremental contract gate whose nudge stays green while flood reports an FQCN caller after a published type tightening.

### realism_source
- source_type: real_system
- evidence_basis: incremental static analysis caches keyed by file that miss type-use edges
- upstream_or_synthetic_rationale: javac/error-prone incremental graphs historically miss non-import type uses
- minimization_preserves: green incremental vs red full walk
- synthetic_exception_review: not required

### Failure topology
nudge exits 0 after a published type is tightened. flood of the same tree reports a caller that uses a qualified name. The mill still writes a well-formed blot. A later tightening with a warm blot repeats the miss if the graph was only rebuilt by wiping.

### Environment shape
Emit roots under purlbox, knitwell, and tintlag. CLI under seamcmd. Corpus under corpus. Desk notes under opsleaf. Warm blot seeded in the image. Decoys wipevat and impgraph.

### Required artifacts
instruction, tests, Dockerfile with verifier wheels, solve.sh, task.toml allow_internet false, Java mill, 20+ environment files.

### Test plan
- test_ax01_held_hit: FQCN caller in findings
- test_ax02_clerk_hit: FQCN caller in assayed
- test_ax03_kin_hold: same-package caller after Kin change
- test_ax04_slot_obj: keys present
- test_ax05_dirty_rc: nonzero
- test_ax06_watch_seen: clean citer assayed
- test_ax07_hi_argc: kind arity note bind
- test_ax08_seed_keep: restore still finds caller
- test_ax09_walk_set: nudge findings match flood
- test_ax10_zz_smear: corrupt then rewrite
- test_ax11_obj_shape: finding keys
- test_ax12_floor_skip: LocalAid absent, still dirty

### Drafting guardrails
Do not name import-only graphs, reverse indexes, or FLOOR as the fix. Symptoms and blot schema only.

### Triviality Ledger
- Wipe blot then flood once: LocalAid appears on Bond-only nudge and Kin holdout still needs a live graph.
- Hand last.json: smear recovery reruns nudge.
- Skip assemble: generated Cite/Sched/Seal stay import-only.

### Per-gate Pitfall Inventory
- RC1: oracle emits new cite/schedule/code logic, not a flag delete
- RC2: fix paths are purlbox/knitwell/tintlag not assayed-fix
- RC3: tests check findings units and exit codes
- RC4: expected Clerk path is in tests not env goldens
- RC5: no golden last.json in environment
- RC6: symptoms-only instruction
- RC7: solve.sh well above 30 LOC
- GX9: last.json observations not boolean keys
- CR1: purl knit tint
- CR8: Boot dispatches Nudge/Flood/Sheet without naming emit symbols

### Initial Draft Commitments
- environment/purlbox/PurlBox.java
- environment/knitwell/ops/KnitBox.java
- environment/tintlag/core/TintBox.java
- environment/seamcmd/Bag.java
- environment/seamcmd/Loom.java
- environment/seamcmd/Drive.java
- environment/seamcmd/Nudge.java
- environment/seamcmd/Flood.java
- environment/seamcmd/Mark.java
- environment/seamcmd/Sheet.java
- environment/seamcmd/Boot.java
- environment/corpus/api/Bond.u
- environment/corpus/api/Kin.u
- environment/corpus/api/LocalAid.u
- environment/corpus/desk/Clerk.u
- environment/corpus/desk/Watch.u
- environment/corpus/wire/Port.u
- environment/opsleaf/MAP.txt
- environment/opsleaf/SHEET.txt
- environment/opsleaf/VERBS.txt
- environment/opsleaf/INK.txt
- environment/wipevat/Dump.java
- environment/impgraph/Scan.java
- environment/gasketurn/quiet.lst
- environment/hopnotes/FLOOR.txt
- environment/oldsnap/Bond.u
- environment/oldsnap/Kin.u
- environment/assemble.bash
- environment/Dockerfile
- environment/.dockerignore
- environment/nethush/wheels
- environment/nethush/debs
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

- path: environment/purlbox/PurlBox.java
  symbol: purl
  kind: function
  signature: purl(PrintWriter a) throws Exception
  purpose: writes Cite.java
- path: environment/knitwell/ops/KnitBox.java
  symbol: knit
  kind: function
  signature: knit(PrintWriter a) throws Exception
  purpose: writes Sched.java
- path: environment/tintlag/core/TintBox.java
  symbol: tint
  kind: function
  signature: tint(PrintWriter a) throws Exception
  purpose: writes Seal.java

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/purlbox/PurlBox.java
    controls_tests: [test_ax01_held_hit, test_ax03_kin_hold, test_ax07_hi_argc, test_ax08_seed_keep]
  - id: B
    path: environment/knitwell/ops/KnitBox.java
    controls_tests: [test_ax02_clerk_hit, test_ax06_watch_seen, test_ax09_walk_set, test_ax11_obj_shape]
  - id: C
    path: environment/tintlag/core/TintBox.java
    controls_tests: [test_ax04_slot_obj, test_ax05_dirty_rc, test_ax10_zz_smear, test_ax12_floor_skip]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

#### decoy_manifest

- path: environment/wipevat/Dump.java
  kind: helper
  rhymes_with: purl
  non_fix_purpose: deletes /app/blot
- path: environment/impgraph/Scan.java
  kind: helper
  rhymes_with: knit
  non_fix_purpose: collects import lines

#### code_forbidden_tokens

```
code_forbidden_tokens: [seamwick, nudge, flood, sheet, blot, last.json, corpus, assayed, findings, unit, kind, note, arity, opsleaf, MAP.txt, VERBS.txt, SHEET.txt, published, argument, nonzero, tightened, skipped]
```
