#!/usr/bin/env python3
"""Bootstrap bandit-sliding-regret-desk environment, solution, and tests."""

from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "tasks" / "bandit-sliding-regret-desk"
ENV = TASK / "environment"

WINDOW = 3

FIXTURES = {
    "exp_aurora": {
        "arms": ["alpha", "beta", "gamma"],
        "pulls": [
            ("alpha", 0.20),
            ("beta", 0.80),
            ("gamma", 0.10),
            ("alpha", 0.25),
            ("beta", 0.70),
            ("gamma", 0.90),
            ("alpha", 0.15),
            ("beta", 0.60),
        ],
    },
    "exp_boreal": {
        "arms": ["north", "south"],
        "pulls": [
            ("north", 0.40),
            ("south", 0.55),
            ("north", 0.35),
            ("south", 0.50),
            ("north", 0.45),
            ("south", 0.65),
        ],
    },
    "exp_coral": {
        "arms": ["one", "two", "three"],
        "pulls": [
            ("one", 0.30),
            ("two", 0.50),
            ("three", 0.20),
            ("two", 0.55),
            ("one", 0.25),
        ],
    },
}


def round6(x: float) -> float:
    return round(x + 0.0, 6)


def window_rewards(history: list[tuple[str, float]], arm: str, w: int) -> list[float]:
    vals = [r for a, r in history if a == arm]
    return vals[-w:] if len(vals) > w else vals


def ucb_scores(
    arms: list[str], history: list[tuple[str, float]], prior_t: int, w: int
) -> dict[str, float]:
    pt = max(prior_t, 1)
    out: dict[str, float] = {}
    for arm in arms:
        wr = window_rewards(history, arm, w)
        mean = sum(wr) / len(wr) if wr else 0.0
        n_i = len(wr) if wr else 1
        bonus = math.sqrt(2.0 * math.log(pt) / n_i)
        out[arm] = round6(mean + bonus)
    return out


def pick_arm(scores: dict[str, float]) -> str:
    best = max(scores.values())
    cands = sorted(a for a, v in scores.items() if abs(v - best) < 1e-9)
    return cands[0]


def mu_star(pulls: list[tuple[str, float]], arms: list[str]) -> float:
    means = []
    for arm in arms:
        vals = [r for a, r in pulls if a == arm]
        if vals:
            means.append(sum(vals) / len(vals))
    return max(means) if means else 0.0


def best_fixed_arm(pulls: list[tuple[str, float]], arms: list[str]) -> str:
    totals: dict[str, float] = {a: 0.0 for a in arms}
    for arm, reward in pulls:
        totals[arm] += reward
    best = max(totals.values())
    return sorted(a for a, v in totals.items() if abs(v - best) < 1e-9)[0]


def oracle_experiment(exp_id: str, meta: dict) -> dict:
    arms = meta["arms"]
    pulls = meta["pulls"]
    history: list[tuple[str, float]] = []
    rounds = []
    regret = 0.0
    star = mu_star(pulls, arms)
    for idx, (arm, reward) in enumerate(pulls, start=1):
        prior = idx - 1
        scores = ucb_scores(arms, history, prior, WINDOW)
        regret += round6(star - reward)
        rounds.append(
            {
                "round": idx,
                "chosen_arm": arm,
                "reward": reward,
                "ucb_scores": scores,
                "cumulative_regret": round6(regret),
            }
        )
        history.append((arm, reward))
    return {
        "experiment_id": exp_id,
        "window": WINDOW,
        "arms": arms,
        "rounds": rounds,
        "summary": {
            "total_regret": round6(regret),
            "best_fixed_arm": best_fixed_arm(pulls, arms),
            "pull_count": len(pulls),
        },
    }


def oracle_ledger() -> dict:
    exps = [oracle_experiment(eid, FIXTURES[eid]) for eid in sorted(FIXTURES)]
    lines = [
        f"{e['experiment_id']}:{e['summary']['total_regret']}:{e['summary']['best_fixed_arm']}\n"
        for e in sorted(exps, key=lambda x: x["experiment_id"])
    ]
    import hashlib

    chain = hashlib.sha256("".join(lines).encode()).hexdigest()[:8]
    return {
        "schema": "bandit.regret.v1",
        "experiments": exps,
        "audit": {"chain_digest": chain, "experiment_count": len(exps)},
    }


