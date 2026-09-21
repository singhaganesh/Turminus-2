### Decision
GO — Attempt 1. Constrained video census: naive line-occupancy edge passes the worked sample and fails overlap, dwell, retreat, and busy held-out reels.

### Metadata
- version: 2
- Task name: fordwick-tally
- Title: Distinct downward scan crossings
- Category: video-processing
- Task shape: constrained_build
- Languages: ["python"]
- Difficulty: hard
- Codebase size: small
- Subcategories: []
- Tags: ["python", "opencv", "video", "tracking", "toml"]
- Milestones: 0

## Authoring Brief

### Public contract
- CLI named in `/app/slipfold/SPAN.txt` is `python3 /app/varnish/mill.pyc CLIP` and writes `/app/inkwell/sheet.toml` with integer `crossings`.
- Distinct bodies whose centroid passes `y = 70` top-to-bottom. 160x120 at 12 fps.
- Worked sample `/app/shown.mp4` reports `crossings = 3`.
- Exact match when true count <= 5; inclusive +/- 1 when true count >= 6.
- Hand-written sheet insufficient. Verifier reruns the CLI from SPAN notes.
- Unreadable CLIP exits non-zero and does not write `/app/inkwell/sheet.toml`.
- Python with cv2, numpy, toml only.

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
  role: offline image
- path: construction_manifest.json
  role: local authoring artifact

### task_files
- path: environment/blot.py
  role: shipped occupancy blot
- path: environment/tether.py
  role: shipped occupancy tether
- path: environment/spout.py
  role: shipped occupancy spout
- path: environment/spanwell.py
  role: shipped occupancy driver
- path: environment/kiln/bake.sh
  role: mill fold script
- path: environment/kiln/KILN.txt
  role: kiln card
- path: environment/slipfold/SPAN.txt
  role: station geometry notes
- path: environment/wickpit/touchcue.py
  role: decoy occupancy helper
- path: environment/wickpit/shiftlog.txt
  role: ops leftover
- path: environment/hopcard/millcard.txt
  role: desk leftover

### fix_frontier
- count: 3
- distribution: driver census script, decoy occupancy helper left in place, geometry notes unread as answers
- naming_policy: opaque helper symbols; public CLI path stays in SPAN notes
- forbidden_stems: crossings, centroid, scan, bodies
- helpers_policy: touchcue is decoy; oracle replaces blot/tether/spout and folds the mill
- symbol_thin_preferred: true

### contract_surface
- boolean_fields_max: 0
- direct_boolean_assertions_max: 0
- preferred_assertion_styles: integer tolerance bands, process exit status, regenerated toml
- forbidden_assertion_styles: byte-exact media, boolean answer keys

### task_shape
- type: constrained_build
- instruction_framing: constraint-complete
- hardness_source: design search
- collapse_risk: occupancy-edge or hardcoded sample 3

### category_profile
- challenge_family: identity_preserving_media_census
- profile_name: floating_point_numeric_policy
- allowed_instruction_disclosures: CLI, paths, geometry, sample count, tolerance bands, allowed libraries
- forbidden_instruction_leaks: tracking recipe, held-out reel plots, occupancy-edge trap name
- category_specific_hardness_bar: naive occupancy fails held-out reels while sample stays green
- category_specific_verifier_risks: byte-exact mp4, unstated tolerance, grading only the sample
- coverage_role: first video-processing identity-across-occlusion task

### difficulty_mechanism_plan
- mechanisms: deceptive_but_valid_local_evidence, buried_local_constraints, stateful_multi_step_dependencies, partial_observability_experiment_design
- adversarial_layers_count: 4
- fairness_guardrails: public geometry and tolerance; held-out reels only at grade time
- mechanism: deceptive_but_valid_local_evidence
  placement: wickpit/touchcue.py occupancy helper
  why_model_misses_it: matches the sample
  fairness_guardrail: rubric negative names the helper
- mechanism: buried_local_constraints
  placement: directional centroid rule plus once-per-body
  why_model_misses_it: contact counting looks like the spec
  fairness_guardrail: instruction states once-per-body and direction
- mechanism: stateful_multi_step_dependencies
  placement: identity must survive merge and dwell
  why_model_misses_it: per-frame blobs look sufficient
  fairness_guardrail: sample does not require that coupling
- mechanism: partial_observability_experiment_design
  placement: held-out reels in verifier fixtures
  why_model_misses_it: tuning to the sample
  fairness_guardrail: same size and fps disclosed

### calibration_plan
- oracle_runs: 3
- no_op_runs: 3
- target_agent_runs: 5
- comparator_agent_runs: 5
- human_sanity: expert writes a tracker and hits the bands
- shortcut_audit: hardcoded 3, occupancy-edge, output stuffing
- ablation_plan: drop identity, drop direction, drop segmentation
- pass_rate_target: hard_max_pct=20, too_easy_threshold_pct=80, basis=Claude Opus 5 and GPT-5.6

### verifier_scoring_plan
- metrics: functional_correctness=0.45, hidden_invariants=0.25, state_hygiene=0.15, interface_correctness=0.10, deliverable_completeness=0.05
- overall_threshold: 0.999
- reward_output: reward.txt
- binary_threshold_rule: every graded test passes including held-out tolerance bands

### subtype_milestone_plan
- subcategories: []
- milestone_count: 0
- sequential_dependency: none
- local_only_data: true
- sidecar_or_protocol_notes: clips bundled; no network media fetch

