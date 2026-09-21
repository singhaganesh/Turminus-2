This is a Rust source-level repair task in /app. The replay and compaction flow can look healthy on an early pass and then regress after later replay/reload activity. Repair the existing implementation so each fixture scenario under /app/fixtures/scenarios stays coherent across the full schedule, then write the result to /app/output/report.json.

The report keeps a top-level scenarios array with one row per fixture. Each row includes scenario_id, ok, fingerprint, counts, and notes. fingerprint is lowercase hex with length 16. counts includes only items, tombstones, and gen_max, and those values are non-negative integers. notes is a semicolon-separated observation string that records check= and reload= entries when those observations occur.

Make the report reflect end-to-end behavior rather than transient snapshots: replay/reload should settle within each scenario, first comparable check/reload observations should agree, and two runs over identical inputs must produce identical report content.

Use these two rules together:
- Behavior rule: in compaction-heavy schedules, a compaction boundary may introduce one transition in reload fingerprints, and later replay/reload observations should converge.
- ok rule: any differing reload observations in a row still count as drift for ok, across the full scenario timeline including compaction boundaries. Example: reload sequence x,x,y,y is drift-present, so ok must be false.

beta, delta, and gamma must finish with positive gen_max, and fingerprint must match the row's final reload observation.
