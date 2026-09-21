### Decision
GO — Attempt 1. Debugging repair of a C impact mill: hash-bucket rank mix, last-file coverage overwrite, and count-cap budget. Repeat-process lock, two-file morn, held-out cards, and a voided origin keep `--stable-order` from scoring.

### Metadata
- version: 2
- Task name: skiffloom-crib
- Title: Impact slate drift
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "coverage", "rank", "elf"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/skiffloom` is a compiled ELF mill.
- `cull CHANGE DEST` writes `DEST/slate.json` and `DEST/slate.bin`.
- Ranking and record layout live in `/app/opsfold/forms.txt`.
- Repeat-process culls of `/app/deltabay/eve.chg` into `/app/slatewell` must match on both slate files.
- `/app/deltabay/morn.chg` must list every sheet-backed name that touches the changed lines.
- Cards outside `/app/deltabay` follow the same rules.
- JSON: `{"pool":["..."],"names":["..."],"spent_ms":0}`.
- `ORIGIN voided` exits non-zero and omits `/app/slatewell/cull.ok`.
- Success writes `/app/slatewell/cull.ok`.
- Hand-copied slates are not enough. Verifier reruns `cull`.
- Shipped mill matches the mill path in `/app/opsfold/HULL.txt` on eve.

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

- path: environment/heapwell/rank.c
  role: rank order
- path: environment/heapwell/rank.h
  role: rank header
- path: environment/spanurn/fold.c
  role: coverage weights
- path: environment/spanurn/fold.h
  role: fold header
- path: environment/tickpit/trim.c
  role: duration prefix
- path: environment/tickpit/trim.h
  role: trim header

### fix_frontier

- count: 3
- distribution: heapwell, spanurn, tickpit as distinct top-level roots
- naming_policy: opaque op_/cfg_/n_ symbols
- forbidden_stems: skiffloom, cull, slate, pool, names, spent, eve, morn, voided, meshcards, ticks
- helpers_policy: --stable-order helper is decoy
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: [slate json, slate bin, exit codes]
- forbidden_assertion_styles: [boolean answer keys]

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: enabling --stable-order or sorting the final list by coverage count only

### category_profile

- challenge_family: concurrency_ordering
- bug_family: unpinned_equal_ranks
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, JSON keys, ELF, voided origin, source-fix intent, forms ranking
- forbidden_instruction_leaks: stack-mix hash buckets, last-file overwrite recipe, count-cap trim, --stable-order as the fix
- category_specific_hardness_bar: parse change cards, normalize coverage union, serialize slate, duration prefix must interact
- category_specific_verifier_risks: golden slate in env, scenery ELF-only tests that pass on NOP
- coverage_role: impact-run mill with prove-twice, not hitch token mill

### difficulty_mechanism_plan

- mechanisms: [false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, environment_specific_cli_semantics]
- adversarial_layers_count: 4
- fairness_guardrails: public paths and forms ranking stated; mechanism withheld
- mechanism: false_green_intermediate_states
  placement: coverage counts on one cull look correct
  why_model_misses_it: stops after one process
  fairness_guardrail: instruction reports rotating names under budget
- mechanism: deceptive_but_valid_local_evidence
  placement: latch.c --stable-order
  why_model_misses_it: flag re-sorts by coverage count
  fairness_guardrail: handbook describes the flag as count reorder, not a pass recipe
- mechanism: cross_file_cross_format_invariants
  placement: rank.c vs fold.c vs trim.c
  why_model_misses_it: one file patch
  fairness_guardrail: morn two-file case is a stated public case
- mechanism: environment_specific_cli_semantics
  placement: cull.ok and ORIGIN voided
  why_model_misses_it: cull still 0
  fairness_guardrail: instruction states both polarities

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert traces rank mix, coverage union, and duration prefix in a few hours
- shortcut_audit: --stable-order only, hand-written slate, script mill, source-only skip kindle
- ablation_plan: revert each of rank/fold/trim and expect a declared test subset to fail
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Opus 5 / GPT-5.6

### verifier_scoring_plan

- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: all pytest tests pass

### subtype_milestone_plan

- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: none
- long_context_token_floor: 0

### satisfiability_risk

- rc2_planned_name_risk: low — generic mill names, no broken_*
- gx9_contract_risk: low — no scenario-key-value recital
- cr1_symbol_frontier_risk: low — op_lift/cfg_span/n_trim off CLI nouns
- hidden_contract_risk: low — forms.txt states ranking without heap recipe

### actionability_plan

- verifier_command_visible: skiffloom cull
- source_fix_intent_visible: C modules from ROUTE.txt need source updates under /app
- generated_output_rule_visible: slate.json, slate.bin, cull.ok; static copies insufficient
- exact_formula_home: forms.txt
- schema_home: instruction plus forms.txt

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- reference_task_id:
- justification_if_none: docs/reference_tasks/index.json has no promoted references; impact-run slate mill is not a clone of a listed candidate

### realism_source

- source_type: real_system
- evidence_basis: test-impact analysers that rank by coverage weight then clip a duration budget; equal weights follow hash/ASLR insertion; overlapping files must union hit cells
- upstream_or_synthetic_rationale: minimized to three C loci plus a stable-order decoy
- minimization_preserves: counts correct per run but unpinned among equals; last file overwrites union; count cap ignores ticks
- synthetic_exception_review: not required

### Failure topology
Operators see matching coverage counts and a rotating budgeted prefix across processes, plus a two-file change whose pool drops sheet-backed names. A count cap and a stable-order flag still look locally green.

### Environment shape
CLI hull, rank well, span fold, tick trim, emit kit, ops notes, change cards, mesh sheets, duration ticks, kindle rebuild, stable-order decoy.

### Required artifacts
Standard task tree, gcc image, pytest under /opt/verifier, native ELF mill, preship R5/R6/R7, rubric.txt.

### Test plan
- ELF plus two-process eve match
- hull mill identity
- eve pool set and names prefix
- spent_ms
- morn union ranking
- morn two-process match
- held-out change card
- voided origin exit
- cull.ok absent on fault
- corrupt then cull
- bin matches json
- success cull.ok

### Drafting guardrails
Do not name stack-mix buckets, last-file overwrite, or count-cap in instruction, comments, or test names. Do not put golden slates under environment/.

### Triviality Ledger

- `--stable-order` re-sorts by coverage count and still leaves equal-count rotation; twin-process tests fail.
- Hand-written slate.json fails recovery that reruns cull after corruption.
- Source-only edits without kindle leave the shipped ELF on the old rank mix.

### Per-gate Pitfall Inventory

- RC1: oracle adds total-order compare, union weights, and duration prefix rather than deleting a flag.
- RC2: no broken_/golden_ names on solver-visible paths.
- RC3: tests check pool membership, names prefix, spent_ms, and two-process bytes, not existence alone.
- RC4: expected values live in tests, not env goldens.
- RC5: no answer-shaped slates in environment/.
- RC6: symptoms-only; ranking grammar in forms.txt.
- RC7: three-file semantic oracle.
- GX9: no scenario-key-value recital in instruction.
- CR2: three roots, concentration cap 0.5.

### Initial Draft Commitments

- instruction.md
- task.toml
- rubric.txt
- output_contract.toml
- construction_manifest.json
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- solution/rank.c
- solution/fold.c
- solution/trim.c
- environment/Dockerfile
- environment/.dockerignore
- environment/kindle.sh
- environment/cribcli/driver.mk
- environment/cribcli/hull.c
- environment/cribcli/latch.c
- environment/cribcli/latch.h
- environment/cribcli/load.c
- environment/cribcli/load.h
- environment/cribcli/flow.c
- environment/cribcli/flow.h
- environment/cribcli/wire.h
- environment/heapwell/rank.c
- environment/heapwell/rank.h
- environment/spanurn/fold.c
- environment/spanurn/fold.h
- environment/tickpit/trim.c
- environment/tickpit/trim.h
- environment/emitkit/pour.c
- environment/emitkit/pour.h
- environment/opsfold/ROUTE.txt
- environment/opsfold/forms.txt
- environment/opsfold/HULL.txt
- environment/deltabay/eve.chg
- environment/deltabay/morn.chg
- environment/deltabay/void.chg
- environment/durcards/ticks.txt
- environment/meshcards/q_ab.mesh
- environment/meshcards/q_cd.mesh
- environment/meshcards/q_ef.mesh
- environment/meshcards/q_gh.mesh
- environment/meshcards/q_ij.mesh
- environment/meshcards/q_kl.mesh
- environment/meshcards/q_mn.mesh
- environment/meshcards/q_op.mesh
- environment/meshcards/q_qr.mesh
- environment/meshcards/q_st.mesh
- environment/cribbox/wheels (copied verifier wheels)
- environment/cribbox/debs (copied tmux debs)
- preship/preship.json
- preship/source_only.sh
- preship/decoy_fix.sh
- preship/shortcut_fix.sh

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

- path: environment/heapwell/rank.c
  symbol: op_lift
  kind: function
  signature: void op_lift(void)
  purpose: Orders loaded rows for emit.
- path: environment/spanurn/fold.c
  symbol: cfg_span
  kind: function
  signature: int cfg_span(void)
  purpose: Fills coverage counts on loaded rows.
- path: environment/tickpit/trim.c
  symbol: n_trim
  kind: function
  signature: int n_trim(void)
  purpose: Selects a prefix of the ordered rows.

#### flipping_point_contract

locations:
  - id: A
    path: environment/heapwell/rank.c
    controls_tests: [test_sk01_hdr, test_sk02_peer, test_sk10_note, test_sk11_ref]
  - id: B
    path: environment/spanurn/fold.c
    controls_tests: [test_sk03_bag, test_sk05_dusk, test_sk09_hold, test_sk12_lab]
  - id: C
    path: environment/tickpit/trim.c
    controls_tests: [test_sk04_cut, test_sk06_tail, test_sk07_seal, test_sk08_rest]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/cribcli/latch.c
  kind: helper
  rhymes_with: op_lift
  non_fix_purpose: Parses --stable-order and sets a flag that re-sorts by coverage count only.

#### code_forbidden_tokens

code_forbidden_tokens: [skiffloom, cull, slate, pool, names, spent, eve, morn, voided, meshcards, ticks]
