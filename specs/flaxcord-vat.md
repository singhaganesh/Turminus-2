### Decision
GO — Attempt 1. Debugging repair of a C compact-capture mill: intern-on-insert, hash-bucket chunk walk, and emit that stamps wall time plus unmapped sample ids. Held-out packing, two-process byte identity, and a trailer fault path keep the trap `--serial-decode` from scoring.

### Metadata
- version: 2
- Task name: flaxcord-vat
- Title: Compact capture drift
- Category: debugging
- Task shape: repair_existing_system
- Languages: ["c"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["c", "compact", "intern", "elf"]
- Milestones: 0

## Authoring Brief

### Public contract
- `/app/bin/flaxcord` is a compiled ELF mill.
- `spin DIR OUT` reads a capture directory under `/app/spoolbay` and writes a compact capture.
- `unreel FILE` prints `frame>frame COUNT n` lines ordered by the joined path.
- `differ A B` writes `/app/cordwell/differ.txt` with exactly `quiet` when the compact files match position by position.
- Two process spins of `/app/spoolbay/day` must produce byte-identical `/app/cordwell/live.pfl`.
- `/app/spoolbay/dusk` is the same workload under other chunk names; `differ` of live vs `/app/cordwell/alt.pfl` must be `quiet`.
- Success writes `/app/cordwell/spin.ok`. A chunk missing `END` makes `spin` exit non-zero and omits `spin.ok`.
- Grammar in `/app/vatnotes/forms.txt`. Desk map in `/app/vatnotes/ROUTE.txt`.
- Hand-written compact files are not enough. Verifier reruns `spin`, `unreel`, and `differ`.

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

- path: environment/flaxcli/hull.c
  role: CLI entry
- path: environment/cordspin/bag.c
  role: name intern table
- path: environment/chunkvat/walk.c
  role: chunk directory walk
- path: environment/emitbay/pour.c
  role: compact emit
- path: environment/differbay/cmp.c
  role: position compare
- path: environment/unreelkit/show.c
  role: text decode
- path: environment/vatnotes/forms.txt
  role: wire grammar
- path: environment/vatnotes/ROUTE.txt
  role: module map
- path: environment/spoolbay/day/
  role: primary capture
- path: environment/spoolbay/dusk/
  role: packing variant

### fix_frontier

- count: 3
- distribution: cordspin, chunkvat, emitbay as distinct top-level roots
- naming_policy: opaque op_/cfg_/n_ symbols
- forbidden_stems: flaxcord, spin, unreel, differ, intern, serial
- helpers_policy: serial-decode helper is decoy; token helper is non-fix
- symbol_thin_preferred: true

### contract_surface

- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: [artifact bytes, differ text, unreel lines, exit codes]
- forbidden_assertion_styles: [boolean answer keys]

### task_shape

- type: repair_existing_system
- instruction_framing: symptoms-only
- hardness_source: diagnosis
- collapse_risk: enabling serial-decode or sorting one table without remapping emit

### category_profile

- challenge_family: concurrency_ordering
- bug_family: intern_and_emit_order
- profile_name: file_format_serialization
- allowed_instruction_disclosures: commands, paths, quiet marker, unreel line shape, ELF, fault trailer, source-fix intent
- forbidden_instruction_leaks: arrival intern, hash-bucket walk, wall-clock stamp, remap recipe, serial-decode as the fix
- category_specific_hardness_bar: parse, normalize, serialize, and packing variant must interact
- category_specific_verifier_risks: golden compact in env, scenery unreel-only tests that pass on NOP
- coverage_role: compact intern table vs index differ, not census/hooks

### difficulty_mechanism_plan

- mechanisms: [false_green_intermediate_states, deceptive_but_valid_local_evidence, cross_file_cross_format_invariants, environment_specific_cli_semantics]
- adversarial_layers_count: 4
- fairness_guardrails: public paths and differ/unreel contract stated; mechanism withheld
- mechanism: false_green_intermediate_states
  placement: unreel of one run looks correct
  why_model_misses_it: stops after one decode
  fairness_guardrail: instruction reports noisy differ and two-process byte drift
- mechanism: deceptive_but_valid_local_evidence
  placement: --serial-decode in flaxcli/serial.c and vatnotes
  why_model_misses_it: docs promise stable tables
  fairness_guardrail: handbook describes the flag as worker join only, not a pass recipe
- mechanism: cross_file_cross_format_invariants
  placement: bag.c vs walk.c vs pour.c
  why_model_misses_it: fixing one locus leaves packing differ red
  fairness_guardrail: dusk packing is a stated public case
- mechanism: environment_specific_cli_semantics
  placement: spin.ok and missing END trailer
  why_model_misses_it: success marker left in place on fault
  fairness_guardrail: instruction states both polarities

### calibration_plan

- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert can trace intern, walk buckets, and stamp in a few hours
- shortcut_audit: serial-decode only, hand-written pfl, script mill, source-only skip hull
- ablation_plan: revert each of bag/walk/pour and expect a declared test subset to fail
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
- cr1_symbol_frontier_risk: low — op_bag/cfg_walk/n_pour off CLI nouns
- hidden_contract_risk: low — forms.txt states wire fields without sort recipe

### actionability_plan

- verifier_command_visible: flaxcord spin, unreel, differ
- source_fix_intent_visible: source fixes under /app required; modules in ROUTE.txt
- generated_output_rule_visible: live.pfl, alt.pfl, differ.txt, spin.ok; hand-written insufficient
- exact_formula_home: unreel line shape in instruction; wire in forms.txt
- schema_home: instruction plus forms.txt

### waiver_plan

- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern

- reference_task_id:
- justification_if_none: docs/reference_tasks/index.json has no promoted references; compact intern mill is not a clone of a listed candidate

### realism_source

- source_type: real_system
- evidence_basis: pprof-style shared string tables and index-by-index capture differs; arrival intern under concurrent chunk decode
- upstream_or_synthetic_rationale: minimized to three C loci plus a serial-decode decoy
- minimization_preserves: intern permutation vs decode-correctness, packing-variant identity
- synthetic_exception_review: not required

### Failure topology
Operators see matching unreels and a green serial flag, while two process compact files and two packing layouts still differ at every sample index because ids follow insert order, chunk labels follow hash buckets, and the emit path stamps wall time without remapping ids.

### Environment shape
CLI hull, intern bag, chunk walk, emit pour, differ, unreel, vatnotes, two spool captures, hull rebuild, serial decoy.

### Required artifacts
Standard task tree, gcc image, pytest under /opt/verifier, native ELF mill, preship R5/R6/R7, rubric.txt.

### Test plan
- header ELF
- two-process byte identity
- packing-variant differ hush
- unreel path order
- held-out packing
- missing trailer exit
- spin.ok on success
- corrupt then spin
- hit totals
- one child per spin
- differ.txt token
- peer unreel match
- ELF still native

### Drafting guardrails
Do not name arrival intern, hash buckets, wall-clock, or remap in instruction, comments, or test names. Do not put golden compact files under environment/.

### Triviality Ledger

- `--serial-decode` joins a no-op worker flag and leaves hash walk plus intern plus stamp untouched; packing-variant differ stays noisy.
- Sorting the string table without remapping sample ids makes unreel lie; tests require both hush differ and ordered unreel lines.
- Hand-written live.pfl fails corrupt-then-spin recovery.

### Per-gate Pitfall Inventory

- RC2: fix files bag.c/walk.c/pour.c; no golden_* names.
- GX9: grade bytes, quiet token, line order; no boolean keys.
- CR1: oracle symbols op_bag, cfg_walk, n_pour.
- R5: tests never make/hull; they invoke /app/bin/flaxcord.
- R3: every graded test fails on the shipped tree (stamp, hash order, intern).

### Initial Draft Commitments

- environment/Dockerfile
- environment/.dockerignore
- environment/hull.sh
- environment/flaxcli/hull.c
- environment/flaxcli/hull.mk
- environment/flaxcli/serial.c
- environment/flaxcli/serial.h
- environment/flaxcli/token.c
- environment/flaxcli/token.h
- environment/flaxcli/wire.h
- environment/cordspin/bag.c
- environment/cordspin/bag.h
- environment/chunkvat/walk.c
- environment/chunkvat/walk.h
- environment/emitbay/pour.c
- environment/emitbay/pour.h
- environment/differbay/cmp.c
- environment/differbay/cmp.h
- environment/unreelkit/show.c
- environment/unreelkit/show.h
- environment/vatnotes/ROUTE.txt
- environment/vatnotes/forms.txt
- environment/spoolbay/day/k0.chk
- environment/spoolbay/day/k1.chk
- environment/spoolbay/dusk/m7.chk
- environment/spoolbay/dusk/m2.chk
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
- path: cordspin/bag.c
  symbol: op_bag
  kind: function
  signature: uint32_t op_bag(const char *a)
  purpose: Records a frame name into the shared table.
- path: chunkvat/walk.c
  symbol: cfg_walk
  kind: function
  signature: int cfg_walk(const char *a)
  purpose: Loads capture chunks into the emit buffer.
- path: emitbay/pour.c
  symbol: n_pour
  kind: function
  signature: int n_pour(const char *a)
  purpose: Writes the compact capture bytes.
```

#### flipping_point_contract

```
locations:
  - id: A
    path: environment/cordspin/bag.c
    controls_tests: [test_fxv03_pair, test_fxv05_hold, test_fxv09_hits]
  - id: B
    path: environment/chunkvat/walk.c
    controls_tests: [test_fxv06_tail, test_fxv07_seal, test_fxv10_child, test_fxv13_stay]
  - id: C
    path: environment/emitbay/pour.c
    controls_tests: [test_fxv01_hdr, test_fxv02_twin, test_fxv04_ord, test_fxv08_mint, test_fxv11_hush, test_fxv12_peer]
no_single_location_flips_majority: true
concentration_cap: 0.5
```

Need walk.c to uniquely fail tail/seal - walk validates END. pour controls stamp (twin) and line order. bag controls packing ids (pair/hold).

Wait C has 6 tests, A 3, B 4, union 13. C is 6/13=0.46 < 0.5. OK.

If reverting bag doesn't fail pair because pour still has clock... pair is live vs alt, BOTH have different clocks so pair fails even with bag fixed? Both spins in same test are sequential so clocks differ regardless of intern!

**pair_quiet ALWAYS fails if stamp is wall clock**, even after intern+walk fix, until pour stamp is 0.

Then bag.c revert: if pour is fixed (stamp 0, remap, sort samples) and walk is fixed (SEQ order), intern arrival still permutes ids between day vs dusk because chunk content order... if walk is SEQ order, both packings visit SEQ1 then SEQ2, intern arrival is THE SAME. Then bag revert wouldn't fail pair!

**When walk is SEQ-sorted, intern-on-arrival is packing-stable.** Bag only matters when walk is hash order.

CR2 isolate bag: need a test where walk is already sequential but intern still wrong... that's impossible if walk order is deterministic and same SEQ.

**Independent bag bug:** intern uses a hash table of names iterated by bucket for the STRING TABLE EMIT order (not first-id). IDs assigned by hash bucket order of the name, not sort and not walk. Packing doesn't matter. Two-run is stable (deterministic hash). Then packing-variant also stable!

Then bag doesn't affect packing at all. Only string table permutation that's deterministic... two-run identical, packing identical. Bag becomes scenery.

**Need intern to depend on walk order** for packing tests, which couples bag and walk.

Standard approach for CR2 with coupled bugs: tests that fail when THAT file is reverted from oracle while others stay fixed.

Oracle: bag sorts names, walk SEQ, pour stamp0+remap+sort samples.

Revert bag only (arrival intern): walk SEQ so both packings intern in same order → pair might PASS. FAIL CR2 for bag.

**Fix:** dusk packing uses different SEQ labels for the same stacks? No that would be different workload.

**Bag unique behavior:** duplicate name folding. Broken intern creates two ids for the same name if they differ by trailing space / case. day.chk has `alpha.tick`, dusk has `alpha.tick` only... 

**Bag: first-insert id, but freeze should uniq+sort.** If walk visits in SEQ order, same.

Give dusk a third chunk that's empty? 

**Use different first-seen order with SEQ still defined:** SEQ is the logical id but broken walk ignores SEQ and uses filename hash. Oracle walk uses SEQ. Revert walk: hash order. Revert bag: even with SEQ walk, if we **intern at emit of string table using hash(name)** not sorted... packing-stable, two-run stable. Need two-run to depend on bag? Can't if deterministic.

**Put PID in intern?** Too obvious.

**Bag controls held-out names that appear in a different first-seen order in the holdout fixture** while walk is SEQ. Holdout packing H has SEQ1 stack `rho.nock` first, SEQ2 `alpha.tick`. Main day has SEQ1 `zeta.main`+`alpha.tick`. Canonical sort makes holdout match a second holdout packing. Two holdout dirs in tests: hold_a and hold_b with swapped SEQ but same names. Tests copy them at grade time.

day/dusk: same SEQ order of names, so intern-arrival with SEQ walk is identical. Then bag doesn't affect day/dusk pair!

**day vs dusk only tests walk (hash vs SEQ) + pour (stamp, sample order).**

**hold_a vs hold_b tests bag** (different first-seen if walk uses file hash of hold filenames... messy).

If oracle walk is SEQ, hold_a SEQ1=rho, SEQ2=alpha vs hold_b SEQ1=alpha, SEQ2=rho. Arrival intern assigns different ids. Sorted intern assigns same. **pair of holdouts controlled by bag.c**. day/dusk have identical SEQ name order so bag doesn't affect them.

day k0 SEQ1 zeta+alpha, k1 SEQ2 mu
dusk m2 SEQ1 zeta+alpha, m7 SEQ2 mu  — same SEQ content, only filenames differ. Hash walk permutes. SEQ walk same intern.

Flipping:
- A bag.c: holdout pair (test_fxv05_hold)
- B walk.c: day vs dusk (test_fxv03_pair) 
- C pour.c: two-process (test_fxv02_twin), unreel order (test_fxv04_ord)

Need more tests per location to balance. Spread ELF, recovery, fault.

Walk validates END → test_fxv06_tail
Pour writes spin.ok? Better walk or hull. Put spin.ok in hull.c after n_pour - not a fix file.

spin.ok in pour.c after successful write. Revert pour: maybe still writes ok with bad bytes. test_fxv07 still passes on NOP if pour writes ok!

NOP pour still succeeds and writes ok. test_fxv07_seal would PASS on NOP. **Forbidden.**

spin.ok must not exist on NOP... or content must include a digest of canonical bytes. Too leaky.

**Grade spin.ok presence only after other asserts in same test** that already fail... still if we assert exists, NOP has it.

Don't test spin.ok presence alone. Test: on fault, spin.ok absent. On NOP success path, ok exists. Fault test fails on NOP? NOP spin on good dir succeeds and writes ok. Fault test uses bad dir - NOP should reject missing END. If broken walk ignores missing END, fault test fails (exit 0). Good NOP fail.

Success ok: skip as scenery.

Remove test_fxv07_seal as presence-on-success. Keep fault: ok must be absent.

Let me also not write spin.ok on NOP success... instruction says success writes it. NOP still writes it. Can't fail a "ok exists after good spin" test.

OK.

Revised tests (13):
1. hdr ELF - always true on prebuilt ELF! **NOP-PASS if we only check ELF**

GAMEABLE-NATIVE: ELF after rebuild. On NOP the binary is still ELF. **ELF-only test passes on NOP.** Checker lessons: ELF on prebuilt is scenery if instruction requires native... they still want ELF assert but it PASSES on NOP.

pinweld test_pws01 combines ELF AND salvage mark landing. Combine ELF with a behavior that fails NOP.

test_fxv01_hdr: ELF and twin bytes in one test? Split: every test that runs spin also checks ELF once in test_fxv01 that also checks twin.

test_fxv01: ELF + two-process identity (fails NOP on stamp)

2. twin - duplicate of 1, skip
Keep 01 as ELF+twin.

I'll define final 12 tests in construction_manifest after writing.

A bag: test_fxv05_hold, test_fxv09_hits (holdout counts if bag splits dupes), test_fxv12_peer
B walk: test_fxv03_pair, test_fxv06_tail, test_fxv10_child
C pour: test_fxv01_hdr, test_fxv02_twin, test_fxv04_ord, test_fxv08_mint, test_fxv11_hush

That's 3+3+5=11. Add test_fxv13_stay ELF+behavior already in 01.

test_fxv07: fault ok absent - walk
B gets 4 tests, C 5, A 3. Union 12. C=5/12=0.42.

hits: if bag double-interns, counts still right. Make holdout have names that HASH-ORDER intern vs sort changes id mapping and we check differ hush between two holdouts - that's 05.

I'll update spec flipping lists to match final tests.

Continue writing files; I'll fix spec flipping after tests exist.

Writing C code now.