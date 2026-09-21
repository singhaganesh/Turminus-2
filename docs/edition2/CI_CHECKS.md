# CI Checks (Edition 2)

All submissions must pass automated Agent checks. This reference explains what each
check validates, which Dockerfile checks **block** by default, which **warn** by
default, and how to fix common failures.

Run locally:

```bash
# Static / LLMaJ-style checks (matches CI model)
harbor tasks check <task-folder> -m openai/@openai/gpt-5.6

# Frontier agent trial (difficulty calibration)
harbor run -a terminus-2 -m openai/@openai/gpt-5.6 -p <task-folder>
harbor run -a terminus-2 -m anthropic/@anthropic/claude-opus-5 -p <task-folder>
```

Repo wrapper: `scripts/run_static_checks.py --task-dir tasks/<task> --version edition_2`

Local uniqueness gate (peer tasks under `tasks/`):

```bash
python3 ci_checks/check-similarity.py tasks/<task> --include-structure --enforce-threshold
```

Default threshold **15%** (local default = platform max); target **≤ 10%** when possible.
`./scripts/check-task.sh --strict` runs this as Phase A2 when peer tasks exist.

Oracle sanity: `harbor run -a oracle -p <task-folder>` or
`scripts/harbor_gate.py tasks/<task> --oracle --nop`

## Structural checks

Some checks report structural errors even when the related rule normally warns.
Missing `environment/`, missing `environment/Dockerfile`, missing `tests/test.sh`,
or malformed `task.toml` surface as errors because the checker cannot safely
inspect the task.

### `validate_task_fields`

**Severity:** Blocking.

**What it checks:** All required fields are present in `task.toml`.

**How to fix:** Ensure `task.toml` has the required `version`, `[metadata]`,
`[agent]`, `[verifier]`, and `[environment]` fields for your task type.
Milestone tasks must use the milestone-specific layout and `[[steps]]`
configuration.

### `check_task_absolute_path`

**Severity:** Blocking.

**What it checks:** Task instructions use absolute paths.

```markdown
# Bad
Edit config/settings.json

# Good
Edit /app/config/settings.json
```

### `check_privileged_containers`

**Severity:** Blocking.

**What it checks:** No privileged containers or unsafe Docker capabilities in
`docker-compose.yaml`.

```yaml
# Bad
privileged: true
```

### `check_task_sizes`

**Severity:** Blocking.

**What it checks:** Individual task files stay within platform limits. Larger
runtime datasets are handled separately by `check_build_context_size`.

**How to fix:** Remove, split, compress, or fetch optional large data at runtime
from an approved mounted source instead of baking it directly into the submitted
task.

---

## Dependency and image checks

### `pinned_dependencies`

**Severity:** Blocking.

**What it checks:** Language-package dependencies use exact version pins.

```dockerfile
# Bad
RUN pip install numpy pandas

# Good
RUN pip install numpy==1.26.4 pandas==2.1.0
```

Package-manager lockfiles are also acceptable where appropriate, such as
`package-lock.json`, `pnpm-lock.yaml`, `uv.lock`, `poetry.lock`, `Cargo.lock`,
`go.sum`, or Maven/Gradle dependency locks.

### `check_pinned_images`

**Severity:** Blocking.

**What it checks:** Every Docker `FROM` image is pinned by digest. Tags are
useful for readability, but the digest is the immutable pin.

```dockerfile
# Bad
FROM python:3.13-slim

# Good
FROM python:3.13-slim@sha256:<digest>
```

Apply the same discipline to service images in `docker-compose.yaml` when a
service uses `image:` instead of `build:`.

Local mirror: `scripts/run_static_checks.py --only dockerfile` enforces
digest-pinned `FROM` lines. `--only build_context_size` enforces the 100 MiB /
50 MiB per-file limits (blocking, same as platform). `--only sanctioned_base_image`
warns when the final runtime `FROM` is not sanctioned (platform blocks; local WARN
because many repo tasks use toolchain finals pending exemption or multi-stage reflow).

### `check_sanctioned_base_images`

**Severity:** Blocking.

