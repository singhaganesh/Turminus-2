# Video-Processing / Media-Output Failure Patterns — Terminal-Bench 2.1 Corpus Study

Source: `terminal-bench-2-1/tasks/`. Only **one** task is officially
`category = "video-processing"` (`video-processing` — hurdle-jump frame
extraction, hard). One task cannot establish a pattern, so this study widens to
the **media-output** cohort: every task whose *graded artifact* is a frame,
image, video, or mask compared perceptually — regardless of its category label.
That cohort (7 tasks) is where the video-processing failure signature actually
lives, because the grading machinery is the same.

Read: each task's `instruction.md` + `task.toml` + the grading assertions in
`tests/`. This is a static content study, not a fresh rollout — difficulty is the
author-assigned `task.toml` field. Use it to calibrate *how* media tasks are made
hard, not as proof a given task resolves <1/3.

## The media-output cohort (graded artifact + metric)

| Task | Category (label) | Difficulty | Graded artifact | Tolerance metric |
|---|---|---|---|---|
| `video-processing` | video-processing | hard | takeoff/landing frame index | **inclusive frame range** (±) |
| `path-tracing` | software-engineering | hard | rendered `.ppm` image | **L2 / cosine similarity ≥ 0.99** |
| `make-doom-for-mips` | software-engineering | hard | rendered `frame.bmp` | **L2 similarity to reference.jpg** + liveness |
| `make-mips-interpreter` | software-engineering | hard | rendered `frame.bmp` | **L2 similarity to reference.jpg** + liveness |
| `build-pov-ray` | software-engineering | medium | rendered image | **SSIM > 0.87** |
| `sam-cell-seg` | data-science | hard | segmentation mask | **IoU ≥ 0.5** |
| `extract-moves-from-video` | file-operations | hard | text from video (OCR) | **edit-distance similarity ≥ 90%** |

**The single unanimous fact: not one media-output task grades byte-exact.** Every
one uses a quantitative tolerance metric (frame range, L2/cosine, SSIM, IoU,
edit-distance %). This is the empirical basis for our `false_failure_lint` INVERSE
rule and `idea-validation.mdc` #26 — byte-exact on media is not just discouraged,
it is *absent* from the reference corpus because it would be a false failure.

## The five failure-pattern families

### 1. Tolerance-threshold grading on a held-out input (the core signature)

The defining media pattern: grading is a **quantitative threshold** on an input
the agent cannot tune to. `video-processing` provides an example video but grades
a **held-out test video**; `path-tracing` explicitly forbids reading the target
image (`image.c` must not read `image.ppm`) and grades L2 ≥ 0.99 against it;
`build-pov-ray` renders and compares SSIM > 0.87 against a reference the agent
doesn't get to inspect pixel-by-pixel.

**Why frontier models fail it:** "looks approximately right" is not enough — the
output must clear a hard numeric bar on unseen input. A solution tuned to the
visible example (a threshold calibrated to `example_video.mp4`, an image that
matches the one visible view) lands *near* the bar and fails. This is the
**unfakeable conformance discriminator** (our SE depth-test point 3) realized as a
perceptual metric: the held-out media input plus the metric threshold together do
the discriminating.

**Authoring takeaway:** always split example (visible) vs test (grade-time-only)
media, and state the exact metric + threshold in the instruction. The threshold
choice IS the difficulty dial — too loose and a naive impl passes; too tight and
it becomes a false failure. `build-pov-ray` (SSIM > 0.87, medium) vs `path-tracing`
(L2 ≥ 0.99, hard) shows the dial in action.

### 2. Derive-the-generator, no data embedding (size budget on media)

`path-tracing` (image.c < 2KB gzipped), `path-tracing-reverse` (< 2KB gzipped),
`make-mips-interpreter` / `make-doom-for-mips` (must actually run the ISA/renderer,
not stub a frame).

**Why frontier models fail it:** the model's instinct — embed or approximate the
target image/frame data — is blocked by a size ceiling (path-tracing) or by the
grading requiring a real rendered frame from a real running engine (doom/mips).
The model must implement the *generating algorithm* (the path tracer, the MIPS
CPU) whose output happens to match perceptually. Same size-budget lever as the SE
study family 1, here producing a perceptual artifact.

### 3. Liveness / timing — the artifact comes from a running process

`make-doom-for-mips` and `make-mips-interpreter` grade by **polling for
`/tmp/frame.bmp` to appear within a timeout**, then check content. The media
artifact is emitted by a live process (an emulator running DOOM), not written once.