def write_fixtures() -> None:
    for exp_id, meta in FIXTURES.items():
        d = ENV / "fixtures" / exp_id
        d.mkdir(parents=True, exist_ok=True)
        lines = []
        for rnd, (arm, reward) in enumerate(meta["pulls"], start=1):
            lines.append(
                json.dumps(
                    {
                        "experiment_id": exp_id,
                        "round": rnd,
                        "arm": arm,
                        "reward": reward,
                    },
                    separators=(",", ":"),
                )
            )
        (d / "pulls.ndjson").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_specs(ledger: dict) -> None:
    spec = ENV / "spec"
    spec.mkdir(parents=True, exist_ok=True)
    (spec / "run_argv.txt").write_text(
        "/app/environment/ops/regret-pass "
        "--manifest /app/environment/spec/experiments.txt "
        "--fixtures /app/environment/fixtures "
        "--out /app/output/regret_ledger.json\n",
        encoding="utf-8",
    )
    (spec / "experiments.txt").write_text(
        "\n".join(sorted(FIXTURES)) + "\n", encoding="utf-8"
    )
    (spec / "ledger_contract.md").write_text(
        textwrap.dedent(
            """\
            # Regret ledger export contract

            Output path: `/app/output/regret_ledger.json`

            Top-level object:
            - `schema` must be the literal string `bandit.regret.v1`
            - `experiments` is an array sorted by ascending `experiment_id`
            - `audit` object with `chain_digest` (8 lowercase hex chars) and `experiment_count`

            Each experiment object:
            - `experiment_id` string
            - `window` integer window size (3 for packaged fixtures)
            - `arms` array of arm ids sorted ascending
            - `rounds` array ordered by ascending `round`
            - `summary` with `total_regret`, `best_fixed_arm`, `pull_count`

            Each round object:
            - `round` 1-based index
            - `chosen_arm` string
            - `reward` number
            - `ucb_scores` object mapping every arm id to a number rounded to 6 decimal places
            - `cumulative_regret` number rounded to 6 decimal places

            `best_fixed_arm` is the arm with highest total reward sum in that experiment; ties break lexicographically smallest arm id.

            Numbers in JSON use plain decimal notation without exponents.
            """
        ),
        encoding="utf-8",
    )
    (spec / "ucb_notes.md").write_text(
        textwrap.dedent(
            f"""\
            # Sliding-window UCB replay notes

            Window size W = {WINDOW} for packaged fixtures.

            Replay each experiment independently using only pulls from that experiment's NDJSON log.

            Before round t (1-based), let `prior_t = t - 1` and consider only pulls from earlier rounds in the same experiment.

            For each arm i, gather rewards from the last min(W, total pulls of i) times arm i was chosen in that experiment (excluding the current round). Let `mean_i` be their average, or 0 when empty. Let `n_i` be the count of those rewards, or 1 when empty.

            UCB score: `mean_i + sqrt(2 * ln(max(prior_t, 1)) / n_i)`, rounded to 6 decimal places.

            Tie-break when choosing arms: lexicographically smallest arm id among max UCB.

            Hindsight star mean `mu_star` is the maximum per-arm mean reward computed over the full experiment log (each arm's total reward divided by its pull count).

            Per-round regret increment is `mu_star - reward` for the logged pull. `cumulative_regret` after round t is the sum of increments through t, rounded to 6 decimal places.

            `chain_digest` is the first 8 hex chars of SHA-256 over UTF-8 lines sorted by `experiment_id`:
            `experiment_id:total_regret:best_fixed_arm` plus newline, using the summary values as emitted.
            """
        ),
        encoding="utf-8",
    )