### satisfiability_risk
- rc2_planned_name_risk: low public CLI names only
- gx9_contract_risk: low integer field plus stated bands
- cr1_symbol_frontier_risk: low oracle replaces one driver
- hidden_contract_risk: low; extra reels share disclosed geometry

### actionability_plan
- verifier_command_visible: python3 /app/varnish/mill.pyc as named in SPAN notes
- source_fix_intent_visible: Correct the video pipeline modules under /app
- generated_output_rule_visible: verifier reruns the CLI; hand-written toml insufficient
- exact_formula_home: instruction tolerance bands and y = 70
- schema_home: instruction crossings integer

### waiver_plan
- waivers_expected: no
- waiver_rationale: none expected

### reference_pattern
- justification_if_none: no promoted reference for held-out video identity census; corpus video-processing is calibration only

### realism_source
- source_type: real_system
- evidence_basis: fixed-camera line census used in traffic and belt counting
- upstream_or_synthetic_rationale: synthetic reels keep deterministic ground truth
- minimization_preserves: merge, dwell, retreat, direction
- synthetic_exception_review: not required for real_system

### Failure topology
A first-pass occupancy edge on the scan matches the spaced sample. Overlapping similar bodies collapse to one blob. A body that sits on the scan or backs up then finishes still has one identity. Direction rejects bottom-to-top motion. Busy reels use the +/- 1 band.

### Environment shape
Driver stub, worked mp4, station notes, decoy occupancy helper, desk leftovers, vendored wheels for offline cv2/numpy.

### Required artifacts
instruction, tests, Dockerfile with verifier pytest off PATH, solve.sh, task.toml allow_internet false, example reel, decoy helper.

### Test plan
- test_fdw01_schema_key: sheet crossings integer
- test_fdw02_known_loop: example exact 3
- test_fdw03_twin_pass: overlap truth 2
- test_fdw04_sit_once: halt truth 2
- test_fdw05_back_once: recede truth 1
- test_fdw06_wide_slack: crowd 7 within 1
- test_fdw07_rise_skip: climb 0
- test_fdw08_poison_rerun: corrupt then rerun
- test_fdw09_absent_path: missing clip nonzero
- test_fdw10_static_reject: stuffed toml loses to rerun
- test_fdw11_twice_same: two runs agree
- test_fdw12_shade_blob: overlap still 2 under shadow

### Drafting guardrails
Do not name MOG2, IoU, Kalman, pause, occlusion, or held-out plots in solver-visible text.

### Triviality Ledger
- Occupancy-edge passes the sample and fails merge/retreat.
- Hardcoded 3 fails every non-sample reel.
- Stuffing output.toml loses because tests rerun the CLI.

### Per-gate Pitfall Inventory
- RC2: no broken_* names; public paths only.
- GX9: integer plus stated inclusive bands, never byte-exact mp4.
- RC3: held-out counts, not schema-only.
- RC7: oracle tracker well above 30 LOC.
- GX6: no algorithm recipe.

### Initial Draft Commitments
- environment/Dockerfile
- environment/.dockerignore
- environment/spanwell.py
- environment/shown.mp4
- environment/slipfold/SPAN.txt
- environment/wickpit/touchcue.py
- environment/wickpit/shiftlog.txt
- environment/hopcard/millcard.txt
- environment/wheelurn/wheels/
- environment/wheelurn/parts/
- environment/wheelurn/debs/
- instruction.md
- task.toml
- output_contract.toml
- tests/test.sh
- tests/test_outputs.py
- tests/reels/
- solution/solve.sh
- solution/spanwell.py
- rubric.txt
- construction_manifest.json

### Construction manifest (BLOCKING — Step 2b must follow this verbatim)

#### symbol_table
- path: environment/spanwell.py
  symbol: emit_span
  kind: function
  signature: emit_span(src: str) -> int
  purpose: run census on a reel path
- path: environment/spanwell.py
  symbol: knit_marks
  kind: function
  signature: knit_marks(pts: list) -> list
  purpose: bind detections across time
- path: environment/spanwell.py
  symbol: fold_gate
  kind: function
  signature: fold_gate(tr: list) -> int
  purpose: score downward passages

#### flipping_point_contract
locations:
  - id: A
    path: environment/spanwell.py
    controls_tests: [test_fdw01_schema_key, test_fdw02_known_loop, test_fdw03_twin_pass, test_fdw04_sit_once, test_fdw05_back_once, test_fdw08_poison_rerun]
  - id: B
    path: environment/wickpit/touchcue.py
    controls_tests: [test_fdw06_wide_slack, test_fdw07_rise_skip, test_fdw09_absent_path, test_fdw10_static_reject, test_fdw11_twice_same, test_fdw12_shade_blob]
  - id: C
    path: environment/slipfold/SPAN.txt
    controls_tests: [test_fdw01_schema_key, test_fdw02_known_loop, test_fdw06_wide_slack, test_fdw07_rise_skip, test_fdw10_static_reject, test_fdw11_twice_same]
no_single_location_flips_majority: true
concentration_cap: 0.5

#### decoy_manifest
- path: environment/wickpit/touchcue.py
  kind: helper
  rhymes_with: emit_span
  non_fix_purpose: occupancy-edge count that matches the sample

#### code_forbidden_tokens
code_forbidden_tokens: [census, crossings, bodies, centroid, scan, recording, sample, station, pipeline, implementation, verifier, integer, motion, horizontal, distinct, tolerance, frames, pixels, video, clip]
