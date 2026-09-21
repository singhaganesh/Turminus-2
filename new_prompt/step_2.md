# Step 2: Validate Idea and Produce Specs

Validate this task idea and produce:

* one authoring spec
* one reviewer appendix

Do NOT create any task files under `tasks/`.

You will operate inside an automated validation loop managed by `validate_loop.py`. The script is the source of truth for loop state, attempt tracking, persistence rules, and next actions.

Follow these references strictly:

* `@idea-validation.mdc` → all hardness checks, anti-trivialization checks, rubric axes, spec format, and reviewer expectations
* `@difficulty-calibration.mdc` Part A → collapse audit requirements
* `specs/validation_schema.json` → mandatory evidence schema and field contract

Never skip required fields, compress reasoning into placeholders, or summarize mandatory evaluations.

---

# Core Objective

Your job is NOT to defend the idea.
Your job is to aggressively attempt to disprove hardness, discover shortcut paths, identify collapse risks, and verify whether the task genuinely forces deep engagement with the codebase.

Assume reviewers are actively searching for:

* hidden one-function exploit paths
* instruction leakage
* topology collapse
* naming leakage
* concentrated test ownership
* fake multi-file complexity
* decoy modules that are too obvious
* patches solvable from instructions alone

A task only passes if it survives hostile scrutiny.

---

# Operating Rules

1. Treat every WARN as a real weakness unless proven otherwise.
2. Never mark PASS without explicit reasoning.
3. Never reuse previous reasoning verbatim across attempts.
4. If a weakness is fixed in later attempts, explicitly identify:

   * the structural change
   * why it improved the result
5. Do not hide uncertainty.
6. If the task collapses to a localized patch, fail it.
7. If instructions reveal the fix path, fail it.
8. If fewer than 3 meaningful fix topologies exist, fail it.
9. If one location dominates test ownership, fail it.
10. Do not optimize for approval. Optimize for correctness.

---

# Step 0 — Initialize

Run:

```bash
python validate_loop.py init <task-name>
```

Read the `ACTION` line from the output.

---

# Main Validation Loop

Repeat until `ACTION` becomes `GO` or `STOP`.

---

## ACTION: CONTINUE

Perform ALL sections below in order.

---

## 1. Hardness Axis Evaluation

Evaluate all 5 hardness axes from `@idea-validation.mdc`:

1. Discover
2. Synthesize
3. Diagnose
4. Navigate Coupling
5. Reason Beyond Training

For EACH axis:

* write 1–2 concrete sentences
* explain why the task genuinely satisfies the axis
* reference actual structural properties of the task
* avoid generic statements

If ANY axis fails:

* mark the task as FAIL
* explicitly state why the task is not hard enough

Do not aggregate results.
Evaluate each axis independently.

---

## 2. Instruction Completeness Test

Run this test exactly:

> “Can the agent solve this task by reading ONLY `instruction.md` without deeply engaging with the repository?”

If the honest answer is YES:

* mark FAIL
* explain precisely what information leaks the solution path

You must assume a strong agent looking for shortcuts.

---

## 3. Anti-Trivialization Audit

Run ALL 20 anti-trivialization checks from `@idea-validation.mdc`.

For EACH check:

1. write reasoning FIRST
2. then produce verdict:

   * PASS
   * WARN
   * FAIL

Never emit verdicts without justification.
Never collapse multiple checks together.

The reasoning should explain:

* how a solver might exploit the task
* whether the current design prevents that exploit
* what still remains risky

---

## 4. Rubric Axis Evaluation

Evaluate all 6 rubric axes individually.

For EACH axis:

* give exactly 1 concise reasoning sentence
* provide a verdict:

  * PASS
  * WARN
  * FAIL

Do NOT summarize as “all pass.”

---

## 5. Collapse Audit

Run the full collapse audit template from:

`@difficulty-calibration.mdc` Part A

Do not abbreviate sections.
Do not skip editable-frontier analysis.

You are specifically looking for:

* one-function repair paths
* hidden root causes
* fake topology distribution
* instruction leakage
* concentrated ownership
* brittle decoys