def java_sources() -> None:
    src = ENV / "src" / "bandit" / "ledger"
    src.mkdir(parents=True, exist_ok=True)

    files = {
        "JsonEscaper.java": r'''
package bandit.ledger;
public final class JsonEscaper {
  private JsonEscaper() {}
  public static String esc(String s) {
    StringBuilder b = new StringBuilder();
    b.append('"');
    for (int i = 0; i < s.length(); i++) {
      char c = s.charAt(i);
      if (c == '\\' || c == '"') b.append('\\').append(c);
      else if (c < 32) b.append(String.format("\\u%04x", (int) c));
      else b.append(c);
    }
    b.append('"');
    return b.toString();
  }
}
''',
        "PathUtil.java": r'''
package bandit.ledger;
import java.nio.file.Path;
public final class PathUtil {
  private PathUtil() {}
  public static Path root(String fixtures, String expId) {
    return Path.of(fixtures, expId, "pulls.ndjson");
  }
}
''',
        "PullLog.java": r'''
package bandit.ledger;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
public final class PullLog {
  public final String experimentId;
  public final List<RoundRecord> rounds = new ArrayList<>();
  public PullLog(String experimentId) { this.experimentId = experimentId; }
  public static PullLog load(Path path, String experimentId) throws IOException {
    PullLog log = new PullLog(experimentId);
    for (String line : Files.readAllLines(path)) {
      if (line.isBlank()) continue;
      String[] parts = line.split("\\|", -1);
      if (parts.length != 4) throw new IOException("bad pull row");
      int round = Integer.parseInt(parts[0]);
      String arm = parts[1];
      double reward = Double.parseDouble(parts[2]);
      log.rounds.add(new RoundRecord(round, arm, reward));
    }
    return log;
  }
  public static PullLog loadNdjson(Path path, String experimentId) throws IOException {
    PullLog log = new PullLog(experimentId);
    for (String line : Files.readAllLines(path)) {
      if (line.isBlank()) continue;
      String body = line.trim();
      int rIdx = body.indexOf("\"round\":");
      int aIdx = body.indexOf("\"arm\":");
      int wIdx = body.indexOf("\"reward\":");
      int round = Integer.parseInt(body.substring(rIdx + 8, body.indexOf(',', rIdx)).trim());
      String arm = body.substring(body.indexOf('"', aIdx + 6) + 1, body.indexOf('"', body.indexOf('"', aIdx + 6) + 1));
      String tail = body.substring(wIdx + 9).trim();
      double reward = Double.parseDouble(tail.replaceAll("[^0-9.\\-]", ""));
      log.rounds.add(new RoundRecord(round, arm, reward));
    }
    return log;
  }
}
''',
        "RoundRecord.java": r'''
package bandit.ledger;
public final class RoundRecord {
  public final int round;
  public final String arm;
  public final double reward;
  public RoundRecord(int round, String arm, double reward) {
    this.round = round; this.arm = arm; this.reward = reward;
  }
}
''',
        "ArmState.java": r'''
package bandit.ledger;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
public final class ArmState {
  public final Deque<Double> window = new ArrayDeque<>();
  public final List<Double> all = new ArrayList<>();
  public void push(double reward, int w) {
    all.add(reward);
    window.addLast(reward);
    while (window.size() > w) window.removeFirst();
  }
  public double meanWindow() {
    if (window.isEmpty()) return 0.0;
    double s = 0.0;
    for (double v : window) s += v;
    return s / window.size();
  }
  public double meanAll() {
    if (all.isEmpty()) return 0.0;
    double s = 0.0;
    for (double v : all) s += v;
    return s / all.size();
  }
  public int windowCount() { return window.size(); }
}
''',
        "WindowStats.java": r'''
package bandit.ledger;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
public final class WindowStats {
  private final Map<String, ArmState> arms = new HashMap<>();
  public void observe(String arm, double reward, int w) {
    arms.computeIfAbsent(arm, k -> new ArmState()).push(reward, w);
  }
  public double meanFor(String arm) {
    ArmState st = arms.get(arm);
    return st == null ? 0.0 : st.meanWindow();
  }
  public int countFor(String arm) {
    ArmState st = arms.get(arm);
    if (st == null) return 1;
    int c = st.windowCount();
    return c == 0 ? 1 : c;
  }
  public double starMean(List<String> armIds) {
    double best = -1.0;
    for (String id : armIds) {
      ArmState st = arms.get(id);
      double m = st == null ? 0.0 : st.meanAll();
      if (m > best) best = m;
    }
    return best < 0 ? 0.0 : best;
  }
}
''',
        "UcbScorer.java": r'''
package bandit.ledger;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
public final class UcbScorer {
  public static Map<String, Double> score(WindowStats stats, List<String> arms, int priorT, int totalPulls) {
    int pt = Math.max(priorT, 1);
    double denomBase = Math.max(totalPulls, 1);
    Map<String, Double> out = new LinkedHashMap<>();
    for (String arm : arms) {
      double mean = stats.meanFor(arm);
      int n = denomBase;
      double bonus = Math.sqrt(2.0 * Math.log(pt) / n);
      out.put(arm, RoundUtil.round6(mean + bonus));
    }
    return out;
  }
}
''',
        "RoundUtil.java": r'''
package bandit.ledger;
public final class RoundUtil {
  private RoundUtil() {}
  public static double round6(double v) {
    return Math.round(v * 1_000_000.0) / 1_000_000.0;
  }
}
''',
        "RegretCalc.java": r'''
package bandit.ledger;
import java.util.List;
public final class RegretCalc {
  public static double increment(WindowStats stats, List<String> arms, double reward) {
    double star = stats.starMean(arms);
    return RoundUtil.round6(star - reward);
  }
}
''',
        "ExperimentSummary.java": r'''
package bandit.ledger;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
public final class ExperimentSummary {
  public final double totalRegret;
  public final String bestFixed;
  public final int pullCount;
  public ExperimentSummary(double totalRegret, String bestFixed, int pullCount) {
    this.totalRegret = totalRegret;
    this.bestFixed = bestFixed;
    this.pullCount = pullCount;
  }
  public static ExperimentSummary fromPulls(List<RoundRecord> rounds, List<String> arms) {
    Map<String, Double> totals = new HashMap<>();
    for (String a : arms) totals.put(a, 0.0);
    for (RoundRecord r : rounds) totals.put(r.arm, totals.get(r.arm) + r.reward);
    double best = -1.0;
    String bestArm = arms.get(0);
    for (String a : arms) {
      double v = totals.get(a);
      if (v > best || (Math.abs(v - best) < 1e-9 && a.compareTo(bestArm) < 0)) {
        best = v; bestArm = a;
      }
    }
    return new ExperimentSummary(0.0, bestArm, rounds.size());
  }
}
''',
        "DigestFold.java": r'''
package bandit.ledger;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.List;
public final class DigestFold {
  public static String chain(List<ExperimentResult> rows) {
    StringBuilder b = new StringBuilder();
    for (ExperimentResult row : rows) {
      b.append(row.experimentId).append(':')
          .append(row.summary.totalRegret).append(':')
          .append(row.summary.bestFixed).append('\n');
    }
    try {
      MessageDigest md = MessageDigest.getInstance("SHA-256");
      byte[] dig = md.digest(b.toString().getBytes(StandardCharsets.UTF_8));
      return HexFormat.of().formatHex(dig).substring(0, 8);
    } catch (Exception ex) {
      throw new RuntimeException(ex);
    }
  }
}
''',
        "ExperimentResult.java": r'''
package bandit.ledger;
import java.util.ArrayList;
import java.util.List;
public final class ExperimentResult {
  public final String experimentId;
  public final int window;
  public final List<String> arms;
  public final List<RoundView> rounds = new ArrayList<>();
  public ExperimentSummary summary;
  public ExperimentResult(String experimentId, int window, List<String> arms) {
    this.experimentId = experimentId;
    this.window = window;
    this.arms = arms;
  }
}
''',
        "RoundView.java": r'''
package bandit.ledger;
import java.util.Map;
public final class RoundView {
  public final int round;
  public final String chosenArm;
  public final double reward;
  public final Map<String, Double> ucbScores;
  public final double cumulativeRegret;
  public RoundView(int round, String chosenArm, double reward, Map<String, Double> ucbScores, double cumulativeRegret) {
    this.round = round;
    this.chosenArm = chosenArm;
    this.reward = reward;
    this.ucbScores = ucbScores;
    this.cumulativeRegret = cumulativeRegret;
  }
}
''',
        "ManifestLoader.java": r'''
package bandit.ledger;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
public final class ManifestLoader {
  public static List<String> load(Path manifest) throws IOException {
    List<String> ids = new ArrayList<>();
    for (String line : Files.readAllLines(manifest)) {
      if (!line.isBlank()) ids.add(line.trim());
    }
    Collections.sort(ids);
    return ids;
  }
}
''',
        "ReportWriter.java": r'''
package bandit.ledger;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
public final class ReportWriter {
  public static void write(Path out, List<ExperimentResult> experiments, String chain, int count) throws IOException {
    StringBuilder b = new StringBuilder();
    b.append("{\"schema\":\"bandit.regret.v1\",\"experiments\":[");
    for (int i = 0; i < experiments.size(); i++) {
      if (i > 0) b.append(',');
      b.append(renderExperiment(experiments.get(i)));
    }
    b.append("],\"audit\":{\"chain_digest\":").append(JsonEscaper.esc(chain))
        .append(",\"experiment_count\":").append(count).append("}}");
    Files.writeString(out, b.toString());
  }
  private static String renderExperiment(ExperimentResult exp) {
    StringBuilder b = new StringBuilder();
    b.append('{');
    b.append("\"experiment_id\":").append(JsonEscaper.esc(exp.experimentId)).append(',');
    b.append("\"window\":").append(exp.window).append(',');
    b.append("\"arms\":[");
    for (int i = 0; i < exp.arms.size(); i++) {
      if (i > 0) b.append(',');
      b.append(JsonEscaper.esc(exp.arms.get(i)));
    }
    b.append("],\"rounds\":[");
    for (int i = 0; i < exp.rounds.size(); i++) {
      if (i > 0) b.append(',');
      RoundView rv = exp.rounds.get(i);
      b.append('{');
      b.append("\"round\":").append(rv.round).append(',');
      b.append("\"chosen_arm\":").append(JsonEscaper.esc(rv.chosenArm)).append(',');
      b.append("\"reward\":").append(rv.reward).append(',');
      b.append("\"ucb_scores\":").append(renderScores(rv.ucbScores)).append(',');
      b.append("\"cumulative_regret\":").append(rv.cumulativeRegret);
      b.append('}');
    }
    b.append("],\"summary\":{");
    b.append("\"total_regret\":").append(exp.summary.totalRegret).append(',');
    b.append("\"best_fixed_arm\":").append(JsonEscaper.esc(exp.summary.bestFixed)).append(',');
    b.append("\"pull_count\":").append(exp.summary.pullCount);
    b.append("}}");
    return b.toString();
  }
  private static String renderScores(Map<String, Double> scores) {
    StringBuilder b = new StringBuilder("{");
    int i = 0;
    for (Map.Entry<String, Double> e : scores.entrySet()) {
      if (i++ > 0) b.append(',');
      b.append(JsonEscaper.esc(e.getKey())).append(':').append(e.getValue());
    }
    b.append('}');
    return b.toString();
  }
}
''',
        "ExperimentRunner.java": r'''
package bandit.ledger;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
public final class ExperimentRunner {
  static final Map<String, WindowStats> SHARED = new HashMap<>();
  private static final int WINDOW = 3;
  public static ExperimentResult run(String expId, Path pullPath, List<String> arms) throws IOException {
    PullLog log = PullLog.loadNdjson(pullPath, expId);
    WindowStats stats = SHARED.computeIfAbsent("global", k -> new WindowStats());
    ExperimentResult result = new ExperimentResult(expId, WINDOW, new ArrayList<>(arms));
    double regret = 0.0;
    for (RoundRecord rec : log.rounds) {
      stats.observe(rec.arm, rec.reward, WINDOW);
      int prior = rec.round - 1;
      Map<String, Double> scores = UcbScorer.score(stats, arms, prior, log.rounds.size());
      regret += RegretCalc.increment(stats, arms, rec.reward);
      result.rounds.add(new RoundView(rec.round, rec.arm, rec.reward, scores, RoundUtil.round6(regret)));
    }
    ExperimentSummary base = ExperimentSummary.fromPulls(log.rounds, arms);
    result.summary = new ExperimentSummary(RoundUtil.round6(regret), base.bestFixed, base.pullCount);
    return result;
  }
}
''',
        "Main.java": r'''
package bandit.ledger;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
public final class Main {
  public static void main(String[] args) throws Exception {
    String manifest = null;
    String fixtures = null;
    String out = null;
    for (int i = 0; i < args.length; i++) {
      if ("--manifest".equals(args[i]) && i + 1 < args.length) manifest = args[++i];
      else if ("--fixtures".equals(args[i]) && i + 1 < args.length) fixtures = args[++i];
      else if ("--out".equals(args[i]) && i + 1 < args.length) out = args[++i];
    }
    if (manifest == null || fixtures == null || out == null) {
      System.err.println("missing argv");
      System.exit(2);
    }
    List<String> ids = ManifestLoader.load(Path.of(manifest));
    List<ExperimentResult> rows = new ArrayList<>();
    Set<String> armCatalog = new HashSet<>();
    for (String id : ids) {
      PullLog log = PullLog.loadNdjson(PathUtil.root(fixtures, id), id);
      Set<String> arms = new HashSet<>();
      for (RoundRecord r : log.rounds) arms.add(r.arm);
      List<String> armList = new ArrayList<>(arms);
      java.util.Collections.sort(armList);
      armCatalog.addAll(armList);
      rows.add(ExperimentRunner.run(id, PathUtil.root(fixtures, id), armList));
    }
    java.util.Collections.sort(rows, (a, b) -> a.experimentId.compareTo(b.experimentId));
    String chain = DigestFold.chain(rows);
    ReportWriter.write(Path.of(out), rows, chain, rows.size());
  }
}
''',
    }

    for name, body in files.items():
        (src / name).write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")


