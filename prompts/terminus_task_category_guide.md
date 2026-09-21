REPO POLICY BANNER (TERMINAL-MAIN)
======================================================================
Every Terminus primary category is OPEN for new tasks and for edits/revisions.
Use this file as an honest classifier: assign the category that matches the
dominant start state, reasoning, and verifier proof. Do not relabel work to
avoid a category. The full set is:

- debugging
- software-engineering
- data-processing
- system-administration
- build-and-dependency-management
- games
- machine-learning
- security
- scientific-computing
- video-processing

`video-processing`: primary evaluated outcome is a verified frame, stream,
codec, timing, or processed-video result (transcoding, frame transforms, frame
extraction, media pipelines). Do NOT use when video is only an input to an
otherwise ML/OCR/analysis task — that routes to `machine-learning` /
`file-operations` (e.g. the corpus's `extract-moves-from-video`, which is
`file-operations` because the real work is OCR/transcription). Video-processing
tasks are `constrained_build` shape: state the full spec + the grading
TOLERANCE (byte-exact media output is a false failure), grade on a held-out test
video, keep `allow_internet = false` with fixtures bundled locally.

Empirical difficulty is judged on **Claude Opus 5** and **GPT-5.6**. Design so
those two models, not weaker earlier ones, land HARD (preferred) or at worst
MEDIUM. See `.cursor/rules/difficulty-calibration.mdc` Part E.

See `.cursor/rules/submission-category-blocklist.mdc` for the same classifier
(no category is blocked).

HOW TO CLASSIFY A TERMINUS TASK AS DEBUGGING, SOFTWARE ENGINEERING, OR DATA PROCESSING

The current Terminus-2.0 format expects exactly one primary category in task.toml. The category should describe the task's dominant activity. A task may contain elements from several areas, but you should not assign multiple primary categories. Separate subcategories such as api_integration, db_interaction, tool_specific, long_context, and ui_building may be added independently.

For example, a broken ETL pipeline involves both data and code, but:

- If the main challenge is discovering why it is broken, use debugging.
- If the main challenge is adding a new pipeline capability, use software-engineering.
- If the main challenge is transforming supplied files into required outputs, use data-processing.


THE SIMPLEST CLASSIFICATION RULE

Ask these three questions:

1. What state does the agent start with?
   - Broken system -> probably debugging.
   - Incomplete or missing functionality -> probably software engineering.
   - Raw or messy input data -> probably data processing.

2. What consumes most of the reasoning?
   - Diagnosing an unknown cause -> debugging.
   - Designing and implementing functionality -> software engineering.
   - Understanding and transforming data -> data processing.

3. What does the verifier mainly prove?
   - A defect has been correctly repaired -> debugging.
   - A software capability has been implemented -> software engineering.
   - A derived dataset, report, or converted artifact is correct -> data processing.


======================================================================
1. DEBUGGING TASKS
======================================================================

OFFICIAL MEANING

A debugging task primarily requires the agent to identify, diagnose, and fix errors in scripts, codebases, or system configurations. Typical examples include repairing a memory leak, diagnosing a production crash, and fixing a failing test suite.


WHEN A TASK SHOULD BE CLASSIFIED AS DEBUGGING

Use:

category = "debugging"

when the central challenge is:

"Something is wrong, but the agent must determine what is causing it and repair it."

The important part is not merely that code changes are needed. The important part is that the agent must perform root-cause analysis.

A proper debugging task normally starts with one or more observable symptoms:

- failing tests
- incorrect output
- crash or exception
- deadlock
- resource leak
- corrupted state
- intermittent failure
- inconsistent behavior
- degraded performance
- invalid configuration behavior

The task should not directly tell the agent which line or function is broken. If the prompt says exactly what to change, most of the diagnostic challenge disappears.


COMMON WAYS TO CREATE DEBUGGING TASKS

A. LOGIC OR REGRESSION DEBUGGING

A previously working feature now produces incorrect results.

Examples:

- Pagination skips records after a deletion.
- A billing service applies discounts in the wrong order.
- A parser incorrectly handles escaped delimiters.
- A date library fails around leap-year boundaries.
- A scheduler executes recurring jobs twice after restart.

The verifier should test both the reported failure and normal behavior that must remain unchanged.


B. FAILING-TEST-SUITE DEBUGGING

The repository contains several failing tests, but the failures may share one hidden root cause.

Examples:

- Eight tests fail because a cache key is incorrectly normalized.
- Integration tests fail because transaction state is retained between requests.
- Snapshot tests fail because object fields are nondeterministically ordered.
- Tests pass individually but fail when run together.

This becomes a stronger task when the visible failures point to different parts of the codebase, while the real cause is deeper or shared.


C. CONCURRENCY DEBUGGING

The problem only appears under parallel or asynchronous execution.

Examples:

- Race condition in an inventory reservation service.
- Deadlock between two database transactions.
- Duplicate message processing by concurrent workers.
- Shared cache mutation without synchronization.
- Asynchronous cleanup occurs before an upload finishes.

Tests should repeatedly exercise concurrent behavior rather than only statically inspect whether a lock was added.


D. STATE-MANAGEMENT DEBUGGING

The system behaves incorrectly after a specific sequence of operations.

Examples:

- An undo operation corrupts subsequent redo history.
- A retry creates duplicate database records.
- A resumed workflow loses partially completed state.
- A service restart reloads stale checkpoint data.
- Session expiration clears the wrong user's state.

The verifier should run operation sequences, restart processes where appropriate, and validate final state.


E. INTEGRATION DEBUGGING

Two individually functioning components do not work correctly together.

Examples:

- API request signing disagrees between client and server.
- Database timestamps use different timezone assumptions.
- A message producer and consumer disagree about schema versions.
- A command-line tool produces data another service cannot parse.
- A reverse proxy removes a required header.

This may also qualify for the api_integration or db_interaction subcategory while retaining debugging as the primary category. Subcategories are a separate metadata axis and multiple subcategories may be used when applicable.


F. RESOURCE AND PERFORMANCE DEBUGGING

The system functions but leaks or becomes unacceptably slow because of a defect.

Examples:

- File descriptors remain open after failed imports.
- Memory grows with every completed request.
- An index is bypassed because a query casts the indexed column.
- A cache never evicts expired entries.
- A recursive operation becomes exponential on nested input.

A pure "make this faster" request may be software engineering. It becomes debugging when the task begins with an unexplained regression or abnormal behavior that must be diagnosed.


G. CONFIGURATION AND RUNTIME DEBUGGING

The application code may be correct, but runtime configuration causes failure.

Examples:

- Incorrect process permissions prevent socket creation.
- Environment-variable precedence selects the wrong database.
- TLS certificate chains are loaded in the wrong order.
- A service works manually but fails under its supervisor.
- File paths behave differently when the process starts from another directory.

Be careful with classification here. If the task is primarily about installing packages, resolving dependencies, or repairing the build, build-and-dependency-management may be more accurate. If it is mainly configuring an operating system or service, system-administration may be more accurate.


RECOMMENDED DEBUGGING TASK SHAPE

environment/
└── app/
    ├── existing source code
    ├── existing tests
    ├── configuration files
    ├── sample data
    └── logs or reproducible failure conditions

A strong debugging task should provide:

- a real symptom
- enough evidence to reproduce it
- an unknown or non-obvious cause
- constraints on what must remain compatible
- multiple interacting files or components
- deterministic success criteria

Subtle root-cause analysis is a good way to produce hard tasks. Obvious debugging patterns commonly make tasks too easy.


HOW DEBUGGING TESTS SHOULD WORK

A debugging verifier should usually include:

1. Failure reproduction test
   Confirms that the original problem is actually repaired.

2. Regression tests
   Confirm that the fix works on related inputs not explicitly shown in the prompt.

3. Preservation tests
   Ensure previously correct behavior remains correct.

4. Sequence or stress tests
   Useful for concurrency, restart, state, or resource problems.

5. Anti-hardcoding tests
   Generate additional inputs or execute alternate scenarios.

6. Interface compatibility tests
   Ensure public commands, APIs, schemas, or file formats were not unnecessarily changed.

Tests should execute behavior instead of looking for a particular code string or implementation technique. Every described behavior should have corresponding tests, and anti-cheating measures should be present.


EXAMPLE DEBUGGING TASK

Title:
Repair duplicate execution in a persistent job scheduler

Starting condition:

- /app/scheduler/ contains an existing scheduler.
- Recurring jobs are stored in SQLite.
- Jobs sometimes execute twice after the worker restarts.
- Existing visible tests do not reveal the complete failure sequence.

Agent's central activity:

- reproduce the restart scenario
- inspect transaction and checkpoint behavior
- identify the root cause
- repair it without changing the public CLI

Verifier checks:

- normal jobs execute once
- restart during execution does not duplicate completed jobs
- legitimately failed jobs can still retry
- two workers do not execute the same job
- existing CLI behavior remains compatible

