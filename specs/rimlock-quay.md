### Decision
GO — Attempt 1. Debugging repair of a C wait-graph mill: pointer-hashed ready pick, hex emit instead of intern tags, and owner-bucket runbook fold. Wait-depth wrap is a decoy. Held-out two-source dump, two-process identity, dusk remapped hex, and a missing closer fault keep the trap from scoring.

### Metadata
- version: 2
- Task name: rimlock-quay
- Title: Unblock plan drift
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "wait-graph", "elf", "kahn"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/rimlock` is a compiled ELF mill.
- `unjam DUMP OUT` writes one lock identity per line.
- `scroll DUMP OUT` writes `tid tag` lines in plan order.
- Identity is column two of `/app/inkurn/book.tsv`, not dump hex.
- Broken mill: shift `unjam` repeats dump hex; dusk hex tokens differ so alt.plan != shift plan; scroll is not `tid tag` in intern sequence.
- After repair: two process unjam of `/app/vatdock/shift.dmp` write intern-identity `/app/planbay/live.plan`.
- `/app/vatdock/dusk.dmp` is the same wait graph under other hex; `unjam` to `/app/planbay/alt.plan` must match live.plan.
- Two process scrolls of shift write byte-identical `/app/scrollbay/desk.chk` as `tid tag`.
- Simultaneously releasable monitors appear in ascending identity.
- Missing thread closer: `unjam` non-zero, `/app/planbay/mill.ok` absent. Success writes mill.ok.
- Grammar in `/app/desknote/forms.txt`. Desk map in `/app/desknote/ROUTE.txt`.
- Static plan writes are not enough. Verifier reruns unjam and scroll. Mill identity: agent `/app/bin/rimlock` matches hull linked to `/tmp/rimlock.ref` from on-disk C.

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

- path: environment/hullcue/main.c
  role: CLI entry
- path: environment/knothub/pick.c
  role: ready pick
- path: environment/emiturn/bind.c
  role: identity emit
- path: environment/inkfold/fold.c
  role: runbook fold

### fix_frontier

- count: 3
- distribution: knothub, emiturn, inkfold as distinct top-level roots
- naming_policy: opaque op_/cfg_/n_ symbols
- forbidden_stems: rimlock, assay, scroll, roster, runbook, identity, closer
- helpers_policy: wait-depth rank wrap is decoy
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: [plan bytes, scroll lines, exit codes]
- forbidden_assertion_styles: [boolean answer keys]

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: enabling wait-depth wrap or sorting hex without intern tags

### category_profile

- challenge_family: concurrency_ordering
- bug_family: ready_set_and_intern
- profile_name: concurrency_ordering
- allowed_instruction_disclosures: commands, paths, ELF, closer fault, source-fix intent, identity column, tid tag lines
- forbidden_instruction_leaks: pointer hash, wait-depth wrap as the bug, hash buckets, Kahn name
- category_specific_hardness_bar: two schedulers of emit (pick vs fold) plus intern identity must coordinate
- category_specific_verifier_risks: golden plans in env, scenery roster-only tests that pass on NOP
- coverage_role: wait-graph mill with prove-twice plans, not compact intern profiles

### difficulty_mechanism_plan

- mechanisms: [false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, environment_specific_cli_semantics]
- adversarial_layers_count: 4
- fairness_guardrails: public paths and identity column stated; mechanism withheld
- mechanism: false_green_intermediate_states
  placement: roster of one run looks correct
  why_model_misses_it: stops after cycle members match
  fairness_guardrail: instruction reports two-process plan drift
- mechanism: deceptive_but_valid_local_evidence
  placement: hullcue/rank.c wait-depth wrap
  why_model_misses_it: notes say ranking already wraps emit
  fairness_guardrail: handbook describes depth wrap as worker join only
- mechanism: cross_file_cross_format_invariants
  placement: pick.c vs bind.c vs fold.c
  why_model_misses_it: fixing one locus leaves dusk or scroll red
  fairness_guardrail: dusk remapping is a stated public case
- mechanism: environment_specific_cli_semantics
  placement: assay.ok and missing closer
  why_model_misses_it: success marker left in place on fault
  fairness_guardrail: instruction states both polarities

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert can trace pick, intern emit, and fold in a few hours
- shortcut_audit: depth-rank only, hand-written plan, script mill, source-only skip stoke
- ablation_plan: revert each of pick/bind/fold and expect a declared test subset to fail
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
- cr1_symbol_frontier_risk: low — op_pick/n_bind/cfg_fold off CLI nouns
- hidden_contract_risk: low — forms.txt states dump fields without pick recipe

### actionability_plan

- verifier_command_visible: rimlock unjam, scroll
- source_fix_intent_visible: Repair C sources under /app named from ROUTE.txt
- generated_output_rule_visible: live.plan, alt.plan, desk.chk, mill.ok; static writes insufficient
- exact_formula_home: identity column in instruction; dump layout in forms.txt
- schema_home: instruction plus forms.txt

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- reference_task_id:
- justification_if_none: docs/reference_tasks/index.json has no promoted references; wait-graph mill with intern tags is not a clone of a listed candidate

### realism_source

- source_type: real_system
- evidence_basis: JVM wait-for-graph / thread-dump deadlock plans whose topo ties follow interned monitor ids, not ASLR hex
- upstream_or_synthetic_rationale: minimized to three C loci plus a wait-depth decoy
- minimization_preserves: prove-twice plan identity vs roster-correctness, remapped-hex identity
- synthetic_exception_review: not required

### Failure topology
Operators see matching cycle members and owners, while two process plan files and two hex encodings of the same wait graph still differ because ready pick follows pointer-hashed buckets, emit writes dump hex, and the runbook folds by owner-bucket order. A wait-depth wrap after pick is a no-op on equal depths.

### Environment shape
CLI hull, dump scan, graph build, ready pick, intern bind, runbook fold, field notes, two dumps, stoke rebuild, depth-rank decoy.

### Required artifacts
Standard task tree, gcc image, pytest under /opt/verifier, native ELF mill, preship R5/R6/R7, rubric.txt.

### Test plan
- ELF plus two-process plan identity
- two-process scroll identity
- dusk vs shift plan match
- scroll rows follow plan
- held-out two-source order
- missing closer exit
- corrupt then assay
- dusk scroll match
- first ready pair ascending
- one child assay
- topo precedence
- dusk two-process scroll

### Drafting guardrails
Do not name pointer hash, Kahn, wait-depth as the bug, or ready-set in instruction, comments, or test names. Do not put golden plans under environment/.

### Triviality Ledger

- Wait-depth wrap in rank.c already runs and leaves pointer pick plus hex emit plus owner fold untouched; two-process plans stay noisy.
- Sorting dump hex without intern tags makes dusk disagree with shift.
- Hand-written live.plan fails corrupt-then-assay recovery.

### Per-gate Pitfall Inventory

- RC2: fix files pick.c/bind.c/fold.c; no golden_* names.
- GX9: grade bytes, line order, exit codes; no boolean keys.
- CR1: oracle symbols op_pick, n_bind, cfg_fold.
- R5: tests never stoke/make; they invoke /app/bin/rimlock.
- R3: every graded test fails on the shipped tree (hash pick, hex emit, owner fold).

### Initial Draft Commitments

- environment/Dockerfile
- environment/.dockerignore
- environment/stoke.sh
- environment/hullcue/main.c
- environment/hullcue/hull.mk
- environment/hullcue/go.c
- environment/hullcue/rank.c
- environment/hullcue/rank.h
- environment/knothub/pick.c
- environment/knothub/pick.h
- environment/knothub/graph.c
- environment/knothub/graph.h
- environment/knothub/store.h
- environment/knothub/cycle.c
- environment/readcue/scan.c
- environment/readcue/scan.h
- environment/emiturn/bind.c
- environment/inkurn/bind.h
- environment/inkurn/book.c
- environment/inkurn/book.h
- environment/inkurn/book.tsv
- environment/inkfold/fold.c
- environment/inkfold/fold.h
- environment/desknote/ROUTE.txt
- environment/desknote/forms.txt
- environment/desknote/DEPTH.txt
- environment/vatdock/shift.dmp
- environment/vatdock/dusk.dmp
- environment/keelbox/wheels/
- environment/keelbox/debs/
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
- path: knothub/pick.c
  symbol: op_pick
  kind: function
  signature: int op_pick(void)
  purpose: Fills the emit index list from remaining nodes.
- path: emiturn/bind.c
  symbol: n_bind
  kind: function
  signature: int n_bind(const char *a)
  purpose: Writes the destination file from the emit index list.
- path: inkfold/fold.c
  symbol: cfg_fold
  kind: function
  signature: int cfg_fold(const char *a)
  purpose: Writes the runbook file from the emit index list.
```

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/knothub/pick.c
    controls_tests: [test_rkq01_hdr, test_rkq05_holdout, test_rkq09_hits, test_rkq11_stay]
  - id: B
    path: environment/emiturn/bind.c
    controls_tests: [test_rkq03_peer, test_rkq06_tail, test_rkq07_mint, test_rkq10_child]
  - id: C
    path: environment/inkfold/fold.c
    controls_tests: [test_rkq02_twin, test_rkq04_rows, test_rkq08_hush, test_rkq12_peer]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

#### decoy_manifest

```
- path: environment/hullcue/rank.c
  kind: helper
  rhymes_with: op_pick
  non_fix_purpose: Optional wait-depth wrap after pick; all depths equal in the fixture.
```

#### code_forbidden_tokens

```
code_forbidden_tokens: [rimlock, assay, scroll, roster, runbook, identity, closer, vatdock, planbay, scrollbay, inkurn, desknote, cycle, monitors, owners]
```