If the oracle patch is dramatically simpler than intended solver effort, explain why.

---

## 6. Attempt Delta Analysis (Attempt 2+ Only)

For every previously WARN/FAIL item that is now PASS:

* identify the exact design modification
* explain why it fixed the issue

Bad example:

* “improved topology”

Good example:

* “moved lifecycle accounting into a second module with independent seeded corruption and redistributed verifier ownership across 3 test clusters”

Do not merely restate improved reasoning.
Name the structural change.

---

## 7. Scope Integrity Check

If ANYTHING changed beyond direct weakness remediation, explicitly list:

* language changes
* architecture changes
* module changes
* scope expansion/reduction
* domain shifts
* topology redistribution
* test redistribution

For each:

* explain why the change was necessary
* explain why the task still preserves the original intent

---

# 8. Naming Pass + Token Provenance Audit

Run this BEFORE constructing evidence JSON.

---

## 8a. Instruction-Noun Extraction

Draft symptoms-only instruction prose.

Extract EVERY noun.

The exact extracted noun list must populate BOTH:

* `naming_pass.instruction_nouns_extracted`
* `construction_manifest.code_forbidden_tokens`

Do NOT derive these separately.
The lists must match exactly.

---

## 8b. Leakage Scan + Renaming

Scan ALL of the following:

* `construction_manifest.symbol_table`
* `flipping_point_contract.locations`
* `decoy_manifest`
* all planned test names

If ANY extracted noun appears as a case-insensitive substring:

* rename the symbol/path/test
* record:

  * original name
  * renamed name
  * reason

Store every rename under:

```json
naming_pass.renames_during_drafting
```

If no renames were needed:

* leave the list empty
* do NOT fabricate renames

---

## 8c. Concentration Math

Compute:

```text
Total tests = union size of all controls_tests
```

For EACH flipping-point location:

* compute test_count
* compute ratio = test_count / total_tests

Populate:

```json
naming_pass.concentration_math
```

Numbers must be exact.
The validator will recompute them.

---

## 8d. Decoy Validation

Every entry in `decoy_manifest` MUST include:

```json
rhymes_with
```

This field must reference a real fix-path symbol.

Missing or empty rhyme references are schema failures.

---

# 9. Evidence JSON Construction

Construct a fully compliant evidence JSON matching:

```text
specs/validation_schema.json
```

Populate ALL required fields.
No placeholders.
No omitted sections.

---

## Required Blocking Sections

The following are mandatory and blocking.

### Hardness

* `hardness_axes`

### Trivialization

* `anti_trivialization_checks`

  * must contain 21 entries
  * includes `topology_distribution_test`

### Discovery

* `discovery_budget`

  * minimum 3 non-trivial discoveries
  * each discovery must include:

    * discovery name
    * intended repository location
    * why instructions must NOT reveal it

If you cannot produce 3 meaningful discoveries:

* the task is easy
* fail it

### Instruction Leakage

* `instruction_specificity`

Hard tasks MUST use:

```json
"level": "symptoms-only"
```

If the honest level is:

* `spec-complete`
* `cause-revealing`

then the task is not hard enough.

### Attack Path

* `attack_path`

### Minimal Repair Risk

* `smallest_plausible_patch`

### Topology Enumeration

Must contain AT LEAST 3 distinct fix topologies.

Each topology must:

* reference at least 3 coordinated locations
* explain why no single location can solve the task

If you cannot articulate 3 legitimate topologies:

* reject the task
* it has a one-function exploit locus

### Construction Manifest

Must include:

* `symbol_table`

  * at least 3 opaque fix-path symbols
* `flipping_point_contract`

  * at least 3 locations
  * must span distinct roots
  * test concentration must remain under 50%
* `decoy_manifest`

  * at least 2 rhyming helper modules
* `code_forbidden_tokens`

  * must exactly match extracted instruction nouns

### Naming Audit

Must include:

* `instruction_nouns_extracted`
* `renames_during_drafting`
* `test_names_audited`

  * minimum 3
* `concentration_math`

---

# 10. Verdict Accounting

Count all WARN and FAIL results.