def write_support_files() -> None:
    (ENV / "compile.sh").write_text(
        "#!/bin/bash\nset -euo pipefail\ncd /app/environment\nmkdir -p bin\n"
        "find src -name '*.java' > sources.txt\n"
        "javac -d bin @sources.txt\n",
        encoding="utf-8",
    )
    ops = ENV / "ops"
    ops.mkdir(parents=True, exist_ok=True)
    (ops / "regret-pass").write_text(
        "#!/bin/bash\nset -euo pipefail\n"
        "bash /app/environment/compile.sh\n"
        "exec java -cp /app/environment/bin bandit.ledger.Main \"$@\"\n",
        encoding="utf-8",
    )
    tools = ENV / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    (tools / "ledger_smoke.sh").write_text(
        "#!/bin/bash\n# quick compile smoke for local desks\n"
        "bash /app/environment/compile.sh\n",
        encoding="utf-8",
    )
    docs = ENV / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "stack_brief.md").write_text(
        "Java replay desk for offline sliding-window bandit logs. Sources live under `src/bandit/ledger`.\n",
        encoding="utf-8",
    )
    (ENV / ".dockerignore").write_text(
        "solution/\ntests/\n.git\n__pycache__/\n*.pyc\nnode_modules/\n",
        encoding="utf-8",
    )
    (ENV / "Dockerfile").write_text(
        textwrap.dedent(
            """\
            FROM public.ecr.aws/docker/library/eclipse-temurin:21-jdk-jammy@sha256:25d1276565738d3c805e632a4542c3a7598866ef967f4def6544c15de3a74b14

            ENV DEBIAN_FRONTEND=noninteractive

            RUN apt-get update && apt-get install -y --no-install-recommends \\
                asciinema=2.1.0-1 \\
                ca-certificates=20230311ubuntu0.22.04.1 \\
                curl=7.81.0-1ubuntu1.21 \\
                python3=3.10.6-1~22.04.1 \\
                tmux=3.2a-4ubuntu0.2 \\
                && rm -rf /var/lib/apt/lists/*

            RUN curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh \\
                && /root/.local/bin/uv venv /opt/verifier-venv --python 3.13 \\
                && /root/.local/bin/uv pip install --python=/opt/verifier-venv/bin/python \\
                   iniconfig==2.3.0 \\
                   packaging==26.2 \\
                   pluggy==1.6.0 \\
                   Pygments==2.20.0 \\
                   pytest==8.4.1 \\
                   pytest-json-ctrf==0.3.5

            ENV PATH="/opt/verifier-venv/bin:/root/.local/bin:${PATH}"

            WORKDIR /app
            COPY spec /app/environment/spec
            COPY fixtures /app/environment/fixtures
            COPY src /app/environment/src
            COPY ops /app/environment/ops
            COPY tools /app/environment/tools
            COPY docs /app/environment/docs
            COPY compile.sh /app/environment/compile.sh
            RUN chmod +x /app/environment/compile.sh /app/environment/ops/regret-pass /app/environment/tools/ledger_smoke.sh \\
                && bash /app/environment/compile.sh \\
                && mkdir -p /app/output

            CMD ["bash"]
            """
        ),
        encoding="utf-8",
    )