Category:

category = "debugging"

The defining feature is that diagnosis is the main challenge.


======================================================================
2. SOFTWARE-ENGINEERING TASKS
======================================================================

OFFICIAL MEANING

Software-engineering tasks focus on developing or testing features and algorithms, improving or optimizing existing features, implementing tests, fixing defects as part of broader development, or maintaining software projects. Typical examples include implementing a caching algorithm, correcting a race condition, and optimizing database queries.


WHEN A TASK SHOULD BE CLASSIFIED AS SOFTWARE ENGINEERING

Use:

category = "software-engineering"

when the central question is:

"What software capability must be designed, implemented, extended, optimized, or maintained?"

The agent may work with an existing repository, but the main intellectual work is implementation rather than discovering an unknown fault.


COMMON WAYS TO CREATE SOFTWARE-ENGINEERING TASKS

A. NEW FEATURE IMPLEMENTATION

The agent must add a clearly specified capability to an existing application.

Examples:

- Add resumable uploads to a storage service.
- Implement audit-history support in an existing API.
- Add a dry-run mode to a deployment tool.
- Add hierarchical configuration inheritance.
- Add transactional batch operations to a key-value store.

The prompt should specify behavior and compatibility constraints, but not prescribe the exact implementation.


B. ALGORITHM OR DATA-STRUCTURE IMPLEMENTATION

The agent must implement non-trivial logic with correctness or performance requirements.

Examples:

- Implement an LRU-K cache.
- Add incremental topological ordering.
- Implement interval merging with provenance tracking.
- Add a bounded priority queue with stable ordering.
- Implement conflict-free merging for replicated state.

A basic textbook algorithm is often too easy. Difficulty should come from integration, edge cases, state persistence, compatibility, or performance, not from obscurity alone.


C. API OR CLI DEVELOPMENT

The agent must expose new behavior through an interface.

Examples:

- Add versioned REST endpoints.
- Implement a command-line migration utility.
- Add streaming output to an existing CLI.
- Build an import/export interface.
- Add pagination, filtering, and cursor validation.

When API source code is included and API interaction is central, api_integration may be added as a subcategory. External network dependencies should be avoided; API implementations should be included or mocked inside the task environment.


D. REFACTORING AND ARCHITECTURAL IMPROVEMENT

The observable behavior largely remains the same, but the internal design must support a concrete requirement.

Examples:

- Separate storage adapters from business logic.
- Replace a monolithic parser with extensible handlers.
- Introduce transactional boundaries.
- Remove circular dependencies while preserving APIs.
- Make a component replaceable through an interface.

"Make this code cleaner" is too subjective. The task needs measurable outcomes such as interface separation, plugin loading, reduced duplication, preserved compatibility, or independently testable components.


E. PERFORMANCE OPTIMIZATION

The agent must improve performance under explicit constraints.

Examples:

- Reduce query count from quadratic to linear growth.
- Implement batched database writes.
- Add bounded caching.
- Replace repeated full-file scans with an index.
- Reduce peak memory for large input streams.

Tests should validate both correctness and measurable performance characteristics. Avoid unstable wall-clock thresholds where possible; operation counts, query counts, bounded memory models, or deliberately large deterministic fixtures are generally safer.


F. TEST ENGINEERING

The main deliverable is a meaningful test capability.

Examples:

- Add contract tests for a plugin system.
- Build a deterministic integration-test harness.
- Add property-based tests for serialization round trips.
- Implement fault-injection tests.
- Create migration compatibility tests.

Simply writing a few unit tests is usually too easy. A stronger task requires environment setup, fixtures, state isolation, realistic failure cases, or cross-component validation.


G. COMPATIBILITY AND MIGRATION ENGINEERING

The system must support old and new representations or versions.

Examples:

- Support reading schema versions 1-3 while writing version 3.
- Add backward-compatible configuration migration.
- Preserve old CLI flags while introducing a new command structure.
- Upgrade a storage format without losing data.
- Implement rolling-upgrade compatibility between service versions.

The verifier should test multiple versions and mixed states rather than only a single happy path.


H. MULTI-COMPONENT FEATURE DEVELOPMENT

The feature spans multiple layers, such as:

- database schema
- domain logic
- API
- CLI
- background worker
- persistence
- tests

This is suitable for milestone tasks when each stage is genuinely a prerequisite for the next. Milestone tasks should have sequential stages with aligned milestone-specific solution and test files.