**Why frontier models fail it:** it is not enough to produce correct code — the
process must actually boot, run far enough to render, and emit the frame within
the time budget. A build that compiles but hangs, renders too slowly, or crashes
before the first frame fails on liveness before content is even checked. This is a
media-specific facet absent from pure-function SE tasks: **the output has to
appear, on time, from a running system.**

**Authoring takeaway:** for pipeline/render/stream tasks, grade
appearance-within-timeout AND content — and pin the environment so timing is
deterministic (a slow decode shouldn't flakily miss the window; that would be a
false failure). Keep the timeout generous relative to the pinned image's real
speed.

### 4. Perceptual robustness to noise the example doesn't show

`video-processing` (background/camera fixed, but real clips carry lighting and
compression variance a naive frame-difference threshold mistakes for the event),
`sam-cell-seg` (segmentation must generalize across cell images, IoU ≥ 0.5), and
by construction any held-out-video task.

**Why frontier models fail it:** the naive detector (absolute frame diff over a
constant threshold; a fixed intensity cut for segmentation) fires on flicker /
compression artifacts / illumination change and fails the held-out input whose
noise straddles the naive threshold. Correctness needs a noise-robust criterion
(persistent normalized-histogram change, adaptive thresholding) that generalizes.
This is our `naive-passes` cap tag made concrete: a first-pass CV script passes
the calm example and fails the noisy held-out clip.

### 5. Metric-mismatch — optimizing the wrong quantity

Across the cohort the model can produce a *plausible* artifact that misses the
*graded* quantity: a rendered image that looks right but scores L2 0.95 (below
0.99); a detected frame that is close but outside the ±range; a mask that covers
the cell but scores IoU 0.4. The instruction states the metric, but the model
optimizes visual plausibility instead of the stated metric.

**Why frontier models fail it:** perceptual "good enough" ≠ the stated numeric
bar. The gap between "produces an image/frame/mask" and "clears the exact metric
threshold" is where these tasks live, and read-only reasoning cannot confirm the
score — the model must actually run and measure against the metric.

## Cross-cutting observations

- **All media-output tasks are `constrained_build` shape** (or reverse-engineering
  for `path-tracing-reverse`) — no hidden defect, full spec stated, hardness from
  building an artifact that clears a perceptual threshold on unseen input. This
  confirms video-processing correctly inherits our SE / constrained_build branch;
  it needs no new depth test, only the media grading law (#26) and the
  `media_conformance` floor class.
- **The metric is chosen to match the artifact:** frame index → inclusive range;
  rendered image → L2/cosine or SSIM; segmentation → IoU; text-from-media →
  edit-distance %. An author must pick the right metric for the output type; the
  wrong metric is either gameable (too loose) or a false failure (too tight /
  byte-exact).
- **Difficulty tracks the threshold + the input hold-out, not the domain nouns.**
  `build-pov-ray` (SSIM > 0.87) is medium; `path-tracing` (L2 ≥ 0.99, no data
  embedding, held-out target) is hard. Same "render an image, compare to
  reference" family; the tighter threshold + size budget + hold-out make one hard.
- **Liveness/timing is the one media-specific facet with no SE analog** — pin the
  environment and set a generous, deterministic timeout, or the task false-fails
  on decode/render speed variance rather than on correctness.

## Mapping to our engine

| Media family | Engine lever it validates | Authoring action |
|---|---|---|
| 1. Tolerance-threshold on held-out input | `idea-validation.mdc` #26 (state tolerance); `media_conformance` floor class; held-out discriminator | State the metric + threshold; split example vs grade-time test media; tune the threshold as the difficulty dial. |
| 2. Derive-the-generator / size budget | SE depth-test point 1 (naive impl fails) | Add a size/no-embedding constraint so the target artifact can't be embedded — forces the real generating algorithm. |
| 3. Liveness / timing | new media-specific facet | Grade appearance-within-timeout AND content; pin the base image for deterministic timing; generous timeout (R8 must hold). |
| 4. Perceptual robustness | `naive-passes` cap tag; SE point 3 | Give held-out media with noise (flicker/compression/lighting) the example lacks, so a naive threshold fails. |
| 5. Metric-mismatch | false-failure firewall + ALT probe | Grade the STATED metric only; confirm a genuinely different correct artifact (ALT probe, reward 1) still clears it. |

## Standing caveat

Officially **n=1** for `video-processing`; this pattern is generalized from the
7-task media-output cohort across categories. It is a static read of
instructions + tests + author-assigned difficulty, not a fresh frontier rollout —
use it to calibrate which mechanisms make media tasks hard, not as proof any
specific task resolves <1/3. The one true `video-processing` anchor
(`video-processing`, frame-range tolerance, held-out test video) is the
calibration point; treat all media verdicts `confidence: low|med` until more are
measured.
