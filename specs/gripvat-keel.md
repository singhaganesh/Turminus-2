### Decision
GO — Attempt 1. Debugging repair of a C heap-ledger mill: root order unpinned by address mix, generated neighbour comparator keyed by object id, and weak edges treated as retaining. Two-process lock, packing-variant lock, held-out class names, and a trailer fault keep `--pin-handles` from scoring.

### Metadata
- version: 2
- Task name: gripvat-keel
- Title: Retaining path drift
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "heap", "retain", "elf"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/keelgrip` is a compiled ELF mill.
- `mint HEAP LEDGER` loads a card under `/app/packurn` and writes a ledger.
- `align LEFT RIGHT` writes `/app/inkurn/align.txt` with exactly `lock` when ledgers match.
- Two process mints of `/app/packurn/day.hpk` must `lock`.
- `/app/packurn/dusk.hpk` is the same leak under other handles; `align` vs the day ledger must `lock`.
- PATH hop labels follow `/app/deskcue/forms.txt` (STRONG retaining chains).
- Success writes `/app/inkurn/mint.ok`. A card missing `END` makes `mint` exit non-zero and omits `mint.ok`.
- Grammar in `/app/deskcue/forms.txt`. Bay map in `/app/deskcue/BAY.txt`.
- Hand-written ledgers are not enough. Verifier reruns `mint` and `align`.

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

- path: environment/rootwell/scan.c
  role: root ordering
- path: environment/adjmill/emit.c
  role: neighbour comparator generator
- path: environment/softbay/skip.c
  role: edge-kind gate

### fix_frontier

- count: 3
- distribution: rootwell, adjmill, softbay as distinct top-level roots
- naming_policy: opaque op_/cfg_/n_ symbols
- forbidden_stems: keelgrip, mint, align, packurn, inkurn, lock, slip
- helpers_policy: pin-handles helper is decoy
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: [ledger text, align token, exit codes]
- forbidden_assertion_styles: [boolean answer keys]

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: enabling --pin-handles or sorting one table by object id

### category_profile

- challenge_family: concurrency_ordering
- bug_family: unpinned_equal_paths
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, lock/slip, ELF, trailer, source-fix intent, forms grammar
- forbidden_instruction_leaks: address-xor root order, handle comparator, weak-as-retain recipe, pin-handles as the fix
- category_specific_hardness_bar: parse, normalize retaining walk, serialize ledger, packing variant must interact
- category_specific_verifier_risks: golden ledger in env, scenery BYTES-only tests that pass on NOP
- coverage_role: retaining-path mill with prove-twice, not compact intern

### difficulty_mechanism_plan

- mechanisms: [false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, environment_specific_cli_semantics]
- adversarial_layers_count: 4
- fairness_guardrails: public paths and lock/slip contract stated; mechanism withheld
- mechanism: false_green_intermediate_states
  placement: SITE/BYTES of one mint look correct
  why_model_misses_it: stops after one ledger
  fairness_guardrail: instruction reports PATH hops that fail forms.txt even when align still lock
- mechanism: deceptive_but_valid_local_evidence
  placement: latch.c and BAY.txt --pin-handles
  why_model_misses_it: flag promises stable neighbour lists
  fairness_guardrail: handbook describes the flag as object-id reorder, not a pass recipe
- mechanism: cross_file_cross_format_invariants
  placement: scan.c vs emit.c vs skip.c
  why_model_misses_it: one file patch
  fairness_guardrail: dusk packing is a stated public case
- mechanism: environment_specific_cli_semantics
  placement: mint.ok and missing END trailer
  why_model_misses_it: mint still 0
  fairness_guardrail: instruction states both polarities

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert traces root order, generated comparator, and weak gate in a few hours
- shortcut_audit: pin-handles only, hand-written ledger, script mill, source-only skip stoke
- ablation_plan: revert each of scan/emit/skip and expect a declared test subset to fail
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
- cr1_symbol_frontier_risk: low — op_root/cfg_emit/n_soft off CLI nouns
- hidden_contract_risk: low — forms.txt states STRONG retaining without handle recipe

### actionability_plan

- verifier_command_visible: keelgrip mint, keelgrip align
- source_fix_intent_visible: C modules from BAY.txt need source updates under /app
- generated_output_rule_visible: live.txt, alt.txt, align.txt, mint.ok; static copies insufficient
- exact_formula_home: PATH grammar in forms.txt
- schema_home: instruction plus forms.txt

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- reference_task_id:
- justification_if_none: docs/reference_tasks/index.json has no promoted references; heap retaining-path mill is not a clone of a listed candidate

### realism_source

- source_type: real_system
- evidence_basis: heap dump retainers (shortest root path) whose tie-break follows loader handles and hash/ASLR root order; weak refs do not retain
- upstream_or_synthetic_rationale: minimized to three C loci plus a pin-handles decoy
- minimization_preserves: shortest-path correct per run but unpinned among equals; packing permutes handles
- synthetic_exception_review: not required

### Failure topology
Operators see matching SITE/BYTES and two-process lock on a PATH that still fails forms.txt hops: JNI-first file order plus WEAK hops plus object-id neighbour order. Packing dusk/holdout still disagrees once WEAK is dropped without a class/field comparator.

### Environment shape
CLI hull, root scan, adj mill generator, soft skip, path walk, align, deskcue, two heap cards, kiln rebuild, pin decoy.

### Required artifacts
Standard task tree, gcc image, pytest under /opt/verifier, native ELF mill, preship R5/R6/R7, rubric.txt.

### Test plan
- ELF plus two-process lock
- second two-process lock
- day vs dusk lock
- PATH omits WEAK field
- held-out handle swap with new class names
- missing trailer exit
- mint.ok absent on fault
- corrupt then mint
- second holdout
- align token
- hull matches shipped mill
- day/dusk PATH equality

### Drafting guardrails
Do not name address-xor, handle comparators, or weak-as-retain in instruction, comments, or test names. Do not put golden ledgers under environment/.

### Triviality Ledger

- `--pin-handles` sets a flag the walker ignores and leaves generated id order plus root mix plus weak hops untouched; packing-variant align stays slip.
- Sorting neighbours by object id without a class/field key still flips dusk vs day.
- Hand-written live.txt fails corrupt-then-mint recovery and held-out class names.

### Per-gate Pitfall Inventory

- RC2: fix files scan.c/emit.c/skip.c; no golden_* names.
- GX9: grade lock token, PATH text, exits; no boolean keys.
- CR1: oracle symbols op_root, cfg_emit, n_soft.
- R5: tests never stoke; they invoke /app/bin/keelgrip.
- R3: every graded test fails on the shipped tree (root mix, handle order, weak hops).

### Initial Draft Commitments

- environment/Dockerfile
- environment/.dockerignore
- environment/kindle.sh
- environment/millarm/driver.c
- environment/millarm/driver.mk
- environment/millarm/latch.c
- environment/millarm/latch.h
- environment/millarm/load.c
- environment/millarm/load.h
- environment/rootwell/scan.c
- environment/rootwell/scan.h
- environment/adjmill/emit.c
- environment/adjmill/emit.h
- environment/adjmill/emit_main.c
- environment/softbay/skip.c
- environment/softbay/skip.h
- environment/ridget/step.c
- environment/ridget/step.h
- environment/ridget/step.inc
- environment/twinline/note.c
- environment/twinline/note.h
- environment/deskcue/BAY.txt
- environment/deskcue/forms.txt
- environment/packurn/day.hpk
- environment/packurn/dusk.hpk
- environment/hullpkg/wheels/
- environment/hullpkg/debs/
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

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

```
- path: rootwell/scan.c
  symbol: op_root
  kind: function
  signature: int op_root(const char *path)
  purpose: Loads ROOT records and orders them for the walker.
- path: adjmill/emit.c
  symbol: cfg_emit
  kind: function
  signature: void cfg_emit(FILE *fp)
  purpose: Writes the neighbour comparator into step.inc.
- path: softbay/skip.c
  symbol: n_soft
  kind: function
  signature: int n_soft(int kind)
  purpose: Decides whether an edge kind is used in the walk.
```

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/rootwell/scan.c
    controls_tests: [test_gvk06_tail, test_gvk07_seal]
  - id: B
    path: environment/adjmill/emit.c
    controls_tests: [test_gvk03_peer, test_gvk05_hold, test_gvk09_swap, test_gvk12_lab]
  - id: C
    path: environment/softbay/skip.c
    controls_tests: [test_gvk01_twin, test_gvk02_again, test_gvk04_line, test_gvk08_rest, test_gvk10_note, test_gvk11_ref]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

#### decoy_manifest

```
- path: environment/millarm/latch.c
  kind: helper
  rhymes_with: cfg_emit
  non_fix_purpose: Parses --pin-handles and sets a flag the walker ignores.
```

#### code_forbidden_tokens

```
code_forbidden_tokens: [keelgrip, mint, align, packurn, inkurn, lock, slip]
```