Your counts must align with:

* evidence JSON
* written review
* rubric verdicts
* anti-trivialization verdicts

No contradictions allowed.

---

# 11. Produce Review Documents

Create:

1. Authoring Spec
2. Reviewer Appendix

Use the exact format required by `@idea-validation.mdc`.

Both documents MUST include:

```text
Decision: <STATUS> — Attempt <N>
```

Examples:

* `Decision: GO — Attempt 2`
* `Decision: CONTINUE — Attempt 4`

Do NOT save the files yet.
Hold them in memory until the script determines persistence behavior.

---

# 12. Save Temporary Evidence

Save evidence JSON to a temporary path.

Example:

```bash
/tmp/<task-name>-validation-evidence.json
```

---

# 13. Record Attempt

Run:

```bash
python validate_loop.py record <task-name> --evidence /tmp/<task-name>-validation-evidence.json
```

This determines:

* persistence behavior
* overwrite rules
* candidate handling
* whether the attempt is accepted

Never save specs before this step.

---

# 14. Save Specs

Read:

* `SAVE_TO`
* `REVIEWER_SAVE_TO`

from script output.

Then:

* save authoring spec to `SAVE_TO`
* save reviewer appendix to `REVIEWER_SAVE_TO`

Rules:

* each file must contain ONLY the current variant
* no comparison tables
* no historical notes
* no discarded attempts

If `SAVE_TO=DISCARD`:

* save nothing
* do not override previous outputs

The script controls persistence authority.

---

# 15. Strict Finalize Gate

After saving BOTH files on a GO attempt:

Run:

```bash
python validate_loop.py finalize <task-name>
```

If finalize fails:

* read every failure carefully
* patch saved specs in place
* rerun finalize

Do NOT rerun `record`.
Evidence has not changed.
Only the spec formatting/contract changed.

Common required fixes include:

* missing `version: 2`
* missing mandatory subsections
* malformed contract sections

Continue until finalize exits successfully.

---

# 16. Post-Attempt Routing

Read the new ACTION.

---

## ACTION: CONTINUE

List ALL current WARNs and FAILs.

For EACH:

* propose a concrete structural fix
* avoid vague remediation language

Bad:

* “increase complexity”

Good:

* “split verifier ownership across async reconciliation and allocator accounting paths with independent seeded corruption”

Apply ALL changes.
Then restart loop from Step 1.

---

## ACTION: SELECT

The validator reached a scoring plateau.

Read the `CANDIDATES` line.
Each candidate includes:

* attempt number
* authoring spec path
* reviewer appendix path

For EACH candidate:

1. run collapse audit
2. summarize:

   * collapse verdict
   * oracle complexity
   * editable frontier size
   * residual hardness

Then choose the strongest candidate.

Selection criteria:

* strongest resistance to shortcut solving
* most believable multi-location coordination
* best topology distribution
* lowest instruction leakage
* strongest reviewer confidence

Then run:

```bash
python validate_loop.py select <task-name> --winner <attempt-or-path>
```

Examples:

```bash
python validate_loop.py select <task-name> --winner 3
```

```bash
python validate_loop.py select <task-name> --winner specs/foo-candidate-2.md
```

---

# ACTION: GO or STOP

Report:

* Final decision
* Winning attempt number (if GO)
* Stopping reason
* Final FAIL count
* Final WARN count
* Final authoring spec path
* Final reviewer appendix path

If STOP:

* explain why the task family is fundamentally unsalvageable
* identify which structural weaknesses could not be repaired

---

# Final Quality Standard

A valid GO candidate should:

* force genuine repository exploration
* require coordinated reasoning across multiple roots
* resist one-function patching
* resist instruction-only solving
* contain meaningful discovery work
* survive collapse audit scrutiny
* maintain topology distribution
* avoid naming leakage
* avoid concentrated verifier ownership
* remain difficult even for strong agents

If the task can realistically be solved through:

* keyword matching
* obvious symbol tracing
* localized patching
* instruction leakage
* verifier concentration
* superficial repo scanning

then it is not hard enough and must not GO.


Here is the task idea:

