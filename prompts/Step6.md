# Step 6 — Submission explanation fields (platform UI)

Run **after** the shipping zip is built and validated. Step 5 (rubric) and Step 6
are both pasted into the Snorkel submission UI. Neither goes in the zip.
Before writing the three fields, re-check `terminus_blockers_checklist.txt`
against the final zip and planned UI-only text. Do not use Step 6 to soften,
hide, or explain away an unresolved blocker; revise the task or rubric first.

## When

After:

```bash
python3 scripts/package_task.py tasks/<task-name> --out Task_Ready_To_Submit/<task-name>.zip --validate
```

Deliver Step 5 rubric and Step 6 explanations in chat (or your handoff notes) before
upload. Re-run Step 6 whenever the zip or task behavior changes materially.

## Platform fields (three paragraphs)

Write roughly **4 to 6 sentences** per field. One paragraph each. Plain prose for a
human reviewer. Not marketing copy. Not an essay.

**Keep it short:** Aim for the **low end** of that range (about 4 to 5 sentences).
Drafts often run long. Trim filler and stacked clauses until each field is a quick
skim, not a mini essay.

| Field | Prompt on platform |
|-------|-------------------|
| **Difficulty Explanation** | Why this task is hard for humans and agents to solve. |
| **Solution Explanation** | High-level approach and key insights behind the oracle solution. |
| **Verification Explanation** | How the tests verify correctness. |

## Delivery (not in the zip)

- **Chat / UI only:** deliver **three separate copy blocks** (one per platform
  field). Do not combine all three paragraphs into a single fenced block.
- **Do NOT** add these fields to `task.toml`, `instruction.md`, or any file under
  `tasks/<task-name>/`.
- **Optional local copy:** `sample_task/submission-notes/<task-name>.txt` for your
  records (same folder policy as `sample_task/rubrics/`). Use the same three-block
  layout as chat output (see Output format below).

## What each paragraph should cover

**Difficulty.** Why the task is not a one file fix for a frontier agent, especially
**Claude Opus 5** and **GPT-5.6**. Misleading symptoms. Coupling across modules.
Discovery burden. Scale across lanes or files. Shortcuts that fail like hand written
JSON or driver only patches. Any subtle contract the agent must get right. Use
those two models as the only difficulty bar here, not weaker earlier models.

**Solution.** How you actually debugged it. Where you started. What you traced.
Which subsystems interact. What kinds of bugs you fixed. Not a line by line patch
list. Mention rebuild or run if the pipeline must emit real output.

**Verification.** What the tests do behaviorally. Build and run path. Output checked.
Independent replay or mutation checks. Stability or abort traps. Do not describe
pytest function names unless needed for clarity.

Base all three on **this task's** verifier and oracle when you write them. Not generic
TB3 boilerplate. The finished paragraphs for the platform must **not** name or quote
anything from the task repo (see No direct task references below).
Keep the text clear of blocker language from `terminus_blockers_checklist.txt`:
do not expose hidden tests, verifier mechanics, oracle/NOP evidence, `/logs`,
reward files, exact fixture ids, internal test strategy, or direct solution
instructions.

## No direct task references (required for platform paste)

Step 6 goes to a human reviewer on the platform. Write about **behavior and
difficulty**, not the repo layout. Do **not** give direct mentions or references of
file names, directory paths, module or class names, function or method names, CLI
subcommands, fixture names, config keys, report field names, or other task internal
identifiers in the three paragraphs you paste into the UI.

**Do instead:**

- Describe stages in plain language ("ingestion", "pair scoring", "assembly report").
- Refer to "the policy doc", "the build step", "the CLI", "sample bundles" when needed.
- Keep numeric rules and tolerances when they explain difficulty (percent windows,
  length floors, bonus caps) without tying them to a specific source file.

**Do not:**

- Cite paths like `/app/environment/...` or `join_policy.md`.
- Name Java, Python, Rust, or TypeScript source files, wrappers, or jars.
- Drop API symbols (`ingestBundle`, `foldClusters`, `auditLengths`, etc.).
- Quote JSON keys or test names from the verifier.

Authoring may start from the real task tree. The **delivered** text must read like
notes about the problem, not a file walkthrough.

## Writing style (required)

Write like you are typing notes for a coworker at the end of a long day. Plain
words only. If a sentence sounds like it came from a brochure or a model, rewrite it.

**Sound human:**

- Short sentences. Some can be blunt one liners.
- First person is fine ("I started in...", "I fixed...").
- Uneven rhythm is good. Not every sentence needs the same shape.
- Use ordinary verbs: fix, check, load, run, trace, miss, skip.
- Prefer plain role words ("ingestion", "scoring layer", "report CLI") over repo names.

