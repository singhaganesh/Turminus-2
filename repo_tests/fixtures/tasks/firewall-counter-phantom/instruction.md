The observability governor under `/app` has drifted: profile agreement flags, metric/span count parity, and slot sampling no longer line up. Problems cut across refresh binding, profile handle resolution, C-side slot deny totals, and the packaged JSON slot probe—not one isolated module. Treat this as a debugging task: fix the code, rebuild, and confirm both `/app/bin/phase_eval truth` and `/app/bin/metrics_probe` before you publish results.

Write `/app/output/report.json` with exactly four boolean keys `agree_alpha`, `agree_beta`, `counts_ok_alpha`, and `counts_ok_beta`, each set to `true`. A green `phase_eval truth` alone is not enough; slot sampling must match the library before the report counts.

Run `/app/bin/metrics_probe --json <a> <b>`. Swapping the two numeric inputs must swap the returned counts. With the default pair `0` then `1`, both counts must be strictly positive and the first must be larger than the second.
