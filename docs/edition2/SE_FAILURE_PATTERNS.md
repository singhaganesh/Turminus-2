# Software-Engineering Failure Patterns — Terminal-Bench 2.1 Corpus Study

Source: `terminal-bench-2-1/tasks/*/task.toml` filtered to `category =
"software-engineering"` (25 of 89 tasks). For each, read `instruction.md` +
`task.toml` (difficulty/time-estimate metadata) and spot-checked
`tests/test_outputs.py` / `solution/` for 12 of the 25 to confirm the
instruction-level read against the actual grading mechanism. This is a static
content study, not a rollout — difficulty labels below are the repo's own
`task.toml` `difficulty` field (author-assigned), not a fresh frontier
measurement. Treat this as a structural pattern inventory to calibrate our SE
authoring engine, not as new empirical proof.

## The 25 tasks, by declared difficulty

**Hard (13):** circuit-fibsqrt, fix-ocaml-gc, make-doom-for-mips,
path-tracing-reverse, make-mips-interpreter, path-tracing, regex-chess,
gpt2-codegolf, polyglot-rust-c, cancel-async-tasks, torch-pipeline-parallelism,
torch-tensor-parallelism, write-compressor

**Medium (10):** build-pmars, build-pov-ray, code-from-image, kv-store-grpc,
pypi-server, git-leak-recovery, polyglot-c-py, winning-avg-corewars,
headless-terminal, schemelike-metacircular-eval

**Easy (3):** fix-git, cobol-modernization, prove-plus-comm

13/25 (52%) are hard — a much higher hard-rate than a typical repair-domain
corpus, which is itself a signal: **SE hardness in this benchmark is not
accidental — it is authored via a small number of repeatable mechanisms.**

## The six failure-pattern families

### 1. Byte/size-budget forces a real algorithm, not a lookup or a copy