**What it checks:** The **final runtime stage** uses a **§2 canonical Terminal-Bench base image** (digest-pinned; see [DOCKERFILE_BEST_PRACTICES.md](DOCKERFILE_BEST_PRACTICES.md)) **or** a non-canonical base with a **brief, credible justification** in the Dockerfile (e.g. `# BASE IMAGE JUSTIFICATION: …`) or `environment/README.md`. Missing or vague justifications are blocked.

Builder stages may use task-specific toolchain images; the **final** stage should prefer one of the 10 canonical stacks (Python, Node, Go, Rust, Java, Ruby, GCC, Maven, Debian, Ubuntu) from the platform Resources table.

```dockerfile
# Good: canonical final base (§2 table — public.ecr.aws)
FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

# Good: short library form when image:tag + digest match §2
FROM debian:bookworm-slim@sha256:4724b8cc51e33e398f0e2e15e18d5ec2851ff0c2280647e1310bc1642182655d

# Good: justified non-canonical final base
# BASE IMAGE JUSTIFICATION: Task ships a vendor .deb linked against bookworm-slim glibc; no §2 image includes the required libGL stack.
FROM debian:bookworm-slim@sha256:<digest>

# Bad: non-canonical final base with no justification
FROM hexpm/elixir:1.16@sha256:<digest>
```

Local mirror: `scripts/run_static_checks.py --only sanctioned_base_image` (WARN when non-canonical and unjustified).

### `check_reproducible_builds`

**Severity:** Warning by default.

**What it checks:** Dockerfiles avoid nondeterministic downloads and package
installs.

```dockerfile
# Bad
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Good
ARG UV_VERSION=0.6.14
ARG UV_SHA256=<sha256>
RUN curl -fsSL "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-x86_64-unknown-linux-gnu.tar.gz" -o /tmp/uv.tar.gz \
    && echo "${UV_SHA256}  /tmp/uv.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/uv.tar.gz -C /usr/local/bin --strip-components=1 \
    && rm /tmp/uv.tar.gz
```

---

## Dockerfile layout and hygiene checks

### `check_build_context_size`

**Severity:** Blocking.

**What it checks:** The `environment/` build context stays lazy-pull friendly:
at most **100 MiB total** and at most **50 MiB per file**.

```dockerfile
# Bad
COPY huge_dataset/ /app/data/

# Good
COPY fetch_seed.py /app/fetch_seed.py
```

Keep only small required seed data in the image. Mount or fetch large optional
data at runtime only when the task design and platform allow it.

### `check_dockerignore`

**Severity:** Warning by default.

**What it checks:** Non-trivial `environment/` directories include a
`.dockerignore`.

Recommended entries:

```dockerignore
.git
**/__pycache__/
**/*.pyc
**/node_modules/
.env
solution/
tests/
```

### `check_dockerfile_hygiene`

**Severity:** Warning by default.

**What it checks:** The build context and image do not include local clutter or
secrets.

Remove or ignore:

- `environment/.git/`
- `environment/.env`
- `environment/**/__pycache__/`
- `environment/**/node_modules/`
- editor files, caches, logs, credentials, and unused build outputs

### `check_apt_usage`

**Severity:** Warning by default.

**What it checks:** Debian/Ubuntu package installation follows one clean apt
transaction per stage and avoids upgrades.

```dockerfile
# Bad
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get upgrade -y

# Good
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
```

### `check_layer_volatility`

**Severity:** Warning by default.

**What it checks:** Dockerfile layers are ordered from least volatile to most
volatile so dependency layers can be cached.

```dockerfile
# Bad
COPY . /app
RUN pip install -r /app/requirements.txt

# Good
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY src/ /app/src/
```

### `check_no_build_tools_in_runtime`

**Severity:** Warning by default.

**What it checks:** Compilers and build tools are not left in the final runtime
image unless the task explicitly requires the agent to use them.

```dockerfile
# Bad: final stage compiles and keeps build tools
RUN apt-get update && apt-get install -y build-essential
RUN make

# Good: compile in a builder, copy artifact into slim runtime
FROM rust:1.86-bookworm@sha256:<digest> AS builder
RUN cargo build --release --locked

FROM mcr.microsoft.com/devcontainers/base:bookworm@sha256:<digest>
COPY --from=builder /build/target/release/tool /usr/local/bin/tool
```

