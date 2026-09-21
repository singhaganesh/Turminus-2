# Harbor Task Components (Edition 2)

Harbor is the evolution of Terminal-Bench. Non-milestone layout:

```
my-task/
├── instruction.md
├── task.toml
├── environment/
│   ├── Dockerfile          # required (or docker-compose.yaml)
│   └── [build files]
├── solution/solve.sh
├── tests/
│   ├── test.sh
│   └── test_outputs.py
└── README.md               # optional
```

Milestone tasks: no root `instruction.md` / `tests/` / `solution/` — use `steps/milestone_N/` (see `task-creation.mdc`).

## 1. instruction.md

Agent-facing prompt. See [INSTRUCTION_STYLING.md](INSTRUCTION_STYLING.md).

## 2. task.toml

```toml
version = "2.0"

[metadata]
author_name = "anonymous"
author_email = "anonymous"
difficulty = "hard"
category = "software-engineering"
subcategories = []
number_of_milestones = 0
codebase_size = "small"
languages = ["bash"]
tags = ["example-tag"]
expert_time_estimate_min = 60
junior_time_estimate_min = 120

[verifier]
timeout_sec = 450.0

[agent]
timeout_sec = 900.0

[environment]
build_timeout_sec = 600.0
cpus = 2
memory_mb = 4096
storage_mb = 10240
allow_internet = false
```

Compose/multi-container metadata when applicable: `custom_docker_compose = true`, `is_multi_container = true` (new tasks of these types not accepted in this repo).

## 3. environment/

Harbor images must be **reproducible**, **cacheable**, **lazy-pull friendly**, **auditable**
(digest-pinned, no secrets), **complete** (no network at runtime), **siloed** (no
solution/tests in image), and **resourced** (`cpus`, `memory_mb`, `storage_mb` in
`task.toml`).

### Layout and policy

- Build context **only** under `environment/` — never escape with `context: ..` in compose
- Keep total size ≤ **100 MiB** and each file ≤ **50 MiB** (`check_build_context_size`)
- **Every image:** install `tmux` and `asciinema` (agent runtime requires both; missing either fails agent runs silently)
- Pin every `FROM` with `@sha256:<digest>` (`check_pinned_images`); final runtime base should be a **§2 canonical Terminal-Bench image** or a **justified non-canonical** base (`check_sanctioned_base_images`) — see [DOCKERFILE_BEST_PRACTICES.md](DOCKERFILE_BEST_PRACTICES.md)
- Pin pip/npm/apt with `==` or lockfiles (`pinned_dependencies`)
- **Never** `COPY` `solution/` or `tests/` into image; no ground-truth answers in agent-visible paths
- **Never** `mkdir` or `chown` `/tests`, `/solution`, or `/oracle` in Dockerfile
- No privileged mode, `SYS_ADMIN`, `NET_ADMIN`, `SYS_MODULE`, or `docker.sock` mounts
- Do not store verifier ground truth in agent-writable paths; reference fixtures belong in controlled locations
- Non-trivial contexts should include `.dockerignore` (see [CI_CHECKS.md](CI_CHECKS.md))

**Runtime paths (reserved by Harbor):**

| Path | Purpose |
|------|---------|
| `/logs/verifier/` | `reward.txt`, verifier logs |
| `/logs/agent/` | Agent logs |
| `/oracle/` | Solution at runtime |
| `/tests/` | Tests at runtime |

Compose must not override reserved mounts: `/logs/artifacts/`, `/logs/verifier/`, `/tests/`, `/solution/`.

### Starter Dockerfile

Location: `environment/Dockerfile`.

```dockerfile
FROM python:3.13-slim@sha256:<digest>

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        asciinema \
        ca-certificates \
        git \
        tmux \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    pandas==2.1.0

COPY app/ /app/
ENV PYTHONPATH=/app
```

### Minimum environment checklist

Before task-specific setup:

- [ ] `environment/Dockerfile` exists and builds locally (`cd environment && docker build -t my-task .`)
- [ ] Final runtime image includes `tmux` and `asciinema`
- [ ] Every `FROM` and compose `image:` includes `@sha256:<digest>`
- [ ] Final runtime base is a §2 canonical TB image or has credible justification ([DOCKERFILE_BEST_PRACTICES.md](DOCKERFILE_BEST_PRACTICES.md))
- [ ] Language deps exact-pinned or locked; apt uses `--no-install-recommends` + `rm -rf /var/lib/apt/lists/*`
- [ ] `environment/` ≤ 100 MiB total; no file > 50 MiB
- [ ] Non-trivial env has `.dockerignore`
- [ ] Image does not copy `solution/`, `tests/`, or hidden verifier assets
- [ ] Verifier deps baked into image (pinned pytest + plugins); `tests/test.sh` does not install or download at runtime
- [ ] Compose has no privileged containers or unsafe capabilities
- [ ] `[environment] allow_internet = false` in `task.toml`

Full Dockerfile policy: [CI_CHECKS.md](CI_CHECKS.md) (blocking vs warning checks).

### Layer ordering and hygiene (warnings by default)

