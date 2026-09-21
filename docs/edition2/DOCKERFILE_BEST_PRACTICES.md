# Dockerfile & Image Best Practices (Edition 2)

Platform mirror of the Snorkel **Dockerfile Best Practices** guide
([Terminus EC Training portal](https://snorkel-ai.github.io/Terminus-EC-Training-stateful/) → Resources → Dockerfile Best Practices).
Use [HARBOR_COMPONENTS.md](HARBOR_COMPONENTS.md) for starter Dockerfiles, compose shapes, and local build commands; use **this page** when you need to understand or fix Dockerfile CI checks.

Related: [CI_CHECKS.md](CI_CHECKS.md) (`check_pinned_images`, `check_sanctioned_base_images`, `check_build_context_size`).

## Image quality principles

All Terminal-Bench task images must be:

| Principle | Requirement |
|-----------|-------------|
| **Reproducible** | The same source builds to the same image over time and across systems |
| **Cacheable** | Common layers are shared across tasks |
| **Lazy-pull friendly** | Startup-critical files are accessible without pulling the full image |
| **Auditable** | Images are digest-pinned, signed, labeled, and free of secrets |
| **Complete** | Tasks run without network access — images must contain all required dependencies |
| **Siloed** | The image must not leak task solutions or tests |
| **Resourced** | Tasks must define CPU, memory, and storage needs in `task.toml` |

## CI enforcement summary

Three Dockerfile checks **block** by default:

| Check | What it enforces |
|-------|------------------|
| `check_pinned_images` | Every `FROM` image must be digest-pinned with `@sha256:<digest>` |
| `check_sanctioned_base_images` | The **final runtime** base must be a §2 canonical image or explicitly exempt with justification |
| `check_build_context_size` | `environment/` must be at most **100 MiB** total, with no file over **50 MiB** |

The remaining Dockerfile checks **warn** by default, but warning checks can still emit structural errors when required files such as `environment/` or `environment/Dockerfile` are missing.

Local mirrors: `scripts/run_static_checks.py --only dockerfile`, `--only build_context_size`, `--only sanctioned_base_image`.

## §1 Pin base images by digest

Every `FROM` line must use an immutable digest. Never use floating tags such as `latest`. Tags may be included for readability, but the **digest is the source of truth**. CI fails any Dockerfile with a `FROM` line lacking `@sha256`.

```dockerfile
# Bad
FROM python:3.13-slim-bookworm

# Good — use the exact digest from §2 when using a canonical base
FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb
```

Update digests deliberately, in reviewable commits.

## §2 Canonical Terminal-Bench base images

Prefer the **approved canonical images below** for the **final runtime stage** over ad hoc public images. Builder stages may use task-appropriate toolchain images, but the **final stage** is what agents and verifiers run in and is checked by CI.

**Why a canonical list:** Tasks across the dataset have been fragmenting onto many slightly different base images (different tags, registries, patch versions) for no real reason. Reusing this small set improves cache hit rates, reduces verifier startup time, and keeps the runtime surface area manageable.

**Use the exact digest-pinned reference from this table whenever possible.** Each row intentionally collapses minor version variants into one canonical entry per family (e.g., the Go row covers Go 1.21–1.26 majors and alpine/bullseye/bookworm variants — **use the canonical row**).

Short-form `library/` references (e.g. `debian:bookworm-slim@sha256:…`) are accepted when the **image:tag** and **digest** match a row below.

### Language runtimes

| Canonical `FROM` (digest-pinned) | Stack | Covers |
|----------------------------------|-------|--------|
| `public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb` | Python | Python 3.10/3.11/3.12/3.13 majors + patch + slim/non-slim |
| `public.ecr.aws/docker/library/node:22-bookworm-slim@sha256:f3a68cf41a855d227d1b0ab832bed9749469ef38cf4f58182fb8c893bc462383` | Node.js | Node 18/20/22/24 majors + slim/non-slim |
| `public.ecr.aws/docker/library/golang:1.24-bookworm@sha256:1a6d4452c65dea36aac2e2d606b01b4a029ec90cc1ae53890540ce6173ea77ac` | Go | Go 1.21–1.26 majors + alpine/bullseye/bookworm |
| `public.ecr.aws/docker/library/rust:1.85-slim@sha256:9f841bbe9e7d8e37ceb96ed907265a3a0df7f44e3737d0b100e7907a679acb36` | Rust | Rust 1.75–1.95 + slim/non-slim + bullseye |
| `public.ecr.aws/docker/library/eclipse-temurin:21-jdk-jammy@sha256:25d1276565738d3c805e632a4542c3a7598866ef967f4def6544c15de3a74b14` | Java (JDK) | Java 17/21 jdk-jammy/noble variants |
| `public.ecr.aws/docker/library/gcc:13-bookworm@sha256:930f2ebe239275fa67226654cb79273ea34eee672ae61c8a39f689c37fb7ac5c` | C / C++ (GCC) | GCC 12/13/14/15 variants |
| `public.ecr.aws/docker/library/ruby:3.3-slim-bookworm@sha256:e76733e94b3a5893e4a141024ef3a583dc10781dc24becebf74f9c9f9a33e3df` | Ruby | Ruby 3.2/3.3/3.4 + slim/non-slim |

### Build tools and SDKs

| Canonical `FROM` (digest-pinned) | Stack | Covers |
|----------------------------------|-------|--------|
| `public.ecr.aws/docker/library/maven:3.9.9-eclipse-temurin-21@sha256:3a4ab3276a087bf276f79cae96b1af04f53731bec53fb2e651aca79e4b10211e` | Maven | Maven + temurin-17/21 variants |

### Distro bases (minimal or custom images)

| Canonical `FROM` (digest-pinned) | Stack | Covers |
|----------------------------------|-------|--------|
| `public.ecr.aws/docker/library/debian:bookworm-slim@sha256:4724b8cc51e33e398f0e2e15e18d5ec2851ff0c2280647e1310bc1642182655d` | Debian | Debian bookworm/bullseye/12.x slim variants |
| `public.ecr.aws/docker/library/ubuntu:24.04@sha256:0d39fcc8335d6d74d5502f6df2d30119ff4790ebbb60b364818d5112d9e3e932` | Ubuntu | Ubuntu 22.04/24.04/jammy variants |

### Example final stage

```dockerfile
FROM public.ecr.aws/docker/library/python:3.13-slim-bookworm@sha256:01f42367a0a94ad4bc17111776fd66e3500c1d87c15bbd6055b7371d39c124fb

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    asciinema \
    tmux \
    && rm -rf /var/lib/apt/lists/*
```

Install **`tmux`** and **`asciinema`** in the final runtime image (Harbor agent runtime). Pre-install verifier tooling in the Dockerfile — no runtime `apt-get` / `pip install` / `curl` in `tests/test.sh` when `allow_internet = false`. Do not `COPY` `solution/` or `tests/` into the image.

### Using a non-canonical base image

Tasks may use a base **not** on this list when there is a genuine reason (runtime the canonical list does not cover, hardware-specific image, niche distro). Acceptance gate:

| Final base | Justification | Result |
|------------|---------------|--------|
| Canonical (§2 table) | Not required | Passes |
| Non-canonical | Present and credible (Dockerfile comment or `environment/README.md`) | Passes; surfaced to reviewers |
| Non-canonical | Empty / missing / boilerplate | **Blocked** |

**Acceptable justification examples:**

- "The canonical Java image is JDK-only; this task requires a full JRE-plus-system-libraries setup."
- "Targeting a new language not yet in the canonical list (e.g., Zig, Crystal)."
- "Stress-testing behavior specific to a Red Hat-derived distribution that Debian-derived canonical images do not reproduce."

A reviewer can reject a non-canonical base if the justification is missing, vague, or matches an existing canonical entry (the canonical image would have worked).

Add justification in **either**:

1. Dockerfile comment on or above the final runtime `FROM`:

   ```dockerfile
   # BASE IMAGE JUSTIFICATION: Final stage must ship libGL + headless Qt built against the same
   # bookworm-slim glibc as the prebuilt .deb under environment/vendor/ — no §2 image includes it.
   FROM debian:bookworm-slim@sha256:…
   ```

2. `environment/README.md` under a **Base image** heading.

**Blocked:** no comment, "custom base", "needed for task", or justification that does not explain why no §2 image fits.

Local mirror: `scripts/run_static_checks.py --only sanctioned_base_image`.

### What a good base-image family provides

- Shell utilities required by the harness (`tmux`, `asciinema`)
- Observability tooling, if required
- Standard CA certificates and locale configuration
- Common verifier/runtime bootstrap tools
- A pinned package-manager baseline

## §3 General build rules (summary)

- Build context lives only under `environment/` (≤ 100 MiB total, ≤ 50 MiB per file).
- Prefer multi-stage builds: toolchain images in builder stages; lean final runtime on a §2 canonical base.
- Pin pip/apt/npm with exact versions or lockfiles where reproducibility matters.
- Do not create or modify `/tests`, `/solution`, or `/oracle` in the image.

## §4 Difficulty benchmark models

Empirical difficulty uses **Claude Opus 5** and **GPT-5.6** (previously Opus 4.8 and GPT-5.5). EASY/MEDIUM/HARD thresholds are unchanged; stronger models may shift labels — calibrate to these two. See [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) and `@difficulty-calibration.mdc` Part E.