### `check_file_extraction`

**Severity:** Warning by default.

**What it checks:** Archives copied into the image are extracted and removed in
the same stage.

```dockerfile
# Bad
COPY fixtures.tar.gz /tmp/fixtures.tar.gz

# Good
COPY fixtures.tar.gz /tmp/fixtures.tar.gz
RUN mkdir -p /app/fixtures \
    && tar -xzf /tmp/fixtures.tar.gz -C /app/fixtures \
    && rm /tmp/fixtures.tar.gz
```

### `check_heredoc_usage`

**Severity:** Warning by default.

**What it checks:** Dockerfiles do not embed source files through heredocs.

```dockerfile
# Bad
RUN cat > /app/foo.py <<'EOF'
print("hello")
EOF

# Good
COPY foo.py /app/foo.py
```

### `check_recursive_permissions`

**Severity:** Warning by default.

**What it checks:** Dockerfiles avoid broad recursive metadata rewrites.

```dockerfile
# Bad
RUN chmod -R 755 /app
RUN chown -R app:app /app

# Good
COPY --chmod=0755 run.sh /usr/local/bin/run-task
COPY --chown=app:app src/ /app/src/
```

---

## Runtime and verifier checks

### `tests_or_solution_in_image`

**Severity:** Blocking.

**What it checks:** The `tests/` folder and `solution/` files are not copied
into the Docker image.

```dockerfile
# Bad
COPY tests/ /tests/
COPY solution/ /solution/
```

### `check_dockerfile_references`

**Severity:** Blocking.

**What it checks:** Dockerfiles do not reference forbidden solution or verifier
files.

Remove references such as:

- `solution/solve.sh`
- `tests/test.sh`
- `test_outputs.py`

### `check_test_sh`

**Severity:** Blocking.

**What it checks:** `tests/test.sh` runs the Python pytest verifier, produces a
reward file, and uses dependencies that were baked into the image. For
non-Python tasks, the pytest file should call the application or service under
test rather than replacing pytest with another test runner.

Platform minimum shape:

```bash
#!/bin/bash
set -uo pipefail

mkdir -p /logs/verifier

python -m pytest /tests/test_outputs.py -rA
rc=$?

if [ "$rc" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
```

**Repo overlay (Edition 2 internet-disabled template):** this repo uses the
`uvx` + pinned `-w` pytest template from `task-creation.mdc` /
`HARBOR_COMPONENTS.md`. Do **not** add `set -e` / `set -euo pipefail` on
standard tasks — it breaks reward capture. The reward `if`/`else` block is the
**canonical script end**; no trailing `exit` is required or desired. Harbor
reads `/logs/verifier/reward.txt`, not the script exit code. With
`allow_internet = false`, `test.sh` must not run runtime `apt-get`, `pip
install`, `curl`/`wget`, or `uv` bootstrap scripts.

### `check_offline_tests`

**Severity:** Warning by default.

**What it checks:** `tests/test.sh` does not install packages or download from
the network.

```bash
# Bad
pip install requests
npm install
curl https://example.com/fixture.json
git clone https://github.com/example/repo.git

# Good: dependencies are baked into the image
python -m pytest /tests/test_outputs.py -rA

# Good: local-only install from preloaded wheels
pip install --no-index -f /opt/wheels pytest==8.4.1
```

With `[environment] allow_internet = false`, offline verifier setup is **blocking**
in this repo even when platform CI only warns.

### `test_deps_in_image`

**Severity:** Blocking (repo).

**What it checks:** Verifier dependencies (`pytest`, plugins, `uv`/`uvx`) are
pre-installed in `environment/Dockerfile`, not fetched at verifier runtime.

---

## Other checks

### `typos`

**Severity:** Blocking.

**What it checks:** Spelling errors in file and variable names.

**How to fix:** Review flagged items and correct spelling.

### `ruff`

**Severity:** Blocking.

**What it checks:** Python code passes linting.

```bash
ruff check <task-folder>
ruff check --fix <task-folder>
```

### `check_canary`

**Severity:** Blocking (repo).