def write_solution() -> None:
    sol = TASK / "solution" / "solve.sh"
    sol.parent.mkdir(parents=True, exist_ok=True)
    sol.write_text(
        textwrap.dedent(
            r'''#!/bin/bash
set -euo pipefail

log() { printf '[solve] %s\n' "$1"; }

log "patch WindowStats to exclude lookahead pulls"
cat > /app/environment/src/bandit/ledger/WindowStats.java <<'JAVA'
package bandit.ledger;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
public final class WindowStats {
  private final Map<String, ArmState> arms = new HashMap<>();
  public void observe(String arm, double reward, int w) {
    arms.computeIfAbsent(arm, k -> new ArmState()).push(reward, w);
  }
  public double meanFor(String arm) {
    ArmState st = arms.get(arm);
    return st == null ? 0.0 : st.meanWindow();
  }
  public int countFor(String arm) {
    ArmState st = arms.get(arm);
    if (st == null) return 1;
    int c = st.windowCount();
    return c == 0 ? 1 : c;
  }
  public double starMean(List<String> armIds, List<RoundRecord> allRounds) {
    double best = -1.0;
    for (String id : armIds) {
      double sum = 0.0;
      int cnt = 0;
      for (RoundRecord r : allRounds) {
        if (r.arm.equals(id)) { sum += r.reward; cnt++; }
      }
      if (cnt == 0) continue;
      double m = sum / cnt;
      if (m > best) best = m;
    }
    return best < 0 ? 0.0 : best;
  }
}
JAVA

log "patch UcbScorer per-arm window denominator"
cat > /app/environment/src/bandit/ledger/UcbScorer.java <<'JAVA'
package bandit.ledger;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
public final class UcbScorer {
  public static Map<String, Double> score(WindowStats stats, List<String> arms, int priorT) {
    int pt = Math.max(priorT, 1);
    Map<String, Double> out = new LinkedHashMap<>();
    for (String arm : arms) {
      double mean = stats.meanFor(arm);
      int n = stats.countFor(arm);
      double bonus = Math.sqrt(2.0 * Math.log(pt) / n);
      out.put(arm, RoundUtil.round6(mean + bonus));
    }
    return out;
  }
}
JAVA

log "patch RegretCalc to use full-log hindsight star mean"
cat > /app/environment/src/bandit/ledger/RegretCalc.java <<'JAVA'
package bandit.ledger;
import java.util.List;
public final class RegretCalc {
  public static double increment(WindowStats stats, List<String> arms, List<RoundRecord> all, double reward) {
    double star = stats.starMean(arms, all);
    return RoundUtil.round6(star - reward);
  }
}
JAVA

log "patch ExperimentRunner for per-experiment isolation and pre-observe scoring"
cat > /app/environment/src/bandit/ledger/ExperimentRunner.java <<'JAVA'
package bandit.ledger;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
public final class ExperimentRunner {
  private static final int WINDOW = 3;
  public static ExperimentResult run(String expId, Path pullPath, List<String> arms) throws IOException {
    PullLog log = PullLog.loadNdjson(pullPath, expId);
    WindowStats stats = new WindowStats();
    ExperimentResult result = new ExperimentResult(expId, WINDOW, new ArrayList<>(arms));
    double regret = 0.0;
    for (RoundRecord rec : log.rounds) {
      int prior = rec.round - 1;
      Map<String, Double> scores = UcbScorer.score(stats, arms, prior);
      regret += RegretCalc.increment(stats, arms, log.rounds, rec.reward);
      result.rounds.add(new RoundView(rec.round, rec.arm, rec.reward, scores, RoundUtil.round6(regret)));
      stats.observe(rec.arm, rec.reward, WINDOW);
    }
    ExperimentSummary base = ExperimentSummary.fromPulls(log.rounds, arms);
    result.summary = new ExperimentSummary(RoundUtil.round6(regret), base.bestFixed, base.pullCount);
    return result;
  }
}
JAVA

log "patch DigestFold to sort experiment ids before hashing"
cat > /app/environment/src/bandit/ledger/DigestFold.java <<'JAVA'
package bandit.ledger;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
public final class DigestFold {
  public static String chain(List<ExperimentResult> rows) {
    List<ExperimentResult> sorted = new ArrayList<>(rows);
    sorted.sort((a, b) -> a.experimentId.compareTo(b.experimentId));
    StringBuilder b = new StringBuilder();
    for (ExperimentResult row : sorted) {
      b.append(row.experimentId).append(':')
          .append(row.summary.totalRegret).append(':')
          .append(row.summary.bestFixed).append('\n');
    }
    try {
      MessageDigest md = MessageDigest.getInstance("SHA-256");
      byte[] dig = md.digest(b.toString().getBytes(StandardCharsets.UTF_8));
      return HexFormat.of().formatHex(dig).substring(0, 8);
    } catch (Exception ex) {
      throw new RuntimeException(ex);
    }
  }
}
JAVA

log "recompile and regenerate ledger"
bash /app/environment/compile.sh
rm -f /app/output/regret_ledger.json
/app/environment/ops/regret-pass \
  --manifest /app/environment/spec/experiments.txt \
  --fixtures /app/environment/fixtures \
  --out /app/output/regret_ledger.json

log "done"
'''
        ),
        encoding="utf-8",
    )


