### Decision
GO — Attempt 1. Debugging repair of C reelmark knit/unspool: generated capability table is silently ignored, compiled-in stock set is used, stale blobs still exit zero. Three cooperating modules across warpkit, fibrekit, and quayc. Rebuild lever on `/app/bin/reelmark`.

### Metadata
- version: 2
- Task name: reelmark-shuttle
- Title: Stock set still loaded
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "record-replay", "capability-table", "reelmark"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/reelmark knit` writes `/app/loomcore/emit/capset.tbl` and `/app/loomcore/emit/knit.ok` from `/app/tapewell/desc/calls.lst`.
- `/app/bin/reelmark unspool <spool>` prints JSON keys `loaded`, `status`, `call`.
- `loaded` must start with `table:` plus trimmed `knit.ok`. `builtin:` is rejected on this image.
- Covered spools print `status` `replayed`. `sys_loom_splice` on splice.reel must replay.
- `unspool --blob /app/tapewell/fixtures/stale.tbl` with open.reel exits non-zero and leaves `accept.ok` missing.
- Success writes `/app/shuttlebin/run/accept.ok` = `1` and `/app/shuttlebin/run/loaded.set` equal to JSON `loaded`.
- Grammar in `/app/millnotes/GRAMMAR.txt`. Module map in `/app/millnotes/ROUTE_MAP.txt`.

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
  role: gcc canonical base plus verifier venv
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/warpkit/knitc/hdr_write.c
  role: header stamp writer
- path: environment/fibrekit/floorc/admit.c
  role: blob admit versus stock path
- path: environment/quayc/playc/bank.c
  role: which capability set unspool uses

### fix_frontier
- count: 3
- distribution: warpkit knitc, fibrekit floorc, quayc playc
- naming_policy: opaque C symbols off instruction nouns
- forbidden_stems: splice, builtin, reelmark, tapewell, shuttlebin, loomcore
- helpers_policy: unused compat helper that rhymes with admit
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: JSON traces, accept.ok, loaded.set, process status
- forbidden_assertion_styles: boolean answer keys

### task_shape
- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: lowering BANK_FLOOR so old MARK tables load

### category_profile
- challenge_family: stale_generated_artifacts
- bug_family: stale_generated_artifacts
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, JSON keys, symptoms, grammar home
- forbidden_instruction_leaks: MARK constant, BANK_FLOOR, use_stock flag, patch files
- category_specific_hardness_bar: knit succeeds and table lists the call while unspool still uses stock
- category_specific_verifier_risks: text listing of CALL rows as a scenery pass
- coverage_role: debugging C2 rebuild-before-claim

### difficulty_mechanism_plan
- mechanisms: buried_local_constraints, deceptive_but_valid_local_evidence, false_green_intermediate_states, cross_file_cross_format_invariants, environment_specific_cli_semantics
- adversarial_layers_count: 5
- fairness_guardrails: local deterministic CLI
- mechanism: buried_local_constraints
  placement: header MARK constant lagging table grammar
  why_model_misses_it: knit exits zero and CALL rows look complete
  fairness_guardrail: GRAMMAR.txt documents current grammar
- mechanism: deceptive_but_valid_local_evidence
  placement: stock bank still replays sys_read
  why_model_misses_it: some reels look healthy
  fairness_guardrail: splice.reel is named in the prompt
- mechanism: false_green_intermediate_states
  placement: silent stock path on admit miss
  why_model_misses_it: unspool still prints JSON
  fairness_guardrail: loaded prefix contract is public
- mechanism: cross_file_cross_format_invariants
  placement: knit.ok text must bind loaded suffix
  why_model_misses_it: agents edit only JSON printer
  fairness_guardrail: loaded.set equality is public
- mechanism: environment_specific_cli_semantics
  placement: --blob stale must be a hard refuse
  why_model_misses_it: lowering floor makes stale look loadable
  fairness_guardrail: stale path named in the prompt

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert compares MARK versus BANK_FLOOR versus pick_bank
- shortcut_audit: lower BANK_FLOOR, hand-write emit, skip make
- ablation_plan: revert each of three loci and expect residual fail
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Opus 5 and GPT-5.6

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.json+reward.txt
- binary_threshold_rule: reward 1 only when every graded test passes

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: recordings and fixtures bundled under tapewell

### satisfiability_risk
- rc2_planned_name_risk: low — fix dirs are knitc/floorc/playc
- gx9_contract_risk: medium — keep values on artifacts not recitation tables
- cr1_symbol_frontier_risk: low — write_hdr, admit_blob, pick_bank
- hidden_contract_risk: low — grammar in millnotes named from instruction

### actionability_plan
- verifier_command_visible: knit and unspool named
- source_fix_intent_visible: source and implementation work under /app millnotes modules
- generated_output_rule_visible: capset.tbl, knit.ok, loaded.set, accept.ok
- exact_formula_home: loaded = table: + knit.ok
- schema_home: instruction.md plus GRAMMAR.txt

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference matches record-replay capability-table stamp versus stock fallback

### realism_source
- source_type: synthetic_exception
- evidence_basis: syscall record-replay tools that refuse old capability tables and keep a compiled-in allow list
- upstream_or_synthetic_rationale: no public repo can be shipped; causal shape matches rr/strace seccomp allowlists
- minimization_preserves: generate table, version/stamp floor, silent stock fallback, provenance of which set loaded
- synthetic_exception_review: BANK_FLOOR decoy is a realistic compat knob that must not pass graded replay

### Failure topology
Knit completes and the on-disk table lists the new call, so operators trust emit/. Unspool still reports unsupported because the binary never admits the generated blob and keeps a stock allow list. A second knob looks like the fix (drop the admit floor) but accepts fixtures that the public contract says must fail. Provenance (`loaded` / `loaded.set`) only lines up when the admitted table stamp matches knit.ok.

### Environment shape
warpkit knits the table header. fibrekit admits or refuses blobs. quayc selects the active name bank. shuttlebin holds the CLI. loomcore holds emit files. tapewell holds descriptions, reels, and the stale fixture. millnotes holds grammar and the module map.

### Required artifacts
Standard single-step scaffold, gcc digest-pinned image, pytest under /opt/verifier, oracle copies three C files then make hull then knit.

### Test plan
- prefix bind, splice replay, accept marker, stale exit, loaded.set match, openat2 replay, JSON shape, holdout pair, knit.ok bind, no stock prefix, held reel, stale isolation, cross-check stamp, emit recovery
- Multiple approaches: any correct MARK/admit/bank coordination passes
- Recovery reruns knit without make

### Drafting guardrails
Do not name MARK_NOW, BANK_FLOOR, or use_stock in instruction, comments, or filenames. No # BUG. No make in instruction. No tests that only assert CALL rows exist.

### Triviality Ledger
- Lowering BANK_FLOOR accepts stale.tbl — blocked by non-zero --blob test
- Hand-written capset.tbl — blocked by recovery knit from the binary
- Source-only without make — binary still stocks; R5 probe
- Text-only CALL grep — not a graded test

### Per-gate Pitfall Inventory
- RC2: opaque knitc/floorc/playc; route map in millnotes
- GX9: grade JSON and markers, not scenario-key-value recitation
- CR1: write_hdr / admit_blob / pick_bank off CLI nouns in patch sentences
- R5: tests never call make
- R3: no scenery tests on stock-healthy sys_read
- GX6: symptoms without causal patch recipe
- GX3: oracle replaces three substantive C modules

### Initial Draft Commitments
- task.toml
- instruction.md
- output_contract.toml
- construction_manifest.json
- rubric.txt
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- solution/hdr_write.c
- solution/admit.c
- solution/bank.c
- environment/Dockerfile
- environment/.dockerignore
- environment/warpkit/knitc/hdr_write.c
- environment/warpkit/knitc/hdr_write.h
- environment/warpkit/knitc/rows_write.c
- environment/warpkit/knitc/rows_write.h
- environment/warpkit/knitc/mix.c
- environment/warpkit/knitc/mix.h
- environment/warpkit/tagw/note_write.c
- environment/warpkit/tagw/note_write.h
- environment/warpkit/common.h
- environment/fibrekit/floorc/admit.c
- environment/fibrekit/floorc/admit.h
- environment/fibrekit/floorc/compat.c
- environment/quayc/playc/bank.c
- environment/quayc/playc/bank.h
- environment/quayc/playc/stock.c
- environment/quayc/playc/stock.h
- environment/shuttlebin/cli/main.c
- environment/shuttlebin/Makefile
- environment/tapewell/desc/calls.lst
- environment/tapewell/spools/splice.reel
- environment/tapewell/spools/open.reel
- environment/tapewell/spools/held.reel
- environment/tapewell/fixtures/stale.tbl
- environment/millnotes/ROUTE_MAP.txt
- environment/millnotes/GRAMMAR.txt
- environment/millnotes/LAB.txt
- environment/preship files under tasks/reelmark-shuttle/preship/

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table
- path: environment/warpkit/knitc/hdr_write.c
  symbol: write_hdr
  kind: function
  signature: int write_hdr(FILE *fp, const char *stamp)
  purpose: Writes REEL header and MARK/STAMP lines
- path: environment/fibrekit/floorc/admit.c
  symbol: admit_blob
  kind: function
  signature: int admit_blob(const char *path, int *mark_out, char *stamp_out, size_t stamp_cap)
  purpose: Decides whether a table blob may be used
- path: environment/quayc/playc/bank.c
  symbol: pick_bank
  kind: function
  signature: int pick_bank(int admit_rc)
  purpose: Selects stock versus knitted rows for unspool

#### flipping_point_contract
locations:
  - id: A
    path: environment/warpkit/knitc/hdr_write.c
    controls_tests: [test_nck01_prefix_bind, test_nck02_row_play, test_nck06_open_play, test_nck08_holdout_pair, test_nck09_ok_bind, test_nck11_held_play, test_nck13_cross_check]
  - id: B
    path: environment/fibrekit/floorc/admit.c
    controls_tests: [test_nck04_stale_exit, test_nck12_stale_gap, test_nck_zz_blob_recovery]
  - id: C
    path: environment/quayc/playc/bank.c
    controls_tests: [test_nck03_marker_one, test_nck05_set_matches, test_nck07_json_shape, test_nck10_no_stock]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest
- path: environment/fibrekit/floorc/compat.c
  kind: helper
  rhymes_with: admit_blob
  non_fix_purpose: Unused lab-floor helper that returns 2
- path: environment/quayc/playc/stock.c
  kind: helper
  rhymes_with: pick_bank
  non_fix_purpose: Compiled-in stock name list used only on the stock path

#### code_forbidden_tokens
code_forbidden_tokens: [splice, builtin, reelmark, tapewell, shuttlebin, loomcore]