RECOMMENDED SOFTWARE-ENGINEERING TASK SHAPE

environment/
└── app/
    ├── existing modules
    ├── public interfaces
    ├── incomplete implementation
    ├── sample configuration
    ├── database or local services
    └── existing tests

The task should define:

- required capability
- public interface
- input and output behavior
- compatibility expectations
- error behavior
- persistence or concurrency rules
- prohibited regressions
- measurable performance constraints, where relevant


HOW SOFTWARE-ENGINEERING TESTS SHOULD WORK

A software-engineering verifier should normally include:

1. Public contract tests
   Test APIs, commands, functions, or files through their supported interface.

2. Functional tests
   Verify required behavior.

3. Edge-case tests
   Test empty state, invalid input, large input, duplicate operations, and boundary values.

4. State-transition tests
   Important for persistence, retries, transactions, and workflows.

5. Compatibility tests
   Ensure existing behavior continues to work.

6. Performance or resource tests
   When optimization is an explicit requirement.

7. Anti-hardcoding tests
   Use multiple or generated inputs.

Quality tasks require deterministic behavioral tests, clear requirements, multi-step work, and no easy hardcoding or test-inspection shortcuts.


EXAMPLE SOFTWARE-ENGINEERING TASK

Title:
Implement a crash-safe disk-backed cache

Starting condition:

- /app/cache/ contains an in-memory cache.
- Public methods already exist.
- Disk persistence functions are incomplete.

Required capability:

- values survive process restart
- writes are atomic
- expired entries are not restored
- size limits are enforced
- corrupted trailing records do not destroy valid earlier entries
- public APIs remain unchanged

Verifier checks:

- write/read behavior
- restart persistence
- expiration
- eviction order
- interrupted write recovery
- invalid record handling
- compatibility with existing callers

Category:

category = "software-engineering"

The main challenge is designing and implementing a capability, not diagnosing an unexplained defect.


======================================================================
3. DATA-PROCESSING TASKS
======================================================================

OFFICIAL MEANING

Data-processing tasks primarily transform, parse, filter, aggregate, or derive outputs from datasets, files, or directories. Typical examples include transforming CSV data, aggregating logs, and filtering or sorting JSON datasets.


WHEN A TASK SHOULD BE CLASSIFIED AS DATA PROCESSING

Use:

category = "data-processing"

when the central objective is:

"Read these inputs, apply specified data rules, and produce correct derived outputs."

Code may need to be written, but the principal product is usually one or more processed artifacts:

- transformed dataset
- normalized records
- report
- index
- manifest
- reconciled ledger
- converted file
- aggregate summary
- partitioned dataset
- deduplicated collection


COMMON WAYS TO CREATE DATA-PROCESSING TASKS

A. PARSING AND NORMALIZATION

Convert inconsistent raw data into a defined canonical representation.

Examples:

- Normalize timestamps from several formats.
- Parse nested application logs.
- Convert mixed units to a canonical unit.
- Normalize names and identifiers.
- Parse multiline records with escaped delimiters.

The prompt must specify the output schema and rules for invalid input.


B. FILTERING, SORTING, AND SELECTION

Extract relevant records according to non-trivial rules.

Examples:

- Select the newest valid record per entity.
- Filter events according to effective-date rules.
- Apply include/exclude rules with precedence.
- Sort records using locale-independent ordering.
- Select complete transaction chains.

This becomes harder when rules interact rather than operating independently.


C. AGGREGATION

Produce grouped or windowed summaries.

Examples:

- Aggregate usage by account and billing period.
- Compute rolling statistics.
- Generate per-service error summaries.
- Calculate inventory balances from event streams.
- Produce hierarchical totals.

The verifier should independently recompute expected aggregates from its own fixtures.


D. JOINING AND RECONCILIATION

Combine records from multiple sources and resolve discrepancies.

Examples:

- Reconcile invoices, payments, and refunds.
- Match sensor readings to calibration periods.
- Join shipment events with order records.
- Resolve duplicate identities across systems.
- Match records using prioritized identifiers.

This is stronger than a simple database join when there are missing records, temporal rules, duplicate candidates, or conflicting values.


E. DEDUPLICATION AND ENTITY RESOLUTION

Identify records that represent the same logical entity.

Examples:

- Deduplicate contacts using normalized fields.
- Merge repeated log events while preserving provenance.
- Identify duplicate transactions across exports.
- Resolve documents by checksum and metadata.
- Merge overlapping time intervals.