def write_tests(ledger: dict) -> None:
    tests = TASK / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    (tests / "test.sh").write_text(
        textwrap.dedent(
            """\
            #!/bin/bash

            if [ "$PWD" = "/" ]; then
                echo "Error: No working directory set. Please set a WORKDIR in your Dockerfile."
                exit 1
            fi

            pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA
            rc=$?

            if [ "$rc" -eq 0 ]; then
              echo 1 > /logs/verifier/reward.txt
            else
              echo 0 > /logs/verifier/reward.txt
            fi
            """
        ),
        encoding="utf-8",
    )

    test_py = textwrap.dedent(
        '''\
        """Sliding-window bandit regret ledger verifier."""

        from __future__ import annotations

        import hashlib
        import json
        import math
        import subprocess
        from contextlib import contextmanager
        from pathlib import Path

        APP = Path("/app")
        ENV = APP / "environment"
        OUT = APP / "output/regret_ledger.json"
        MANIFEST = ENV / "spec/experiments.txt"
        FIXTURES = ENV / "fixtures"
        OPS = ENV / "ops/regret-pass"
        WINDOW = 3

        FIXTURE_META = '''
    )
    test_py += json.dumps(FIXTURES, indent=8)
    test_py += textwrap.dedent(
        '''

        RUNNER = ENV / "src/bandit/ledger/ExperimentRunner.java"
        SCORER = ENV / "src/bandit/ledger/UcbScorer.java"
        WINDOW_SRC = ENV / "src/bandit/ledger/WindowStats.java"
        REGRET = ENV / "src/bandit/ledger/RegretCalc.java"
        DIGEST = ENV / "src/bandit/ledger/DigestFold.java"


        def read_text(path: Path) -> str:
            return path.read_text(encoding="utf-8")


        def round6(x: float) -> float:
            return round(x + 0.0, 6)


        def window_rewards(history, arm, w):
            vals = [r for a, r in history if a == arm]
            return vals[-w:] if len(vals) > w else vals


        def ucb_scores(arms, history, prior_t, w):
            pt = max(prior_t, 1)
            out = {}
            for arm in arms:
                wr = window_rewards(history, arm, w)
                mean = sum(wr) / len(wr) if wr else 0.0
                n_i = len(wr) if wr else 1
                bonus = math.sqrt(2.0 * math.log(pt) / n_i)
                out[arm] = round6(mean + bonus)
            return out


        def mu_star(pulls, arms):
            means = []
            for arm in arms:
                vals = [r for a, r in pulls if a == arm]
                if vals:
                    means.append(sum(vals) / len(vals))
            return max(means) if means else 0.0


        def best_fixed_arm(pulls, arms):
            totals = {a: 0.0 for a in arms}
            for arm, reward in pulls:
                totals[arm] += reward
            best = max(totals.values())
            return sorted(a for a, v in totals.items() if abs(v - best) < 1e-9)[0]


        def oracle_experiment(exp_id: str, meta: dict) -> dict:
            arms = meta["arms"]
            pulls = meta["pulls"]
            history = []
            rounds = []
            regret = 0.0
            star = mu_star(pulls, arms)
            for idx, (arm, reward) in enumerate(pulls, start=1):
                scores = ucb_scores(arms, history, idx - 1, WINDOW)
                regret += round6(star - reward)
                rounds.append(
                    {
                        "round": idx,
                        "chosen_arm": arm,
                        "reward": reward,
                        "ucb_scores": scores,
                        "cumulative_regret": round6(regret),
                    }
                )
                history.append((arm, reward))
            return {
                "experiment_id": exp_id,
                "window": WINDOW,
                "arms": arms,
                "rounds": rounds,
                "summary": {
                    "total_regret": round6(regret),
                    "best_fixed_arm": best_fixed_arm(pulls, arms),
                    "pull_count": len(pulls),
                },
            }


        def oracle_ledger() -> dict:
            exps = [oracle_experiment(eid, FIXTURE_META[eid]) for eid in sorted(FIXTURE_META)]
            lines = [
                f"{e['experiment_id']}:{e['summary']['total_regret']}:{e['summary']['best_fixed_arm']}\\n"
                for e in sorted(exps, key=lambda x: x["experiment_id"])
            ]
            chain = hashlib.sha256("".join(lines).encode()).hexdigest()[:8]
            return {
                "schema": "bandit.regret.v1",
                "experiments": exps,
                "audit": {"chain_digest": chain, "experiment_count": len(exps)},
            }


        def run_driver(expect_ok: bool = True) -> subprocess.CompletedProcess:
            subprocess.run(["bash", str(ENV / "compile.sh")], check=True)
            OUT.unlink(missing_ok=True)
            proc = subprocess.run(
                [
                    str(OPS),
                    "--manifest",
                    str(MANIFEST),
                    "--fixtures",
                    str(FIXTURES),
                    "--out",
                    str(OUT),
                ]
            )
            if expect_ok:
                assert proc.returncode == 0, proc.returncode
            return proc


        @contextmanager
        def patched(path: Path, marker: str, replacement: str):
            original = read_text(path)
            if marker not in original:
                raise AssertionError(f"missing marker in {path}")
            path.write_text(original.replace(marker, replacement, 1), encoding="utf-8")
            try:
                yield
            finally:
                path.write_text(original, encoding="utf-8")


        class TestBanditRegretLedger:
            def test_driver_regenerates_ledger(self):
                """Published regret-pass command recreates the JSON ledger."""
                run_driver()
                assert OUT.is_file()
                doc = json.loads(read_text(OUT))
                assert doc["schema"] == "bandit.regret.v1"

            def test_experiment_order_and_window(self):
                """Experiments are sorted by id and carry window size three."""
                run_driver()
                doc = json.loads(read_text(OUT))
                ids = [row["experiment_id"] for row in doc["experiments"]]
                assert ids == sorted(ids)
                assert all(row["window"] == WINDOW for row in doc["experiments"])

            def test_ucb_scores_match_sliding_window_policy(self):
                """Per-round ucb_scores follow the documented sliding-window formula."""
                run_driver()
                got = json.loads(read_text(OUT))
                exp = oracle_ledger()
                for grow, erow in zip(got["experiments"], exp["experiments"], strict=True):
                    for gr, er in zip(grow["rounds"], erow["rounds"], strict=True):
                        assert gr["ucb_scores"] == er["ucb_scores"]

            def test_cumulative_regret_tracks_hindsight_star(self):
                """cumulative_regret sums mu_star minus reward using full-log means."""
                run_driver()
                got = json.loads(read_text(OUT))
                exp = oracle_ledger()
                for grow, erow in zip(got["experiments"], exp["experiments"], strict=True):
                    for gr, er in zip(grow["rounds"], erow["rounds"], strict=True):
                        assert gr["cumulative_regret"] == er["cumulative_regret"]
                    assert grow["summary"]["total_regret"] == erow["summary"]["total_regret"]

            def test_best_fixed_arm_totals(self):
                """summary.best_fixed_arm picks highest total reward with lex tie-break."""
                run_driver()
                got = json.loads(read_text(OUT))
                exp = oracle_ledger()
                for grow, erow in zip(got["experiments"], exp["experiments"], strict=True):
                    assert grow["summary"]["best_fixed_arm"] == erow["summary"]["best_fixed_arm"]
                    assert grow["summary"]["pull_count"] == erow["summary"]["pull_count"]

            def test_audit_chain_digest(self):
                """audit.chain_digest matches sorted experiment summary fold."""
                run_driver()
                got = json.loads(read_text(OUT))
                exp = oracle_ledger()
                assert got["audit"]["chain_digest"] == exp["audit"]["chain_digest"]
                assert got["audit"]["experiment_count"] == exp["audit"]["experiment_count"]

            def test_experiment_isolation_on_fresh_cohort(self):
                """A synthetic experiment does not inherit arm windows from packaged logs."""
                synth = {
                    "arms": ["east", "west"],
                    "pulls": [("east", 0.10), ("west", 0.90), ("east", 0.12)],
                }
                exp_id = "exp_synth"
                d = FIXTURES / exp_id
                d.mkdir(exist_ok=True)
                lines = [
                    json.dumps(
                        {
                            "experiment_id": exp_id,
                            "round": i,
                            "arm": arm,
                            "reward": reward,
                        },
                        separators=(",", ":"),
                    )
                    for i, (arm, reward) in enumerate(synth["pulls"], start=1)
                ]
                pull_file = d / "pulls.ndjson"
                manifest_backup = read_text(MANIFEST)
                pull_backup = pull_file.read_text(encoding="utf-8") if pull_file.exists() else None
                try:
                    pull_file.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
                    MANIFEST.write_text(exp_id + "\\n", encoding="utf-8")
                    run_driver()
                    got = json.loads(read_text(OUT))["experiments"][0]
                    exp = oracle_experiment(exp_id, synth)
                    assert got["rounds"][2]["ucb_scores"] == exp["rounds"][2]["ucb_scores"]
                finally:
                    MANIFEST.write_text(manifest_backup, encoding="utf-8")
                    if pull_backup is None:
                        pull_file.unlink(missing_ok=True)
                        d.rmdir()
                    else:
                        pull_file.write_text(pull_backup, encoding="utf-8")

            def test_partial_revert_ucb_denominator_flips_round_scores(self):
                """Reverting per-arm UCB denominators changes ucb_scores on graded rounds."""
                run_driver()
                baseline = json.loads(read_text(OUT))
                marker = "int n = stats.countFor(arm);"
                bad = "int n = Math.max(priorT + arms.size(), 1);"
                with patched(SCORER, marker, bad):
                    run_driver()
                    regressed = json.loads(read_text(OUT))
                assert baseline != regressed
                assert (
                    baseline["experiments"][0]["rounds"][4]["ucb_scores"]
                    != regressed["experiments"][0]["rounds"][4]["ucb_scores"]
                )

            def test_partial_revert_shared_stats_flips_isolation(self):
                """Reverting per-experiment stats changes synthetic cohort ucb_scores."""
                synth = {
                    "arms": ["east", "west"],
                    "pulls": [("east", 0.10), ("west", 0.90), ("east", 0.12)],
                }
                exp_id = "exp_synth"
                d = FIXTURES / exp_id
                d.mkdir(exist_ok=True)
                lines = [
                    json.dumps(
                        {
                            "experiment_id": exp_id,
                            "round": i,
                            "arm": arm,
                            "reward": reward,
                        },
                        separators=(",", ":"),
                    )
                    for i, (arm, reward) in enumerate(synth["pulls"], start=1)
                ]
                pull_file = d / "pulls.ndjson"
                manifest_backup = read_text(MANIFEST)
                pull_backup = pull_file.read_text(encoding="utf-8") if pull_file.exists() else None
                marker = "WindowStats stats = new WindowStats();"
                bad = "WindowStats stats = ExperimentRunner.SHARED.computeIfAbsent(\\"global\\", k -> new WindowStats());"
                try:
                    pull_file.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
                    MANIFEST.write_text(exp_id + "\\n", encoding="utf-8")
                    run_driver()
                    good = json.loads(read_text(OUT))["experiments"][0]["rounds"][2]["ucb_scores"]
                    with patched(RUNNER, marker, bad):
                        run_driver()
                        bad_doc = json.loads(read_text(OUT))["experiments"][0]["rounds"][2]["ucb_scores"]
                    assert good != bad_doc
                finally:
                    MANIFEST.write_text(manifest_backup, encoding="utf-8")
                    if pull_backup is None:
                        pull_file.unlink(missing_ok=True)
                        d.rmdir()
                    else:
                        pull_file.write_text(pull_backup, encoding="utf-8")

            def test_partial_revert_digest_sort_flips_audit(self):
                """Reverting sorted digest fold changes audit.chain_digest."""
                run_driver()
                good = json.loads(read_text(OUT))["audit"]["chain_digest"]
                marker = "sorted.sort((a, b) -> a.experimentId.compareTo(b.experimentId));"
                bad = "// sorted.sort"
                with patched(DIGEST, marker, bad):
                    run_driver()
                    bad_digest = json.loads(read_text(OUT))["audit"]["chain_digest"]
                assert good != bad_digest
        '''
    )
    (tests / "test_outputs.py").write_text(test_py, encoding="utf-8")


