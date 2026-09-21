Invent ONE hard unique task idea in this JSON format for PRIMARY_CATEGORY `build-and-dependency-management`, then convert that JSON into one complete submission-ready Terminus 2.0 task end to end. Do not stop at ideation.

PRIMARY_CATEGORY: build-and-dependency-management
Set JSON `domain` to `build-and-dependency-management`. Honest category must stay
build-and-dependency-management.

Required idea JSON fields:
`id`, `title`, `domain`, `premise`, `symptom`, `defect`, `trap`, `why_hard`, `difficulty_summary`, `graded_on`, `capability`, `capability_name`

Follow `prompts/oneshot_unique_task.md` exactly (occupancy inventory → 3 candidates →
instruction probe vs tasks+specs → spec → files → gates). Never invent a similarity
percentage.

JSON field split:
- Public: `title`, `premise`, `symptom`, `graded_on`
- Author-only (never in solver-visible files): `defect`, `trap`, `why_hard`, `difficulty_summary`

Final chat report: idea JSON, category proof, pasted uniqueness stdout, 5 unique
properties, 7 acceptance checks + how `trap` was blocked, gates, ready only if
`approve_task.py` exited 0.
