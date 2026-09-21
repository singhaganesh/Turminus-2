### Decision
GO — Attempt 1. Debugging repair of a Go hitch mill: UF parent used as the printed hitch, pair files not joined, and map-range emit. Size-rank helper is a decoy. Two-process identity, morn permutation, held-out yarn, and scrapped origin keep the trap from scoring.

### Metadata
- version: 2
- Task name: twinefuse-berth
- Title: Hitch token drift
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["go"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["go", "hitch", "elf", "yarn"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/twinefuse` is a compiled ELF mill.
- `sew YARN OUTDIR` writes `rows.ndjson` and `hitch.idx` in OUTDIR.
- Column meanings and hitch rule live in `/app/millnote/LAY.txt`.
- Pair files under `/app/aliascue` join tokens that never share a dump line.
- Two OS invocations sewing `/app/cordbay/eve.yarn` into `/app/dockurn` must agree byte-for-byte on both files.
- `/app/cordbay/morn.yarn` is the same ids/tokens in another order; morn sew must keep the same hitch per id.
- Yarns not already in `/app/cordbay` keep that hitch-to-id rule.
- origin `scrapped` → sew non-zero, `/app/dockurn/berth.ok` absent. Success writes berth.ok.
- Source work under `/app` from `/app/millnote/ROUTE.txt`. Hand paste of dockurn is not enough. Verifier reruns `/app/bin/twinefuse sew`.

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

- path: environment/netsrc/tie.go
  role: token net hitch
- path: environment/cardpit/pair.go
  role: pair file join
- path: environment/walkbind/stamp.go
  role: dockurn write

### fix_frontier

- count: 3
- distribution: netsrc, cardpit, walkbind as distinct top-level roots
- naming_policy: opaque OpMark / NPair / CfgStamp
- forbidden_stems: twinefuse, sew, hitch, eve, morn
- helpers_policy: ribdrop Rank size table is decoy
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: [ndjson bytes, idx lines, exit codes]
- forbidden_assertion_styles: [boolean answer keys]

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: copying deskfold hitch.idx or ranking by component size

### category_profile

- challenge_family: distributed_reconciliation
- bug_family: unstable_component_label
- profile_name: distributed_reconciliation
- allowed_instruction_disclosures: commands, paths, ELF, scrapped origin, two-invocation identity, morn permutation, source-fix intent
- forbidden_instruction_leaks: union-find parent, map iteration, union-by-size as the fix, pair skip
- category_specific_hardness_bar: membership, hitch token, and emit order must coordinate across pair files
- category_specific_verifier_risks: golden idx in env, scenery ELF-only tests, test-side rebuild
- coverage_role: prove-twice labelled streams with alias joins

### difficulty_mechanism_plan

- mechanisms: [false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies]
- adversarial_layers_count: 4
- fairness_guardrails: public paths and LAY schema stated; UF recipe withheld
- mechanism: false_green_intermediate_states
  placement: shared-token groups already agree
  why_model_misses_it: stops after membership looks right
  fairness_guardrail: instruction reports hitch drift across invocations
- mechanism: deceptive_but_valid_local_evidence
  placement: ribdrop/rank.go size table plus union-by-size comment
  why_model_misses_it: notes say size already makes roots stable
  fairness_guardrail: equal-size aliased groups still drift
- mechanism: cross_file_cross_format_invariants
  placement: netsrc/tie.go vs cardpit/pair.go vs walkbind/stamp.go
  why_model_misses_it: fixing hitch alone leaves shuffled rows or split alias groups
  fairness_guardrail: morn permutation and pair files are public
- mechanism: stateful_multi_step_dependencies
  placement: source then hull.sh then sew
  why_model_misses_it: skip mill rebuild or paste dockurn
  fairness_guardrail: instruction says paste is not enough

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert traces hitch, pair join, and emit order in a few hours
- shortcut_audit: size-rank only, deskfold copy, script mill, source-only skip hull
- ablation_plan: revert each of tie/pair/stamp and expect a declared test subset to fail
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
- cr1_symbol_frontier_risk: low — OpTie/NPair/CfgStamp off CLI nouns
- hidden_contract_risk: low — LAY.txt states columns without UF recipe

### actionability_plan

- verifier_command_visible: twinefuse sew
- source_fix_intent_visible: source work under /app named from ROUTE.txt
- generated_output_rule_visible: rows.ndjson, hitch.idx, berth.ok; paste insufficient
- exact_formula_home: hitch least-token rule in LAY.txt
- schema_home: instruction plus LAY.txt and forms.txt

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- reference_task_id:
- justification_if_none: docs/reference_tasks/index.json has no promoted references; hitch mill with prove-twice labelled streams is not a clone of a listed candidate

### realism_source

- source_type: real_system
- evidence_basis: sessionisation / correlation-id stitching that labels a component by union-find representative; Go map iteration makes the parent unstable across processes
- upstream_or_synthetic_rationale: minimized to three Go loci plus a size-rank decoy
- minimization_preserves: prove-twice hitch identity vs membership-correctness, alias join, emit order
- synthetic_exception_review: not required

### Failure topology
Operators see matching id groups while two process hitch files still differ because the printed token follows the union-find parent, pair cards never join, and emit walks a hash map. A size-rank helper after join is a no-op on equal-size groups.

### Environment shape
CLI, yarn scan, token net, pair join, dockurn stamp, field notes, two yarns, hull rebuild, size-rank decoy, deskfold snapshot.

### Required artifacts
Standard task tree, golang image, pytest under /opt/verifier, native ELF mill, preship R5/R6/R7, rubric.txt.

### Test plan
- ELF plus two-process rows identity
- two-process idx identity
- dump-order rows
- alias-joined hitch
- morn vs eve hitch per id
- held-out yarn
- scrapped origin exit
- corrupt then sew
- idx membership
- berth.ok polarity with hush
- hitch equals least token in group
- independent recompute digest

### Drafting guardrails
Do not name union-find, map iteration, union-by-size as the bug, or lex-min in instruction, comments, or test names. Least-token rule lives in LAY.txt. Do not put golden rows.ndjson under environment/.

### Triviality Ledger

- Size-rank in rank.go already runs and leaves UF parent hitch plus skipped pair join plus map emit untouched; two-process files stay noisy.
- Copying deskfold/night.hitch matches one eve idx snapshot but fails morn, held-out, and recovery.
- Hand-written dockurn fails corrupt-then-sew recovery.

### Per-gate Pitfall Inventory

- RC2: fix files tie.go/pair.go/stamp.go; no golden_* names.
- GX9: grade bytes, line order, exit codes; no boolean keys.
- CR1: oracle symbols OpMark, NPair, CfgStamp.
- R5: tests never hull/go build; they invoke /app/bin/twinefuse.
- R3: every graded test fails on the shipped tree (parent hitch, skipped pairs, map emit).

### Initial Draft Commitments

- environment/Dockerfile
- environment/.dockerignore
- environment/hull.sh
- environment/go.mod
- environment/berthcli/main.go
- environment/berthcli/sew.go
- environment/netsrc/tie.go
- environment/cardpit/pair.go
- environment/aliascue/desk.cue
- environment/walkbind/stamp.go
- environment/ribdrop/rank.go
- environment/readcue/scan.go
- environment/readcue/attach.go
- environment/millnote/LAY.txt
- environment/millnote/ROUTE.txt
- environment/millnote/CLI.txt
- environment/millnote/HULL.txt
- environment/millnote/forms.txt
- environment/cordbay/eve.yarn
- environment/cordbay/morn.yarn
- environment/deskfold/night.hitch
- environment/deskfold/NOTE.txt
- environment/cratebox/wheels/
- environment/cratebox/debs/
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
- path: netsrc/tie.go
  symbol: OpMark
  kind: function
  signature: func OpMark(n *Net, tok string) string
  purpose: Returns the printed hitch token for a member token.
- path: cardpit/pair.go
  symbol: NPair
  kind: function
  signature: func NPair(dir string, n *Net) error
  purpose: Loads pair files into the token net.
- path: walkbind/stamp.go
  symbol: CfgStamp
  kind: function
  signature: func CfgStamp(outDir string, rows []Row) error
  purpose: Writes dockurn row and idx files.
```

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/netsrc/tie.go
    controls_tests: [test_tf00_magic, test_tf01_twin, test_tf06_peer, test_tf07_held]
  - id: B
    path: environment/cardpit/pair.go
    controls_tests: [test_tf04_clump, test_tf05_span, test_tf08_hush, test_tf10_hits]
  - id: C
    path: environment/walkbind/stamp.go
    controls_tests: [test_tf02_book, test_tf03_seq, test_tf09_guard, test_tf11_redo]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

#### decoy_manifest

```
- path: environment/ribdrop/rank.go
  kind: helper
  rhymes_with: OpMark
  non_fix_purpose: Optional size table after join; equal-size groups in the fixture.
```

#### code_forbidden_tokens

```
code_forbidden_tokens: [twinefuse, sew, cordbay, eve, dockurn, rows, hitch, millnote, LAY, aliascue, ROUTE, morn, scrapped, berth, ELF, yarn, bookmark]
```