1. Base OS packages → runtime/package-manager setup → copy manifests → install deps → copy source → task build step → `WORKDIR`
2. One apt transaction per stage; no `apt-get upgrade`
3. Multi-stage builds when compiling; do not leave build tools in final runtime unless the task requires the agent to compile
4. Pin downloaded binaries by version + checksum (no `curl | sh` without verification)
5. `COPY` files instead of heredocs; extract archives and delete tarball in same stage
6. Use `COPY --chmod` / `--chown` instead of `chmod -R` / `chown -R`
7. Prefer `COPY src/ /app/src/` over `COPY . /app` unless context is minimal and `.dockerignore` is strict

### Local troubleshooting

```bash
cd environment
docker build -t my-task .
docker run -it my-task bash
harbor tasks start-env -p <task-folder> -i   # interactive env
```

If compose fails: `docker compose logs`. On macOS Docker Desktop: enable socket access in Advanced settings if needed.

### Common patterns

**Git repository task** — pin commit at build to prevent cheat-by-update:

```dockerfile
RUN git clone https://github.com/example/repo.git /app \
    && cd /app && git checkout abc123def456
```

**Optional advanced (warnings if missing):** set `SOURCE_DATE_EPOCH` for reproducible builds; add OpenContainers image labels (`org.opencontainers.image.*`) for audit metadata. Platform also supports `solution/solution.yaml` for interactive oracles (vim, etc.) — not used in standard repo tasks.

## 4. solution/solve.sh

Expert-authored oracle script. Harbor runs it via the **Oracle agent** (`harbor run -a oracle -p <task>`) to prove the task is solvable. If oracle fails, fix before submission.

### Principles

- **Command sequence, not answers** — demonstrate steps to derive the result; never `echo` golden outputs
- **Deterministic** — no unseeded randomness, wall-clock timing, or runtime network; use seeds when randomness is required
- **Human-authored** — written by you; minimal syntax help from LLMs only
- **Real work** — fixes source / runs pipelines; not hardcoded pass values copied from tests
- **`set -e` is OK here** (unlike `test.sh`) — fail fast on oracle errors

```bash
#!/bin/bash
set -e
cd /app
# ... fix commands that derive the answer ...
```

### Milestone tasks

Per `steps/milestone_N/solution/`: wrapper `solve.sh` calls `solveN.sh` scoped to milestone N only. Filesystem persists across milestones — reset state explicitly when needed.

### Testing

```bash
harbor run -a oracle -p <task-folder>
harbor tasks start-env -p <task-folder> -i   # manual step-through
```

Platform may run oracle **3×** on upload; Step 4 in this repo runs oracle **10×** for flakiness (`harbor_gate.py --oracle-repeat 10`).

## 5. tests/test.sh

Bash entry point that runs **Python pytest** and writes the reward file. For non-Python tasks, pytest still drives the CLI/service under test — do not replace pytest with JUnit/Jest/go test in `test.sh`.

### Requirements

- All verifier deps in Dockerfile (pinned pytest, plugins; typically `/opt/verifier` on `PATH`)
- `tests/test.sh` invokes Dockerfile-provided `pytest` only — **no** `uvx` / pip / apt install
- No runtime `apt`/`pip`/`curl`/`npm`/`git clone`/`uvx` when `allow_internet = false`
- **Binary reward only:** `0` or `1` in `/logs/verifier/reward.txt` (not partial scores)
- Same logic for oracle and agent — no `/oracle` branching
- Platform minimum uses `python -m pytest`; **this repo** uses the internet-disabled template below

```bash
#!/bin/bash

if [ "$PWD" = "/" ]; then
    echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile."
    exit 1
fi

pytest --ctrf /logs/verifier/ctrf.json ${TEST_DIR:-/tests}/test_outputs.py -rA
rc=$?
if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
```

Prefer `rc=$?` immediately after the `pytest` invocation.

Do **not** use `set -e` before the reward block (breaks `$?` capture). Optional `mkdir -p /logs/verifier` preamble is fine.

## 6. tests/test_outputs.py

All verifier tests in Python/pytest regardless of task language.

### Principles

1. **Test behavior, not implementation** — run code and check results; do not grep source for patterns
2. **Informative docstrings** on every test (LLMaJ `informative_test_docstrings`)
3. **Full prompt coverage** — every explicit requirement, implicit expectation, and critical edge case in `instruction.md` maps to at least one test; nothing tested that is not described
4. **No latency/throughput assertions** — correctness only
5. **Independent tests** — no order dependency or shared mutable global state
6. **Anti-cheating** — computed checks; answers not derivable from reading tests alone

### NOP baseline

The **NOP agent** runs `test.sh` without doing any task work. It must score **0.0**. If NOP passes, the task or verifier is broken. Local: `harbor_gate.py --nop`.

## Validation checklist

See [CI_CHECKS.md](CI_CHECKS.md) for the full blocking vs warning check list
(`check_pinned_images`, `check_sanctioned_base_images`, `check_build_context_size`,
Dockerfile hygiene warnings, etc.).

- [ ] Human `instruction.md`, complete `task.toml`
- [ ] Dockerfile builds; pinned deps; `allow_internet = false`
- [ ] Verifier deps in image, not `test.sh`
- [ ] Oracle is a real command sequence
- [ ] `test.sh` always produces reward file
- [ ] Instruction ↔ tests aligned
- [ ] No solution/tests in image