`regex-chess` (<100k regex pairs, <10MB), `path-tracing` (<2KB gzip'd C),
`path-tracing-reverse` (<2KB gzip'd C), `write-compressor` (≤2500 bytes
compressed), `gpt2-codegolf` (<5000 byte C file), `circuit-fibsqrt` (<32,000
logic-gate lines).

**Mechanism:** the task states a full behavioral spec (what the output must be)
plus a hard resource ceiling far too small for the "obvious" implementation
(embed a lookup table, hardcode known cases, brute-force enumerate). A model
that tries the naive approach hits the byte/line/size limit and fails a
*separate, independently-checked* constraint — it cannot pass by memorizing or
tabulating; it must derive the actual generating algorithm (compression scheme,
rendering math, arithmetic-circuit construction, regex-based move grammar).

**Why frontier models fail it:** these are genuine algorithm-design/derivation
problems disguised as "write a file that satisfies X." There is no shortcut
that fits under the ceiling. This is the cleanest real-world instance of our
**"naive impl fails" SE gate** — the size constraint IS the naive-impl trap,
made mechanically enforced instead of merely graded behaviorally.

**Authoring takeaway:** a hard resource/size ceiling checked independently of
the functional test is one of the strongest, cheapest-to-implement SE hardness
levers available. It converts "did you implement a correct algorithm" into a
binary, unfakeable check.

### 2. Independent-oracle / held-out conformance (not visible-example grading)

`regex-chess` (verified move-by-move against the `python-chess` library across
full historical games — Immortal Game, Game of the Century, Naroditsky vs
Ivanchuk — not just the one worked example in the instruction), `torch-tensor-
parallelism` / `torch-pipeline-parallelism` (numeric outputs checked with
`torch.allclose` against a reference implementation across `world_size` = 1, 2,
4 — configurations the agent doesn't get worked examples for), `make-mips-
interpreter` / `make-doom-for-mips` (output frame checked by L2 image
similarity against a reference frame, not just "did it not crash"),
`cobol-modernization` (output `.DAT` files must be byte-identical to running
the real COBOL binary via GnuCOBOL — the COBOL program IS the oracle).

**Mechanism:** the instruction gives one worked example (sometimes with the
exact expected output shown), but grading independently re-derives or
re-executes the reference behavior on inputs the agent never saw stated. A
solution tuned to the one visible example (or to a narrow reading of the stated
rule) diverges from the independent oracle on the unseen cases.

**Why frontier models fail it:** models pattern-match the worked example and
under-generalize — e.g. get basic chess moves right but miss castling-rights
tracking across a full game, or get `world_size=2` right but not `world_size=4`
sharding. This is exactly our **unfakeable conformance discriminator** —
except here it is realized as "run an independent reference implementation /
library / real toolchain," not a hand-authored held-out fixture. That is a
stronger, cheaper discriminator than hand-crafted held-out cases: reuse an
existing correct implementation (`python-chess`, GnuCOBOL, a reference PyTorch
op) as the oracle instead of authoring one.

### 3. Concurrency / lifecycle correctness under adversarial interruption

`cancel-async-tasks` (five test scenarios: normal concurrency, `max_concurrent`
throttling with timing assertions, and THREE separate cancel-timing
scenarios — cancel below/at/above the concurrency ceiling — each still
requiring cleanup code to run), `headless-terminal` (Ctrl-C mid-command must
kill the process AND not leave the output file, `.bashrc` must be sourced,
shell state must persist across calls, background commands must actually be
backgrounded and pollable).

**Mechanism:** the naive implementation of the stated contract (a semaphore, a
`subprocess.Popen`) satisfies the *steady-state* description but breaks under
an *interruption* the instruction only implies ("sometimes I cancel via
keyboard interrupt but I want cleanup to still run"). Each interruption timing
variant is graded separately, so a fix for one (e.g. cleanup-on-cancel-below-max)
does not guarantee the sibling case (cleanup-on-cancel-above-max) passes.

**Why frontier models fail it:** correct cancellation/cleanup semantics under
`asyncio` (or correct PTY/session semantics for an interactive shell) is a
narrow, easy-to-get-almost-right domain — the naive version passes the calm-path
tests and fails exactly the interruption-timing matrix. This maps directly to
our **≥3 independent interacting facets** test: "obeys max_concurrent," "cleans
up on normal completion," and "cleans up on cancel at each of 3 timing points"
are graded as separate, independently-failing facets.

### 4. Self-application / bootstrapping as the discriminator

`schemelike-metacircular-eval` (the Scheme-like interpreter written by the agent
must interpret *itself* — `eval.scm` interpreting `eval.scm` interpreting a test
program — three levels deep), `fix-ocaml-gc` (the fixed GC must let the OCaml
compiler *bootstrap itself* — compile its own source — not just pass a fixed
unit-test file), `make-doom-for-mips` / `make-mips-interpreter` (the interpreter
must run a real, large, pre-existing program — DOOM — not a toy test ISA
program).

**Mechanism:** a bug that is invisible on any hand-written toy test case
surfaces only when the built artifact is asked to process something of real
complexity — itself, or a real full-scale program it wasn't specifically
tuned against. This is an unfakeable discriminator that requires zero authored
held-out fixtures: complexity of the *target itself* (self-hosting, real ISA
software) does the discriminating work.

**Why frontier models fail it:** it is easy to build an interpreter/compiler
that passes small directed tests and still has a bug that only manifests under
recursion depth, instruction coverage, or code complexity found in a real
self-hosting pass or a real 90s game engine. This is a distinct SE hardness
lever from held-out test cases: **scale/self-reference as the adversarial
input**, not a crafted edge case.

### 5. Deceptively simple spec, real protocol/format conformance underneath

`kv-store-grpc` (sounds like "store some numbers in a dict," but graded on an
actual live gRPC wire handshake — `test_real_grpc_server_running` checks the
port is listening with a real server, `test_grpc_protocol_handshake` makes a
real RPC call and checks the typed response object), `pypi-server` (graded by
an actual `pip install --index-url` round-trip against a real PEP 503 simple
index, then importing and calling the installed package), `build-pmars` (graded
on: does the debugger actually step through instructions, is it linked without
X11, AND was it built from the specific Debian source tree, not just "does the
binary run" — three independent facts about the SAME binary).

**Mechanism:** the instruction reads like an application feature ("build a
server," "package something") but the grading exercises the underlying
protocol/format machinery end-to-end and checks provenance/build facts a
"looks-right" implementation wouldn't necessarily satisfy (real wire types vs.
duck-typed responses; real PEP 503 discovery vs. a plain file server; real
Debian source lineage vs. any pmars binary that runs).

**Why frontier models fail it:** the spec reads easy, inviting a shortcut
implementation (a REST-ish shim instead of real grpc stubs; a raw HTTP file
server instead of a spec-compliant index; downloading any working pmars binary).
The grading is deliberately end-to-end and provenance-aware, so the shortcut
fails a check the instruction implied but did not spell out mechanically. This
is our **interface/protocol-contract facet** made concrete — and a caution: the
line between "fair DERIVABLE consequence" and "unstated trap" is thin here; see
Authoring takeaway below.

### 6. Cross-language / cross-toolchain identical-behavior porting

`cobol-modernization` (COBOL → Python, byte-identical `.DAT` output), `polyglot-
c-py` / `polyglot-rust-c` (one file valid simultaneously in two languages,
identical stdout), `code-from-image` (pseudocode image → any language,
identical final value), `path-tracing-reverse` (compiled binary → C source,
identical behavior without invoking the original).

**Mechanism:** the target behavior is defined by an existing artifact (another
program, an image, a compiled binary) rather than a prose spec. The agent must
extract semantics from a non-prose or foreign-language source and reproduce
them exactly in a different substrate, often under an additional constraint
(polyglot syntax validity in two languages simultaneously; independence from
the original binary).

**Why frontier models fail it:** faithful semantic extraction from a non-target
representation (bytecode/binary behavior, an image, another language's runtime
quirks — e.g. COBOL's exact rounding/field-width semantics) is where subtle
divergences hide; the failure surfaces as "close but not byte-identical" output,
which read-only inspection of the prose spec cannot catch.

## Cross-cutting observations

- **None of the 25 SE tasks are repair tasks.** Every one is `constrained_build`
  (or `reverse_engineering` for the binary/image-sourced ones) in our
  `task_shape` taxonomy — there is no hidden bug to diagnose; the instruction
  states the full target behavior. This directly confirms the SE branch we just
  added to `prompt.md` / `idea-validation.mdc` / the `tb2-check-idea-hardness`
  skill: symptoms-only framing does not apply here, and requirement≡spec is
  normal, not a leak.
- **Every hard task pairs a stated spec with an independently-enforced
  constraint the naive reading doesn't satisfy**: a size ceiling (family 1), an
  external oracle (family 2), an interruption/timing matrix (family 3), a
  self-application target (family 4), a protocol/provenance check (family 5),
  or byte-identical cross-substrate output (family 6). This is empirical
  confirmation of our SE depth-test point 1 ("naive implementation fails") and
  point 3 ("unfakeable conformance discriminator") — in this real corpus, the
  discriminator is very often an *existing* independent tool/library/toolchain
  reused as the oracle, not a hand-authored held-out fixture. That's cheaper and
  stronger than what our current SE authoring guidance emphasizes (author your
  own `adversarial_cases`) — **worth adding as a preferred technique.**
- **The "easy" tasks are the counter-examples that prove the pattern**:
  `fix-git` (single obvious git operation, no ceiling/oracle/interruption
  matrix), `prove-plus-comm` (one theorem, no adversarial dimension), `cobol-
  modernization` (family 6, but rated easy — likely because the COBOL program
  is short/simple, so the porting problem itself is shallow despite fitting a
  hard-capable family). This confirms family membership alone doesn't guarantee
  hard — the family's specific instance still needs real depth (a short/simple
  source artifact under family 6 stays easy; a large/self-hosting target under
  family 4 goes hard).
- **Time-estimate ratios track difficulty but not linearly**: hard tasks show
  junior/expert time ratios of 2–10x (e.g. `fix-ocaml-gc` 1440→14400 min = 10x;
  `regex-chess` 1440→4800 = 3.3x), suggesting the junior solver doesn't just take
  longer — they take disproportionately longer, consistent with needing to
  rediscover the domain knowledge (family-dependent: OCaml GC internals, full
  chess-rule edge cases) rather than just grinding.

## Mapping to our SE authoring engine (`prompt.md` Phase 0-B, `idea-validation.mdc`, `tb2-check-idea-hardness`)

| Corpus family | Our SE depth-test point it validates | Authoring lever to add/emphasize |
|---|---|---|
| 1. Byte/size budget | Point 1 (naive impl fails) | Prefer a **mechanically enforced** resource ceiling (size, line count, byte count) as the naive-impl trap over a purely behavioral held-out check — cheaper to verify, harder to game. |
| 2. Independent-oracle conformance | Point 3 (unfakeable discriminator) | **Reuse an existing correct library/toolchain as the oracle** (a reference parser, a real compiler, a well-known library) instead of hand-authoring `adversarial_cases` from scratch — stronger and less author-error-prone. |
| 3. Concurrency/interruption matrix | Point 2 (≥3 interacting facets) | Author the facets as an explicit **timing/interruption matrix** (before/at/after a threshold), not just "handle cancellation" — each matrix cell is graded separately. |
| 4. Self-application/bootstrapping | Point 3 (unfakeable discriminator), Point 4 (applied domain knowledge) | Where the built artifact is an interpreter/compiler/codec, prefer grading it against **itself or a real large target** over synthetic test files — zero authoring cost, strong discrimination. |
| 5. Protocol/provenance under a simple-sounding spec | Point 2 (interacting facets) + our existing false-failure firewall | **Caution, not just opportunity**: this family sits closest to the false-failure line. `build-pmars`'s provenance check (must be Debian source, not koth.org) is fair only because the instruction explicitly states it ("get the source from Debian packages instead") — an unstated provenance/protocol requirement here would be a `NOT_PUBLIC` false failure. Only adopt this lever when the extra conformance requirement is stated as plainly as `build-pmars` does. |
| 6. Cross-substrate identical porting | Point 4 (applied domain knowledge) | Byte-identical / behavior-identical framing against a real reference artifact (binary, image, foreign-language program) is a strong, low-authoring-cost hard lever, but depth still depends on the SOURCE artifact's complexity (see `cobol-modernization` counter-example) — vet the source's real complexity before assuming the family makes it hard. |

## Standing caveat

This is a **static read of 25 tasks' instructions/tests plus author-assigned
`difficulty`** — not a fresh frontier rollout. It should be used to calibrate
*which mechanisms* make SE tasks hard, not as proof any specific task currently
resolves <1/3. Per our own skill's framing: only rollouts confirm hard.
