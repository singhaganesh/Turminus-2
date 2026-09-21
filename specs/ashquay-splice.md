### Decision
GO — Attempt 1. Debugging repair of a C split-debug mill: well bag, richer-object pick, and provenance credit sit in three roots. retry_first decoy is punished.

### Metadata
- version: 2
- Task name: ashquay-splice
- Title: Splice hosts drift
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "debuginfo", "splice", "elf"]
- Milestones: 0

## Authoring Brief

### Public contract
- /app/bin/ashquay is a compiled ELF.
- splice CORE OUTDIR writes OUTDIR/backtrace.txt and OUTDIR/provenance.json.
- Two splices of /app/dumpit/shift.core into /app/outkeg/runA and /app/outkeg/runB must be byte-identical.
- Frames with a source row in some well print NAME at 0xADDR FILE:LINE.
- Provenance objects entries use build_id and host.
- Success writes OUTDIR/ok.mark. Missing build id exits non-zero without ok.mark.
- Source fixes under /app for modules in /app/vatnotes/BAYMAP.txt.
- Pasted outkeg files are insufficient.
- The verifier reruns /app/bin/ashquay splice.

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
- path: environment/hopbag/op_bag.c
  role: host bag
- path: environment/hopbag/op_bag.h
  role: bag header
- path: environment/objbay/n_pick.c
  role: object pick
- path: environment/objbay/n_pick.h
  role: pick header
- path: environment/objbay/readwell.c
  role: object loader
- path: environment/objbay/readwell.h
  role: loader header
- path: environment/ribvat/n_credit.c
  role: provenance credit
- path: environment/ribvat/n_credit.h
  role: credit header
- path: environment/millcue/main.c
  role: argv
- path: environment/vatnotes/BAYMAP.txt
  role: layout map
- path: environment/vatnotes/forms.txt
  role: grammar

### fix_frontier
- count: 3
- distribution: hopbag, objbay, ribvat
- naming_policy: opaque mill symbols
- forbidden_stems: ashquay, splice, dbgwells, cardurn, backtrace, provenance, host, build_id, outkeg, dumpit, LINE, ELF, desk, objects, cards
- helpers_policy: retry_first helper under sidelog
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: artifacts, process exit, JSON fields
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: retry_first as the host-pin workaround

### category_profile
- challenge_family: concurrent fetch completeness
- bug_family: first-complete object
- profile_name: concurrency_ordering
- allowed_instruction_disclosures: splice paths, two-run identity, FILE:LINE outcome, provenance keys, missing-id exit, ELF mill
- forbidden_instruction_leaks: outdir hash bag, names-only first pick, retry_first credit, race recipe
- category_specific_hardness_bar: bag, pick, and credit must coordinate; retry_first must not pass
- category_specific_verifier_risks: pasted JSON, script mill, retry_first
- coverage_role: C split-debug mill vs existing C decoder mills

### difficulty_mechanism_plan
- mechanisms: [false_green_intermediate_states, buried_local_constraints, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants]
- adversarial_layers_count: 4
- fairness_guardrails: two-run identity and FILE:LINE outcome are public; bag hash and names-first pick are not
- mechanism: false_green_intermediate_states
  placement: splice exits 0 with matching function names
  why_model_misses_it: names look finished
  fairness_guardrail: two trees must match and FILE:LINE is public
- mechanism: buried_local_constraints
  placement: names-only vs line table objects sharing a build id
  why_model_misses_it: both objects look valid
  fairness_guardrail: source rows must print
- mechanism: deceptive_but_valid_local_evidence
  placement: mill.cfg retry_first plus decoykit
  why_model_misses_it: looks like host pin
  fairness_guardrail: host must be the used object well
- mechanism: cross_file_cross_format_invariants
  placement: bag vs pick vs credit
  why_model_misses_it: one locus leaves another drifting
  fairness_guardrail: forms.txt names both artifacts

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: splice shift.core twice and compare trees plus FILE:LINE
- shortcut_audit: retry_first, pasted emitvat, script mill, source-only
- ablation_plan: drop bag, drop pick, drop credit separately
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Claude Opus 5 and GPT-5.6 worst-model floor

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: all graded tests pass after splice on the rebuilt mill

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: local C mill only
- long_context_token_floor: 0

### satisfiability_risk
- rc2_planned_name_risk: low — opaque op_bag/n_pick/n_credit
- gx9_contract_risk: low — no scenario-key-value tables
- cr1_symbol_frontier_risk: medium — keep CLI nouns off fix symbols
- hidden_contract_risk: low — keys and two-run rule are public

### actionability_plan
- verifier_command_visible: `/app/bin/ashquay splice`
- source_fix_intent_visible: C modules listed in BAYMAP.txt need source updates under /app
- generated_output_rule_visible: backtrace.txt provenance.json ok.mark
- exact_formula_home: `/app/vatnotes/forms.txt`
- schema_home: `/app/vatnotes/forms.txt`

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected; canonical gcc image, offline wheels, no multi-container

### reference_pattern
- justification_if_none: no promoted reference matches a split-debug splice mill whose two runs agree on names while provenance hosts and line-bearing frames drift

### realism_source
- source_type: real_system
- evidence_basis: debuginfod/symbol-server first-complete fetch racing a richer slower object
- upstream_or_synthetic_rationale: minimized from concurrent debuginfod clients that accept the first matching build-id payload
- minimization_preserves: first-complete bag, names-only vs line tables, retry-first contact stamp
- synthetic_exception_review: not required