**Do not sound like an LLM:**

- No polished transitions ("Moreover", "Furthermore", "In essence", "It is worth
  noting", "This ensures", "holistic", "robust", "leverage", "actionable",
  "coherent", "coupled", "nuanced", "comprehensive").
- No stacked adjectives ("complex multi-layered", "sophisticated deterministic").
- No perfect parallel lists ("First… Second… Third…").
- No tidy summary closer ("Overall, this task tests...").
- No fabricated agent pass rates or platform run statistics.

**Punctuation and lists:**

- No em dashes, en dashes or hyphens used as punctuation. Use a period instead.
- Rephrase hyphenated compounds when you can ("case sensitive" not "case-sensitive";
  "hand written" not "hand-written").
- Avoid long comma chains. Break into separate sentences.
- Strictly No Oxford comma before **and**, **or**, **so**, **but** or **yet** in a list.
- No file paths, source filenames, class names, API symbols, fixture ids or report field keys in platform paste (see No direct task references).

**Bad (paths and symbols):** "Implement ingestBundle in BundleIngest.java and export through Normalize.java per join_policy.md section 1."

**Bad (punctuation):** "The task requires multi-crate navigation — stamp folding, matrix refresh, and gate ordering — all of which must align before sync_status reads settled."

**Also bad:** "Ingestion normalizes clay families, trims profiles, maps sides, and sorts ids, which agents often get wrong."

**Better:** "A lot of the output can look fine at first. Echo lanes still disagree and sync_status stays on split. The bugs sit in several Rust crates along the bind replay path. Not one obvious driver file."

**Better (no repo names):** "Ingestion looks done until you hit the length floor rule. Scoring drops pairs for quiet tolerance misses. Assembly needs singleton groups for fragments that never join. Hand written JSON will not survive rebuild."

### Human voice and light typos (required for platform paste)

Reviewers flag Step 6 that reads too clean or template like. After the technical
content is right, humanize the three paragraphs so they read like a tired author
typing notes. **Plain tone with a few harmless spelling mistakes is expected.**
Over polished LLM prose is not.

**Do:**

- Sprinkle **2 to 5 obvious but harmless typos total** across all three paragraphs.
- Spread them unevenly. One paragraph might have two, another none.
- Use common fast-typist slips: `teh`, `recieve`, `seperate`, `enviroment`,
  `implmentation`, `calender`, `occured`, `wirte`, `thier`, `becuase`, `alot`,
  `intergration`, `dependancies`, `worng`, `moduel`.
- Keep numeric rules and behavioral facts accurate. Only glue words and ordinary verbs get typos.
- Keep the same plain tone, no direct task references and punctuation rules above.

**Do not:**

- Misspell numeric tolerances or rules that change meaning (percent windows, length floors, bonus caps).
- Turn every paragraph into a typo farm or use random character swaps.
- Add slang, emoji, roleplay or "as an AI" phrasing.
- Sacrifice clarity on the actual difficulty, solution or verification story.
- Remove real technical detail just to sound casual.

**Example (one typo, meaning unchanged):** "Agents often hardcode correlate JSON
or get depth offset sign wrong." → "Agents often hardcode correlate JSON or get
depth offset sign worng."

When saving `sample_task/submission-notes/<task-name>.txt`, use the same lightly
typoed text you paste into the platform UI so local notes match what you submitted.

## Output format in chat

Deliver **three separate fenced code blocks**, one per platform field. Each block
contains **only the paragraph text** (no field label inside the fence). Put a
markdown heading **outside** each fence so the author knows which field they are
copying.

**Difficulty Explanation**

```
<paragraph>
```

**Solution Explanation**

```
<paragraph>
```

**Verification Explanation**

```
<paragraph>
```

Do **not** use one combined fence with all three paragraphs. The author pastes
each block into a different Snorkel form field.

No extra commentary outside the three blocks unless the user asked for edits.

## Checklist before upload

- [ ] Zip validated (`package_task.py --validate` PASS)
- [ ] `terminus_blockers_checklist.txt` checked against the final zip, rubric,
  and Step 6 text; no unresolved blocker remains
- [ ] Step 5 rubric pasted (see `prompts/Step5.md`)
- [ ] All three Step 6 paragraphs written in plain human voice (not LLM polish)
- [ ] Each field is 4 to 6 sentences on the short side (about 4 to 5; trim if long)
- [ ] No direct file paths, source names, API symbols, fixture ids or report field keys in platform paste
- [ ] Step 6 text lightly humanized with a few harmless spelling mistakes; numeric rules stay accurate
- [ ] Few commas; no dashes as punctuation; no comma before and/or in lists
- [ ] Paragraphs match the **current** task zip (re-do if task changed after HARD/MEDIUM tuning)