**What it checks:** No legacy canary strings in `instruction.md`.

---

## Quick reference table

| Check | Default severity | Validates | Common fix |
|-------|------------------|-----------|------------|
| `check_pinned_images` | **Blocks** | Every `FROM` has `@sha256` | Add digest pins |
| `check_sanctioned_base_images` | **Blocks** | Final runtime is §2 canonical TB base or justified non-canonical | See [DOCKERFILE_BEST_PRACTICES.md](DOCKERFILE_BEST_PRACTICES.md) §2 |
| `check_build_context_size` | **Blocks** | `environment/` ≤ 100 MiB total and ≤ 50 MiB per file | Remove large files or mount/fetch optional data |
| `pinned_dependencies` | **Blocks** | Language deps have exact versions | Add exact pins or lockfiles |
| `tests_or_solution_in_image` | **Blocks** | No tests/solution in Docker image | Remove forbidden `COPY` lines |
| `check_dockerfile_references` | **Blocks** | No forbidden solution/test refs | Remove references |
| `check_test_sh` | **Blocks** | Reward file written; deps in image | Always write `/logs/verifier/reward.txt`; end at reward block on standard tasks |
| `check_task_absolute_path` | **Blocks** | Instructions use absolute paths | Use `/full/path` |
| `check_privileged_containers` | **Blocks** | No privileged mode | Remove `privileged: true` and unsafe caps |
| `validate_task_fields` | **Blocks** | Required TOML fields | Add missing fields |
| `ruff` | **Blocks** | Python linting passes | Run `ruff --fix` |
| `typos` | **Blocks** | Names are spelled correctly | Correct flagged names |
| `check_task_sizes` | **Blocks** | Files stay within platform limits | Compress/remove large files |
| `check_dockerignore` | Warns | Non-trivial context has `.dockerignore` | Add ignore rules |
| `check_dockerfile_hygiene` | Warns | No context clutter or secrets | Remove or ignore clutter |
| `check_offline_tests` | Warns (blocking in repo when `allow_internet = false`) | Verifier is network-free | Bake deps into image |
| `check_apt_usage` | Warns | Apt usage is clean | One transaction, no upgrade, cleanup lists |
| `check_reproducible_builds` | Warns | Downloads are pinned and verified | Pin version and checksum |
| `check_layer_volatility` | Warns | Cache-friendly layer order | Copy manifests, install deps, then copy source |
| `check_no_build_tools_in_runtime` | Warns | Runtime image is slim | Use multi-stage builds |
| `check_file_extraction` | Warns | Archives extracted and removed | Extract and delete in same stage |
| `check_heredoc_usage` | Warns | Source files not embedded in Dockerfile | Commit files and `COPY` them |
| `check_recursive_permissions` | Warns | No broad `chmod -R` or `chown -R` | Use `COPY --chmod` / `--chown` |

## LLMaJ checks (via `harbor tasks check`)

| Check | Validates |
|-------|-----------|
| `behavior_in_task_description` | All tested behavior appears in `instruction.md` |
| `behavior_in_tests` | All instruction requirements have tests |
| `informative_test_docstrings` | Each test has a docstring |
| `anti_cheating_measures` | Task resists trivial bypass |
| `hardcoded_solution` | Oracle demonstrates process, not echo answers |
| `file_reference_mentioned` | Tested files/paths mentioned in instruction |
| `structured_data_schema` | JSON/API schemas defined when tested |

## CI iteration workflow

1. Run `harbor tasks check <task-folder> -m openai/@openai/gpt-5.6`
2. Fix **one** failure at a time using this reference
3. Re-run until CI + LLMaJ pass
4. Run oracle (`harbor run -a oracle -p …`) — must PASS
5. Confirm NOP fails (local: `harbor_gate.py --nop`)
6. Run frontier agents for difficulty calibration

Fix easy structural CI issues before LLMaJ quality issues. Read error messages — they include file, line, and fix hints.

## apt pinning note

Pin niche apt packages where versions matter. Common distro packages need not
always be pinned.

Repo-specific hardness policy: `docs/HARD_BUT_FAIR_AUTHORING.md`,
`scripts/collapse_check.py`.