Avoid vague instructions such as "remove duplicates." Define what counts as equivalent and how conflicting fields are resolved.


F. DATA VALIDATION AND QUARANTINE

Separate valid and invalid records while preserving diagnostics.

Examples:

- Validate records against cross-field rules.
- Produce a rejection file with reason codes.
- Detect broken references between files.
- Verify checksums and sequence continuity.
- Identify impossible state transitions.

A useful deliverable pattern is:

/app/output/accepted.jsonl
/app/output/rejected.jsonl
/app/output/summary.json

Each schema and rejection reason should be precisely defined.


G. FORMAT CONVERSION

Convert between file or data representations.

Examples:

- CSV to normalized JSONL.
- XML records to SQLite.
- Binary event files to Parquet.
- Markdown metadata to a searchable manifest.
- Directory trees to archive indexes.

A straightforward one-to-one format conversion may be too easy. Add meaningful semantics such as schema evolution, nested records, streaming constraints, malformed inputs, or cross-file references.


H. FILE AND DIRECTORY PROCESSING

The input is a collection of files rather than a single dataset.

Examples:

- Build an inventory from a nested archive.
- Detect duplicate media by content.
- Merge configuration fragments according to precedence.
- Generate a dependency manifest from project directories.
- Extract and correlate records from rotated logs.

The data-processing category includes processing files and directories, not only tabular datasets.


I. DATABASE-BACKED PROCESSING

The agent must query or transform data in a real database engine.

Examples:

- Reconstruct account balances from event tables.
- Create materialized summaries.
- Repair inconsistent foreign-key relationships.
- Migrate denormalized records into normalized tables.
- Generate a report through SQL and application logic.

Such a task can use:

category = "data-processing"
subcategories = ["db_interaction"]

when the transformation is primary and database interaction is an additional challenge dimension. Real database interaction should be distinguished from tasks that merely use flat CSV files.


RECOMMENDED DATA-PROCESSING TASK SHAPE

environment/
├── app/
│   └── incomplete or existing processing code
├── input/
│   ├── source-a/
│   ├── source-b/
│   └── metadata/
└── schemas/
    └── output-schema.json

A strong data-processing prompt should explicitly define:

- input locations
- accepted input formats
- record interpretation rules
- normalization rules
- precedence rules
- invalid-record behavior
- output locations
- output schemas
- ordering rules
- numeric precision
- date and timezone handling
- idempotency expectations

Output files should be named, and structured-data schemas should be fully specified where applicable.


HOW DATA-PROCESSING TESTS SHOULD WORK

A data-processing verifier should normally include:

1. Output existence tests
2. Schema validation
3. Exact transformation tests
4. Cross-file consistency tests
5. Ordering and determinism tests
6. Invalid-input and rejection tests
7. Duplicate and missing-data tests
8. Idempotency tests
9. Generated or alternate input fixtures
10. Anti-hardcoding tests

Avoid verifying only one supplied dataset whose final output can be hardcoded. A stronger verifier can copy alternate fixtures into the input location, execute the processor, and validate the generated result.


EXAMPLE DATA-PROCESSING TASK

Title:
Reconstruct shipment timelines from inconsistent carrier exports

Starting condition:

/app/input/carrier_a.csv
/app/input/carrier_b.jsonl
/app/input/carrier_c.xml
/app/input/timezone_map.json

The sources use different:

- event names
- timestamp formats
- location identifiers
- package identifiers
- cancellation semantics

Required outputs:

/app/output/timelines.jsonl
/app/output/rejected_events.jsonl
/app/output/summary.json

Verifier checks:

- schemas
- canonical event mapping
- timestamp normalization
- duplicate handling
- cancellation precedence
- event ordering
- rejection reasons
- counts and summaries
- alternate hidden shipments

Category:

category = "data-processing"

The main challenge is interpreting and transforming data into derived artifacts.


======================================================================
IMPORTANT OVERLAP CASES
======================================================================

Because the official definitions overlap, particularly because software engineering can include bug fixing, classify according to the dominant reasoning activity, not merely keywords in the prompt.

Task scenario:
Find why a CSV parser drops fields containing escaped commas
Best category:
debugging
Reason:
Root-cause diagnosis is central.

Task scenario:
Implement a new streaming CSV parser library
Best category:
software-engineering
Reason:
Building reusable software is central.

Task scenario:
Process supplied CSV exports into a normalized report
Best category:
data-processing
Reason:
Derived data output is central.