### Failure topology
Two splices of one dump print the same function names while provenance hosts move and one listing gains extra FILE:LINE suffixes. Each tree is internally consistent. retry_first looks like a pin.

### Environment shape
CLI under millcue, host bag under hopbag, object pick under objbay, credit under ribvat, cards under cardurn, objects under dbgwells, dumps under dumpit, grammar under vatnotes, retry helper under sidelog.

### Required artifacts
Standard Harbor scaffold, digest-pinned gcc runtime with python verifier venv, C mill, oracle copies, pytest suite, rubric, preship probes.

### Test plan
- ELF mill plus line-bearing frames on shift.core
- runA and runB byte-identical
- aabbccdd host is midquay
- eeff0011 host is deepwell
- missing id nonzero
- missing id leaves no ok.mark
- ok.mark after success
- held-out dump
- corrupt then splice recovers
- objects key shape
- name/line grammar
- one splice argv

### Drafting guardrails
Do not name outdir hash, names-first pick, or retry_first as the fix. Keep handbook symptoms-only.

### Triviality Ledger
- retry_first still stamps every object with the contact well; credit tests block that decoy.
- Pasted emitvat files fail when grade corrupts them and reruns splice.
- Source-only edits leave the prebuilt `/app/bin/ashquay` hashing OUTDIR to a single well.

### Per-gate Pitfall Inventory
- RC2: fix files stay op_bag.c / n_pick.c / n_credit.c; no broken_* names; no extensionless files under fix dirs.
- GX9: grade artifacts and exits, not boolean answer keys.
- CR1: oracle symbols op_bag, n_pick, n_credit stay off CLI nouns in the same patch-verb sentence.
- R5: tests never rebuild; they invoke `/app/bin/ashquay`.
- GX3: oracle replaces three C bodies plus hull rebuild, not one-liners.
- R7: ELF assert on the linked mill; shortcut replaces it with a script.

### Initial Draft Commitments
- environment/hopbag/op_bag.c
- environment/hopbag/op_bag.h
- environment/objbay/n_pick.c
- environment/objbay/n_pick.h
- environment/objbay/readwell.c
- environment/objbay/readwell.h
- environment/ribvat/n_credit.c
- environment/ribvat/n_credit.h
- environment/millcue/main.c
- environment/millcue/go.c
- environment/millcue/fin.c
- environment/millcue/ash.h
- environment/millcue/hull.mk
- environment/sidelog/retry.c
- environment/sidelog/retry.h
- environment/vatnotes/BAYMAP.txt
- environment/vatnotes/forms.txt
- environment/vatnotes/ops.txt
- environment/cardurn/fastpit.card
- environment/cardurn/deepwell.card
- environment/cardurn/midquay.card
- environment/dbgwells/fastpit/aabbccdd.dbg
- environment/dbgwells/fastpit/eeff0011.dbg
- environment/dbgwells/deepwell/aabbccdd.dbg
- environment/dbgwells/deepwell/eeff0011.dbg
- environment/dbgwells/midquay/aabbccdd.dbg
- environment/dbgwells/midquay/99887766.dbg
- environment/dumpit/shift.core
- environment/mill.cfg
- environment/slimbox/wheels
- environment/slimbox/debs
- environment/Dockerfile
- environment/.dockerignore
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- solution/op_bag.c
- solution/n_pick.c
- solution/n_credit.c
- instruction.md
- task.toml
- output_contract.toml
- construction_manifest.json
- rubric.txt
- preship/preship.json
- preship/source_only.sh
- preship/decoy_fix.sh
- preship/shortcut_fix.sh

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table
- path: environment/hopbag/op_bag.c
  symbol: op_bag
  kind: function
  signature: int op_bag(const char *a, char b[][64], int c)
  purpose: Fills the list of wells to query for this output directory.
- path: environment/objbay/n_pick.c
  symbol: n_pick
  kind: function
  signature: int n_pick(const struct Obj *a, int b)
  purpose: Returns the index of the debug object to use.
- path: environment/ribvat/n_credit.c
  symbol: n_credit
  kind: function
  signature: int n_credit(const char *a, const struct Sel *b, int c)
  purpose: Writes the provenance objects list.

#### flipping_point_contract
locations:
  - id: A
    path: environment/hopbag/op_bag.c
    controls_tests: [test_aq02_twin_trees, test_aq01_magic_stock, test_aq07_corrupt_again, test_aq12_one_proc]
  - id: B
    path: environment/objbay/n_pick.c
    controls_tests: [test_aq06_held_row, test_aq11_name_shape, test_aq04_void_exit, test_aq10_void_nomark]
  - id: C
    path: environment/ribvat/n_credit.c
    controls_tests: [test_aq03_row_host, test_aq08_second_id, test_aq09_key_shape, test_aq05_ok_flag]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest
- path: environment/sidelog/retry.c
  kind: helper
  rhymes_with: n_credit
  non_fix_purpose: Optional first-contact log used by an unused sidecar.

#### code_forbidden_tokens
code_forbidden_tokens: [ashquay, splice, dbgwells, cardurn, backtrace, provenance, host, build_id, outkeg, dumpit, LINE, ELF, desk, objects, cards]
