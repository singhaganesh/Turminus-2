# Harden-or-Drop — one shot, any task

You are given ONE already-built Terminus task that a frontier model still solves.
Your job: **diagnose why it is solvable, then either harden it once or declare it
undroppable and tell the user to drop it.** You run once. After you finish, the
user measures; if the model still solves it, they drop it. So do not waste the
shot hardening a task whose cause cannot be hardened.

Global prompt — works on any task. Read the task first, do not assume its domain.

You have NO frontier-model access. Never claim/invent an Opus 5 / GPT-5.6 /
harbor result. Prove everything with the local probes and the local red-team run.

## Information to request

Ask for exactly these two, nothing else:

```
Task summary:
Task path:
```

Then read the whole task: `instruction.md`, `solution/solve.sh` (+ patches),
`tests/`, `environment/` (the files solve.sh touches + the docs it names),
`rubric.txt`, `task.toml`. Restate in one line each: what the agent must work
out, and what the actual defect(s) are.

---

## STEP 1 — Diagnose the cause (decisive; decides harden vs drop)

Classify why the model solves it into exactly one primary cause. This choice
determines everything after.

Apply the **GAP test first** (the single strongest signal):

> Can the tests grade the outcome WITHOUT the instruction stating the fix?
> If the fair, must-be-stated requirement **is** the insight, hardening cannot
> help — stating what you grade states the fix.

| Cause | Signature | Verdict |
|---|---|---|
| **req≡insight** | The graded requirement literally names the fix (e.g. "detect a changed file even when device+inode are unchanged"; "compare the live tree to the newest snapshot"). Removing it makes the task an ambush. | **DROP** — go to Step 4A |
| **thin substrate** | One realisation only (often spread across files = still one). Undergraduate solves the core in an afternoon; symptom greps to the bug. No amount of decoy/held-out adds a second independent insight. | **DROP** — go to Step 4A |
| **spec-implementation / cause-revealing** | Instruction states the algorithm, schema, or the cause ("the CRC uses half the payload"). Pure "translate English to code." | **DROP unless de-leakable** — if the deep structure survives once the recipe is removed, treat as Leaked (Step 3); else Step 4A |
| **leaked (deep idea, telegraphed)** | The substrate is genuinely deep (≥2 independent insights, generator/rebuild/held-out available) but the instruction/docs give the insights away (names the field-order rule, the count guard, the fix location, the mechanism). | **HARDEN** — go to Step 3 |

If two causes apply, the **undroppable** one wins (req≡insight / thin substrate
override leaked). Only a cleanly Leaked cause proceeds to hardening.

State the verdict now, with the quoted evidence. Do not proceed to harden a task
whose primary cause is undroppable.

---

## STEP 2 — Confirm the substrate is worth hardening (only if "Leaked")

Before spending the shot, confirm the deep structure is real. It must have:

1. **≥2 genuinely independent insights** — fixing one does not reveal the others
   (same fix in N files = one insight).
2. **A structural/rebuild/generator lever** — scoring depends on running,
   rebuilding, regenerating, or a held-out/deployed/recovery artifact, not on the
   source text the agent edits.
3. **An unfakeable discriminator available** — a held-out input, a deployed
   artifact made by old code, or a fault/recovery path the agent cannot see or
   fabricate.

If it does not have these, it was not really "leaked" — it is thin substrate.
Reclassify as DROP (Step 4A).

---

## STEP 3 — Harden the leaked task (the one shot)

Difficulty comes from the PROBLEM, not the environment, vocabulary, or volume.
You are removing what was given away and forcing discovery + verification.

1. **Strip the leak, keep the contract.** Remove from `instruction.md` and any
   env doc: the fix location, the mechanism, the per-insight recipe, ordered
   walkthroughs, and any restatement of an insight sitting next to the code that
   implements it. KEEP the graded output contract (schema, formats, fault rules)
   — hiding a graded rule is an ambush. State the operator-visible SYMPTOM and
   the required OUTPUT, never the cause or the fix.

2. **Make the defect survive reading (P1).** Rewrite each broken component so it
   reads as a plausible-correct implementation, not an obvious deviation. The
   agent must run/experiment to locate it, not diff spec-vs-code.

3. **Push discrimination into held-out.** Ensure the visible fixtures do NOT
   exercise every edge; move edge combinations into held-out inputs the verifier
   supplies at grade time. A solution keyed to the visible cases must fail them.
   Grade the OBSERVABLE outcome, never dictate the mechanism.

4. **Keep the levers independent and interacting.** Confirm no single edit
   passes: encode half-fix probes in `preship/preship.json` (R10a/R10b/…), each
   expecting reward 0. Fixing lever A alone must leave the suite failing on B.

5. **Do not add breadth.** More edge cases / assertions / decoys on a shallow
   core do nothing. If you find yourself padding, the cause was thin substrate —
   stop and go to Step 4A.

### Fairness (do not cross)
- Every graded rule stays stated; hide the FIX, never the requirement.
- No new randomness/timing/network. Keep the language. Oracle derives the fix +
  rebuild; no hardcoded outputs, no copying held-out answers.
- Native-binary tasks: the suite must still assert ELF on the rebuilt binary
  (`native_binary_check.py` stays PASS).

### Prove it (run; quote real output)
```
python3 scripts/difficulty_floor_check.py tasks/<slug>
python3 scripts/caveat_audit_check.py tasks/<slug>
python3 scripts/native_binary_check.py tasks/<slug>
python3 scripts/preship_probes.py tasks/<slug> --strict
python3 scripts/oracle_idempotency_probe.py tasks/<slug> --strict
python3 scripts/harbor_gate.py tasks/<slug> --oracle --nop
./scripts/check-task.sh --strict tasks/<slug>
python3 scripts/package_task.py tasks/<slug> --out Task_Ready_To_Submit/<slug>.zip --validate
```
Pass: floor ≥2 classes; native PASS (if applicable); R5/R6/R7/R10 all reward 0;
NOP 0, oracle 1, idempotent; held-out shortcut fails; instruction no longer
contains the fix/mechanism but still states the contract.

### Local red-team (no API key)
In a throwaway built container, prompt an agent: *"read only the instruction and
environment; name the exact fix without running anything."* If it can name every
defect from the docs alone, the leak remains — tighten. Success = it knows the
required OUTPUT but must run/experiment to find the CAUSES.

---

## STEP 4 — Output

### 4A · DROP verdict (undroppable cause)
State plainly: **DROP.** Give the cause (req≡insight / thin substrate /
non-de-leakable spec-implementation), the quoted evidence, and one sentence on
why hardening cannot help (e.g. "the requirement 'X' is the fix; removing it is
an ambush"). Do not edit the task. Do not attempt a partial harden.

### 4B · HARDEN report (leaked cause)
1. Cause = leaked; the deep structure (Step 2) that justified hardening.
2. What was stripped from instruction/docs (before → after).
3. P1: how each defect was made to survive reading.
4. Held-out discrimination added; visible-only solution now fails.
5. Probe evidence (floor, native, R5/R6/R7/R10, NOP/oracle/idempotency).
6. Red-team result.
7. Files changed.
8. One line: **"Hardened once. If the model still solves it after measurement,
   drop it — the shot is spent."**

---

## Guardrails
- One shot. Diagnose before hardening; never harden an undroppable cause.
- Hardness = idea ceiling; execution only loses it. If the ceiling is medium
  (req≡insight / thin), no execution move reaches hard — say drop.
- Never claim a probe, red-team, or frontier result you did not run.
- Never claim measured difficulty — the platform measures; you predict.