Task scenario:
Diagnose incorrect totals in an existing ETL pipeline
Best category:
debugging
Reason:
Existing behavior is wrong and the cause must be found.

Task scenario:
Add a new aggregation stage to an ETL framework
Best category:
Usually data-processing
Reason:
The new capability's purpose is dataset transformation.

Task scenario:
Build a generic workflow engine that can run arbitrary ETL plugins
Best category:
software-engineering
Reason:
The reusable engine is the main product.

Task scenario:
Repair a race condition in a data-import worker
Best category:
debugging
Reason:
Concurrency defect diagnosis dominates.

Task scenario:
Optimize a generic database access library
Best category:
software-engineering
Reason:
Library behavior and design dominate.

Task scenario:
Aggregate database tables into specified reports
Best category:
data-processing
Reason:
Data transformation dominates.

Task scenario:
Resolve a broken package lockfile
Best category:
build-and-dependency-management
Reason:
Dependency resolution is the primary activity.

Task scenario:
Configure a service and user permissions from scratch
Best category:
system-administration
Reason:
Operating-system and service configuration are primary.


======================================================================
A RELIABLE CATEGORY DECISION TREE
======================================================================

Does the task start with a malfunction whose cause is not directly given?
|
+-- Yes
|   |
|   +-- Is identifying and repairing that cause the main challenge?
|       |
|       +-- Yes -> debugging
|
+-- No, or diagnosis is only a minor part
    |
    +-- Is the main result a transformed dataset, report, manifest,
    |   normalized file collection, or other derived data artifact?
    |   |
    |   +-- Yes -> data-processing
    |
    +-- Is the main result a new or improved software capability,
        algorithm, interface, architecture, or reusable tool?
        |
        +-- Yes -> software-engineering

Then perform a final boundary check:

Mostly packages/build?            -> build-and-dependency-management
Mostly OS/services/network setup? -> system-administration
Mostly model training/inference?  -> machine-learning
Mostly security behavior?         -> security
Mostly scientific numerical work? -> scientific-computing


======================================================================
HOW TO MAKE EACH TYPE MEANINGFULLY DIFFICULT
======================================================================

All three categories still need clear instructions, deterministic verification, multi-step reasoning, behavioral tests, and anti-cheating protections.


DEBUGGING DIFFICULTY

Make the task harder through:

- multiple symptoms with one shared cause
- failure that appears only after a sequence of actions
- concurrency or restart behavior
- misleading but legitimate logs
- compatibility constraints
- several plausible root causes
- requirement to preserve unrelated behavior

Do not make it difficult by hiding necessary information or introducing nondeterministic failures.


SOFTWARE-ENGINEERING DIFFICULTY

Make the task harder through:

- several interacting modules
- state persistence
- backward compatibility
- concurrency
- rollback behavior
- explicit performance constraints
- partial failure handling
- schema or API versioning
- multiple public interfaces

Avoid simple tutorial-style feature requests or isolated one-function exercises.


DATA-PROCESSING DIFFICULTY

Make the task harder through:

- multiple input formats
- cross-file relationships
- temporal rules
- incomplete and conflicting records
- strict schemas
- precedence rules
- deterministic rejection reasons
- precision and rounding requirements
- generated hidden fixtures
- large-data or streaming constraints

Avoid making the task merely "read CSV, rename columns, write JSON."


======================================================================
FINAL DISTINCTION IN ONE SENTENCE
======================================================================

- Debugging: Find what is wrong and repair it.
- Software engineering: Design or implement a software capability.
- Data processing: Transform input data into correct derived output.

The strongest deciding factor is not whether code, files, or databases appear in the task. It is what the agent is fundamentally being evaluated for doing.


SOURCES

Terminus-2.0 Task Taxonomy:
https://terminus-2.cognyzer.com/03-understanding-tasks/12-task-taxonomy.html

Terminus-2.0 Task Subtypes:
https://terminus-2.cognyzer.com/03-understanding-tasks/15-task-subtypes.html

Terminus-2.0 Difficulty Guidelines:
https://terminus-2.cognyzer.com/03-understanding-tasks/18-difficulty-guidelines.html

Terminus-2.0 Milestones:
https://terminus-2.cognyzer.com/03-understanding-tasks/14-milestones.html

Terminus-2.0 Submission Checklist:
https://terminus-2.cognyzer.com/02-submission-process/07-submission-checklist.html

Terminus-2.0 What Makes a Good Task:
https://terminus-2.cognyzer.com/03-understanding-tasks/09-what-makes-a-good-task.html
