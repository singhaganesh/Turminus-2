### Decision
GO — Attempt 1. Debugging repair: aborting sting leaves a truncated on-disk last-words file while the returning ease path looks whole. Three cooperating write-path loci (knit class, buffered spool, Drop seal) plus rustc rebuild.

### Metadata
- version: 2
- Task name: finspool-keel
- Title: Abort path drops last words
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["rust"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["rust", "fault-record", "stdio", "rebuild"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/finspool` is a compiled ELF (`\x7fELF`).
- `knit` refreshes generated mill pieces.
- `sting THREAD OP DEST` takes the non-returning path; `DEST` must then hold four lines: `FIN1`, `thread=<THREAD>`, `op=<OP>`, `END`.
- `look DEST` reprints those lines and exits 0 only when the file is whole.
- `ease` is the returning path; both paths must name the passed thread and op.
- `DEST` under `/app/bloturn`; other destinations exit non-zero and must not leave a success file.
- Corrupt `DEST` then another `sting` restores a whole file.
- Source fixes under `/app`; modules named in `/app/vatnote/ROUTE.txt`.
- Hand-copied `final.rec` is not enough. Desk reruns `sting` then `look` on `/app/bloturn/final.rec`.

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
  role: Rust+python offline image
- path: construction_manifest.json
  role: local authoring artifact

### task_files

- path: environment/spindock/modes.rs
  role: knit-time class for hard vs returning emit
- path: environment/hookvat/spool.rs
  role: dest open and write channel
- path: environment/hookvat/seal.rs
  role: closing mark emission
- path: environment/spindock/spin.rs
  role: generator that writes hookvat/gen_emit.rs
- path: environment/fincli/boot.rs
  role: CLI
- path: environment/spindock/text.rs
  role: string helper used by spin
- path: environment/hookvat/open.rs
  role: dest prefix helper
- path: environment/hookvat/gen_emit.rs
  role: knitted emit body
- path: environment/scanpit/peek.rs
  role: reader

### fix_frontier

- count: 3
- distribution: spindock, hookvat spool, hookvat seal
- naming_policy: opaque op_a op_b op_c
- forbidden_stems: sting, look, knit, thread, mill, bloturn
- helpers_policy: slipcards/cap.rs decoy ROOM off frontier
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: four-line record, look exit, ELF magic
- forbidden_assertion_styles: boolean answer keys

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: enlarge ROOM so a short card appears to flush

### category_profile

- challenge_family: crash_record_durability
- bug_family: crash_record_durability
- profile_name: state_recovery_crash_consistency
- allowed_instruction_disclosures: commands, paths, four-line schema, symptoms
- forbidden_instruction_leaks: BufWriter, abort skips Drop, inverted knit class
- category_specific_hardness_bar: returning path already whole; aborting path empty until three write-path loci cooperate
- category_specific_verifier_risks: test-side rustc, hand final.rec, script mill
- coverage_role: debugging C2 rebuild-before-claim

### difficulty_mechanism_plan

- mechanisms: false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, stateful_multi_step_dependencies
- adversarial_layers_count: 4
- fairness_guardrails: local deterministic CLI
- mechanism: false_green_intermediate_states
  placement: ease already writes a whole file
  why_model_misses_it: handler body looks correct
  fairness_guardrail: sting path is the graded abort
- mechanism: deceptive_but_valid_local_evidence
  placement: slipcards ROOM and vatnote card-size note
  why_model_misses_it: enlarge buffer
  fairness_guardrail: held-out long op still empty
- mechanism: cross_file_cross_format_invariants
  placement: knit class vs spool vs seal
  why_model_misses_it: patch one locus
  fairness_guardrail: four lines must all be on disk
- mechanism: stateful_multi_step_dependencies
  placement: hull.sh knit then rustc
  why_model_misses_it: skip rebuild
  fairness_guardrail: ELF plus regenerated gen_emit.rs

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: sting then look, rustc
- shortcut_audit: ROOM bump, hand rec, script bin
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
- sidecar_or_protocol_notes: none

### satisfiability_risk

- rc2_planned_name_risk: low — spindock/hookvat names
- gx9_contract_risk: low four-line schema not a scenario table
- cr1_symbol_frontier_risk: low three symbols
- hidden_contract_risk: low public schema

### actionability_plan

- verifier_command_visible: sting then look
- source_fix_intent_visible: ROUTE.txt modules
- generated_output_rule_visible: bloturn/final.rec four lines
- exact_formula_home: thread= and op= interpolation
- schema_home: instruction.md

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- justification_if_none: no promoted reference for a Rust last-words mill whose aborting sting drops a buffered record while ease still looks whole

### realism_source

- source_type: real_bug
- evidence_basis: stdio/BufWriter plus abort skipping destructors; inverted emit class in a codegen table
- upstream_or_synthetic_rationale: classic libc abort vs atexit flush; RAII trailer never runs
- minimization_preserves: content correct in memory, missing on disk after abort
- synthetic_exception_review: not required

### Failure topology
Returning ease leaves a whole four-line file because destructors run. sting ends without returning, so a gather-until-exit knit class, a buffered spool, and a closing mark in Drop never reach disk. Enlarging ROOM looks locally helpful and still loses a longer held-out op.

### Environment shape
A CLI crate, a knit generator, a spool, a seal, a look reader, templates, vatnote map, slipcards ROOM decoy, hull rebuild, offline debs/wheels.

### Required artifacts
instruction, tests, Dockerfile with verifier deps, solve.sh, task.toml with allow_internet false, environment components listed in Initial Draft Commitments.

### Test plan
- test_fs01_hdr_tok: FIN1 present after sting
- test_fs02_live_nam: thread= line after sting
- test_fs03_held_verb: held-out op= after sting
- test_fs04_close_mark: file ends with END
- test_fs05_long_verb: second held-out op
- test_fs06_pair_same: sting and ease name the same thread
- test_fs07_bin_magic: ELF plus whole record
- test_fs08_one_proc: one sting subprocess
- test_fs09_read_code: look exits 0 on whole file
- test_fs10_bad_root: ease outside bloturn nonzero, no success file
- test_fs11_dirty_redo: corrupt then sting restores
- test_fs12_zero_body: look nonzero on empty dest

### Drafting guardrails
Do not name BufWriter, abort, Drop, flush, or hull.sh in instruction.md. Keep ROUTE.txt as operator notes. No bug comments. Oracle full-file writes.

### Triviality Ledger

- Enlarging spool ROOM can look like a flush fix on a short card and still lose a longer held-out op because abort never runs Drop.
- Hand-writing final.rec fails recovery because sting overwrites from the running mill.
- A script mill fails the ELF check on `/app/bin/finspool`.

### Per-gate Pitfall Inventory

- RC2: fix paths stay under spindock and hookvat with source files only.
- GX9: instruction states the four-line schema, not a scenario answer table.
- CR1: oracle symbols are op_a, op_b, op_c.
- CR8: boot dispatches; knit is a separate binary.
- GX6: symptoms only; no causal patch recipe.
- R5: tests never call hull.sh; they grade the prebuilt mill.
- R7: ELF magic on the mill after the agent rebuild plus held-out op.

### Initial Draft Commitments

- task.toml
- instruction.md
- output_contract.toml
- construction_manifest.json
- rubric.txt
- tests/test.sh
- tests/test_outputs.py
- solution/solve.sh
- environment/Dockerfile
- environment/.dockerignore
- environment/hull.sh
- environment/fincli/boot.rs
- environment/fincli/usage.txt
- environment/spindock/spin.rs
- environment/spindock/modes.rs
- environment/spindock/text.rs
- environment/hookvat/spool.rs
- environment/hookvat/seal.rs
- environment/hookvat/open.rs
- environment/scanpit/peek.rs
- environment/scanpit/fmt.rs
- environment/tplfold/emit.tpl
- environment/tplfold/modes.knt
- environment/vatnote/ROUTE.txt
- environment/vatnote/FORMAT.txt
- environment/slipcards/cap.rs
- environment/slipcards/NOTE.txt
- environment/opsleaf/SHIFT.txt
- environment/debcue/README.txt
- environment/debcue/debs/
- environment/debcue/wheels/
- preship/preship.json
- preship/source_only.sh
- preship/decoy_fix.sh
- preship/shortcut_fix.sh
- preship/alt_solution.sh

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table

- path: environment/spindock/modes.rs
  symbol: op_a
  kind: function
  signature: op_a(k: u8) -> u8
  purpose: returns the knit-time emit class for a path kind
- path: environment/hookvat/spool.rs
  symbol: op_b
  kind: function
  signature: op_b(p: &str) -> std::io::BufWriter<std::fs::File>
  purpose: opens the dest write channel
- path: environment/hookvat/seal.rs
  symbol: op_c
  kind: function
  signature: op_c(w: &mut W) -> Guard
  purpose: attaches the closing mark for the dest channel

#### flipping_point_contract

locations:
  - id: A
    path: environment/spindock/modes.rs
    controls_tests: [test_fs02_live_nam, test_fs05_long_verb, test_fs06_pair_same, test_fs01_hdr_tok]
  - id: B
    path: environment/hookvat/spool.rs
    controls_tests: [test_fs03_held_verb, test_fs10_bad_root, test_fs08_one_proc, test_fs07_bin_magic]
  - id: C
    path: environment/hookvat/seal.rs
    controls_tests: [test_fs04_close_mark, test_fs09_read_code, test_fs11_dirty_redo, test_fs12_zero_body]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest

- path: environment/slipcards/cap.rs
  kind: helper
  rhymes_with: op_b
  non_fix_purpose: publishes a ROOM constant unused by the mill
- path: environment/vatnote/FORMAT.txt
  kind: config-reader
  rhymes_with: op_c
  non_fix_purpose: describes the four-line card shape
- path: environment/opsleaf/SHIFT.txt
  kind: helper
  rhymes_with: op_a
  non_fix_purpose: notes that ease already looks whole

#### code_forbidden_tokens

code_forbidden_tokens: [Investigators, vatnote, bloturn, final.rec, mill, sting, THREAD, DEST, lines, FIN1, thread, END, Truncated, ease, ELF, finspool, knit, look]
