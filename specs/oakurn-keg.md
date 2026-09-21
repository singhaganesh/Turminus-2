### Decision
GO — Attempt 1. Debugging repair of a C++ crash-desk mill: overlapping pours leave steep green while the board stalls; coverage stamp, calendar fold, and idle mill status sit in three roots. Exclusive-hold decoy is punished.

### Metadata
- version: 2
- Task name: oakurn-keg
- Title: Desk totals freeze busy
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c++"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c++", "crash", "mill", "desk"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/oakurn` is a compiled ELF.
- `pour` loads an urn from `/app/caskbay`.
- `steep` regenerates `/app/inkpit/counts.json`.
- `board` prints that JSON.
- JSON keys `days` and `covers` as in `/app/treenote/forms.txt`.
- After pour, `covers` equals that urn identifier; `days` uses the urn's own day field.
- Steep that did no mill work exits non-zero.
- Source fixes under `/app` for modules in `/app/treenote/TREE.txt`.
- Pasted counts.json is insufficient.

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
- path: environment/latchpit/op_a.cpp
  role: mill admit
- path: environment/stampwire/op_b.cpp
  role: coverage stamp
- path: environment/dayfold/n_fold.cpp
  role: calendar fold
- path: environment/ribcli/hull_cli.cpp
  role: CLI
- path: environment/treenote/forms.txt
  role: grammar
- path: environment/treenote/TREE.txt
  role: layout map

### fix_frontier
- count: 3
- distribution: latchpit, stampwire, dayfold
- naming_policy: opaque mill symbols
- forbidden_stems: oakurn, board, pour, steep, caskbay, inkpit, counts, covers, days, mill, urn, ELF, desk
- helpers_policy: exclusive-hold helper under holdbay
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
- collapse_risk: exclusive mill hold as the busy-floor workaround

### category_profile
- challenge_family: generated artifact completeness
- bug_family: stale generator view
- profile_name: build_dependency_toolchain
- allowed_instruction_disclosures: pour/steep/board, JSON keys, urn day field, idle non-zero, ELF mill
- forbidden_instruction_leaks: latch skip, last.id stamp, clock.snap fold, exclusive --hold recipe
- category_specific_hardness_bar: admit, coverage stamp, and day fold must coordinate with idle status
- category_specific_verifier_risks: pasted JSON, exclusive hold, script mill
- coverage_role: C++ crash-desk mill vs existing C/Go decoder mills

### difficulty_mechanism_plan
- mechanisms: [false_green_intermediate_states, buried_local_constraints, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants]
- adversarial_layers_count: 4
- fairness_guardrails: symptoms and public JSON/day/idle rules are visible; latch skip and clock fold are not
- mechanism: false_green_intermediate_states
  placement: steep exits 0 while counts.json stays behind
  why_model_misses_it: success looks like a finished mill
  fairness_guardrail: idle non-zero is public
- mechanism: buried_local_constraints
  placement: urn day field vs mill wall stamp
  why_model_misses_it: totals can look internally consistent
  fairness_guardrail: urn day rule is public
- mechanism: deceptive_but_valid_local_evidence
  placement: holdbay hold helper
  why_model_misses_it: exclusive hold looks like the busy-floor cure
  fairness_guardrail: board still must print regenerated JSON
- mechanism: cross_file_cross_format_invariants
  placement: covers, days, steep status
  why_model_misses_it: fixing one field leaves another stale
  fairness_guardrail: forms.txt names both keys

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert pours an urn then checks covers and day keys
- shortcut_audit: exclusive hold, pasted JSON, script mill, source-only
- ablation_plan: drop admit, drop stamp, drop fold separately
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Claude Opus 5 and GPT-5.6 worst-model floor

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: all graded tests pass after pour, steep, and board on the rebuilt mill

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: local C++ mill only
- long_context_token_floor: 0

### satisfiability_risk
- rc2_planned_name_risk: low — opaque op_a/op_b/n_fold names
- gx9_contract_risk: low — no scenario-key-value tables
- cr1_symbol_frontier_risk: medium — keep CLI nouns off fix symbols
- hidden_contract_risk: low — day field and idle exit are public

### actionability_plan
- verifier_command_visible: `/app/bin/oakurn pour`, `steep`, `board`
- source_fix_intent_visible: C++ modules listed in TREE.txt need source updates under /app
- generated_output_rule_visible: counts.json
- exact_formula_home: `/app/treenote/forms.txt`
- schema_home: `/app/treenote/forms.txt`

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected; canonical gcc image, offline wheels, no multi-container

### reference_pattern
- justification_if_none: no promoted reference matches a crash-desk mill whose overlapping pours leave steep green while coverage identity and calendar fold drift

### realism_source
- source_type: real_system
- evidence_basis: analytics rollup CLIs that no-op when a mill lock is held and still report success
- upstream_or_synthetic_rationale: minimized from warehouse refresh jobs that skip when another refresh is in flight
- minimization_preserves: skip-on-busy success, stale coverage identity, wall-clock day buckets
- synthetic_exception_review: not required

### Failure topology
Steep returns success during overlapping pours while desk totals freeze. Internally consistent JSON still names an old urn and parks events on a mill wall day. A second steep with no new mill work also stays green.

### Environment shape
Urns under caskbay, mill CLI under ribcli, admit under latchpit, coverage stamp under stampwire, calendar fold under dayfold, grammar under treenote, products under inkpit, wall stamp under snapvat, exclusive-hold decoy under holdbay.

### Required artifacts
Standard Harbor scaffold, digest-pinned gcc runtime with python verifier venv, C++ mill, oracle copies, pytest suite, rubric, preship probes.

### Test plan
- ELF mill plus coverage mark after pour and steep
- urn day key not mill wall stamp
- held-out urn lands
- idle steep non-zero
- twin-day totals
- busy latch still folds
- one steep process
- corrupt JSON then steep recovers
- board prints regenerated object
- extra urn at grade time
- key order days then covers
- idle fingerprint after a real mill pass

### Drafting guardrails
Do not name latch skip, last.id, clock.snap, or exclusive hold as the fix. Keep handbook symptoms-only.

### Triviality Ledger
- Exclusive `--hold` still parks events on the mill wall stamp; twin-day urns block that decoy.
- Pasted counts.json fails when grade corrupts the file and reruns steep.
- Source-only edits leave the prebuilt `/app/bin/oakurn` skipping mill work.

### Per-gate Pitfall Inventory
- RC2: fix files stay op_a.cpp / op_b.cpp / n_fold.cpp; no broken_* names; no extensionless files under fix dirs.
- GX9: grade JSON fields and exits, not boolean answer keys.
- CR1: oracle symbols op_a, op_b, n_fold stay off CLI nouns in the same patch-verb sentence.
- R5: tests never rebuild; they invoke `/app/bin/oakurn`.
- R3: every graded test fails on the shipped tree.

### Initial Draft Commitments
- environment/latchpit/op_a.cpp
- environment/stampwire/op_b.cpp
- environment/dayfold/n_fold.cpp
- environment/ribcli/hull_cli.cpp
- environment/ribcli/run_k.cpp
- environment/ribcli/hull.mk
- environment/ribcli/hull.hpp
- environment/latchpit/admit.hpp
- environment/stampwire/mark.hpp
- environment/dayfold/fold.hpp
- environment/holdbay/hold.cpp
- environment/holdbay/hold.hpp
- environment/treenote/TREE.txt
- environment/treenote/forms.txt
- environment/caskbay/core.urn
- environment/caskbay/quiet.urn
- environment/inkpit/counts.json
- environment/snapvat/busy.latch
- environment/snapvat/clock.snap
- environment/snapvat/last.id
- environment/offpack/wheels
- environment/offpack/debs
- environment/Dockerfile
- environment/.dockerignore
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- solution/op_a.cpp
- solution/op_b.cpp
- solution/n_fold.cpp
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
- path: environment/latchpit/op_a.cpp
  symbol: op_a
  kind: function
  signature: int op_a(void)
  purpose: Returns whether mill work may proceed.
- path: environment/stampwire/op_b.cpp
  symbol: op_b
  kind: function
  signature: int op_b(void)
  purpose: Writes the coverage identifier for the last folded urn.
- path: environment/dayfold/n_fold.cpp
  symbol: n_fold
  kind: function
  signature: int n_fold(void)
  purpose: Folds event totals by calendar day.

#### flipping_point_contract
locations:
  - id: A
    path: environment/latchpit/op_a.cpp
    controls_tests: [test_aa_magic_stock, test_hh_busy_still, test_ii_one_proc, test_ee_corrupt_regen]
  - id: B
    path: environment/stampwire/op_b.cpp
    controls_tests: [test_bb_id_mark, test_cc_held_row, test_kk_extra_row, test_jj_panel_read]
  - id: C
    path: environment/dayfold/n_fold.cpp
    controls_tests: [test_ff_clock_key, test_gg_twin_key, test_ll_key_order, test_dd_idle_nonzero]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest
- path: environment/holdbay/hold.cpp
  kind: helper
  rhymes_with: op_a
  non_fix_purpose: Optional exclusive mill hold used by an unused sidecar.

#### code_forbidden_tokens
code_forbidden_tokens: [oakurn, board, pour, steep, caskbay, inkpit, counts, covers, days, mill, urn, ELF, desk]