def write_spec(ledger: dict) -> None:
    spec_path = ROOT / "specs" / "bandit-sliding-regret-desk.md"
    spec_path.write_text(
        textwrap.dedent(
            f"""\
            ### Decision

            GO — Attempt 1. Java sliding-window UCB bandit regret replay under machine-learning; multi-module frontier across per-arm denominators, hindsight regret star means, experiment isolation, and sorted digest folding.

            ### Metadata

            - version: 2
            - Task name: bandit-sliding-regret-desk
            - Title: Sliding-window bandit regret ledger
            - Category: machine-learning
            - Task shape: repair_existing_system
            - Languages: [java, bash]
            - Difficulty: hard
            - Codebase size: small
            - Subcategories: [tool_specific]
            - Tags: [sliding-window-ucb, bandit-regret, java-replay, offline-rl, experiment-isolation]
            - Milestones: 0

            ## Authoring Brief

            ### Public contract

            Offline bandit replay memo. Packaged pull logs feed the Java desk at `/app/environment/ops/regret-pass` which must regenerate `/app/output/regret_ledger.json` per `/app/environment/spec/run_argv.txt`. UCB scores, cumulative regret, experiment isolation, and audit chain_digest drift until Java sources under `/app/environment/src` are corrected. Static JSON is insufficient when graded runs delete output and rerun the entrypoint.

            ### Triviality avoidance ledger

            - Hand-written ledger JSON — graded runs delete output and invoke regret-pass; tests compare against independent Python UCB oracle.
            - Single-module clip tweak — partial revert tests on UcbScorer, ExperimentRunner, and DigestFold flip distinct round fields.
            - Fixture memorization — synthetic exp_synth cohort generated at test time checks isolation without packaged answers.
            - Shared static stats shortcut — isolation partial revert proves cross-experiment contamination is caught.
            - Digest-only patch — chain_digest partial revert fails while per-round scores would still pass.

            ### Per-gate pitfall inventory

            - run_static_checks — instruction documents schema, UCB formula, regret rule, digest fold; no verifier wording in instruction.md.
            - collapse_check — opaque Java package names; instruction avoids fix-path symbol stems; four distributed frontiers.
            - oracle 10x — deterministic compile and replay; no randomness or network.
            - NOP — missing output and wrong UCB/regret values fail independent oracle comparisons.

            ### Initial draft commitments

            - task.toml — metadata without reference_pattern block per submission policy.
            - instruction.md — concise bandit replay memo with contract doc pointers.
            - environment Java desk — replay pipeline with four intentional defect frontiers.
            - tests/test_outputs.py — independent sliding-window UCB oracle with partial reverts.
            - solution/solve.sh — substantive multi-file Java patches then regret-pass regeneration.

            ### category_profile

            - profile_name: ml_adversarial_robustness
            - challenge_family: offline bandit policy replay audit

            ### reference_pattern

            - justification_if_none: No promoted reference covers sliding-window UCB regret replay with per-experiment isolation and sorted audit digest folding.

            Expected chain_digest for packaged fixtures: {ledger['audit']['chain_digest']}
            """
        ),
        encoding="utf-8",
    )


def main() -> None:
    ledger = oracle_ledger()
    write_fixtures()
    write_specs(ledger)
    java_sources()
    write_support_files()
    write_solution()
    write_tests(ledger)
    write_spec(ledger)
    print("bootstrap complete", ledger["audit"]["chain_digest"])


if __name__ == "__main__":
    main()
