#!/usr/bin/env python3
"""Generate split-subsystem Java sources for bandit-sliding-regret-desk."""

from pathlib import Path

ENV = Path("tasks/bandit-sliding-regret-desk/environment")

FILES = {
    "r3k/RoundUtil.java": "package r3k;\npublic final class RoundUtil { public static double round6(double v){return Math.round(v*1_000_000.0)/1_000_000.0;} }\n",
    "r3k/ArmState.java": """
package r3k;
import java.util.*;
public final class ArmState {
  public final Deque<Double> window = new ArrayDeque<>();
  public final List<Double> all = new ArrayList<>();
  public void push(double reward, int w) { all.add(reward); window.addLast(reward); while (window.size() > w) window.removeFirst(); }
  public double meanWindow() { if (window.isEmpty()) return 0.0; double s=0; for (double v: window) s+=v; return s/window.size(); }
  public double meanAll() { if (all.isEmpty()) return 0.0; double s=0; for (double v: all) s+=v; return s/all.size(); }
  public int windowCount() { return window.size(); }
}
""",
    "r3k/WindowStats.java": """
package r3k;
import java.util.*;
public final class WindowStats {
  private final Map<String, ArmState> arms = new HashMap<>();
  public void observe(String arm, double reward, int w) { arms.computeIfAbsent(arm, k -> new ArmState()).push(reward, w); }
  public double meanFor(String arm) { ArmState st = arms.get(arm); return st == null ? 0.0 : st.meanWindow(); }
  public int countFor(String arm) { ArmState st = arms.get(arm); if (st == null) return 1; int c = st.windowCount(); return c == 0 ? 1 : c; }
  public double starMean(List<String> armIds) {
    double best = -1.0;
    for (String id : armIds) { ArmState st = arms.get(id); double m = st == null ? 0.0 : st.meanAll(); if (m > best) best = m; }
    return best < 0 ? 0.0 : best;
  }
}
""",
    "r3k/UcbScorer.java": """
package r3k;
import java.util.*;
public final class UcbScorer {
  public static Map<String, Double> score(WindowStats stats, List<String> arms, int priorT, int totalPulls) {
    int pt = Math.max(priorT, 1);
    int denomBase = Math.max(totalPulls, 1);
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
""",
    "t7n/RegretCalc.java": """
package t7n;
import java.util.List;
import r3k.RoundUtil;
import r3k.WindowStats;
public final class RegretCalc {
  public static double increment(WindowStats stats, List<String> arms, double reward) {
    return RoundUtil.round6(stats.starMean(arms) - reward);
  }
}
""",
    "w8v/RoundRecord.java": "package w8v; public final class RoundRecord { public final int round; public final String arm; public final double reward; public RoundRecord(int r,String a,double w){round=r;arm=a;reward=w;} }\n",
    "w8v/PullLog.java": """
package w8v;
import java.io.IOException;
import java.nio.file.*;
import java.util.*;
public final class PullLog {
  public final List<RoundRecord> rounds = new ArrayList<>();
  public static PullLog loadNdjson(Path path) throws IOException {
    PullLog log = new PullLog();
    for (String line : Files.readAllLines(path)) {
      if (line.isBlank()) continue;
      String body = line.trim();
      int rIdx = body.indexOf("\"round\":");
      int aIdx = body.indexOf("\"arm\":");
      int wIdx = body.indexOf("\"reward\":");
      int round = Integer.parseInt(body.substring(rIdx + 8, body.indexOf(',', rIdx)).trim());
      String arm = body.substring(body.indexOf('"', aIdx + 6) + 1, body.indexOf('"', body.indexOf('"', aIdx + 6) + 1));
      double reward = Double.parseDouble(body.substring(wIdx + 9).trim().replaceAll("[^0-9.\\-]", ""));
      log.rounds.add(new RoundRecord(round, arm, reward));
    }
    return log;
  }
}
""",
    "w8v/PathUtil.java": "package w8v; import java.nio.file.Path; public final class PathUtil { public static Path root(String f,String id){return Path.of(f,id,\"pulls.ndjson\");} }\n",
    "w8v/ManifestLoader.java": """
package w8v; import java.nio.file.*; import java.util.*; import java.io.IOException;
public final class ManifestLoader {
  public static List<String> load(Path manifest) throws IOException {
    List<String> ids = new ArrayList<>();
    for (String line : Files.readAllLines(manifest)) if (!line.isBlank()) ids.add(line.trim());
    Collections.sort(ids); return ids;
  }
}
""",
    "w8v/ExperimentSummary.java": """
package w8v; import java.util.*;
public final class ExperimentSummary {
  public final double totalRegret; public final String bestFixed; public final int pullCount;
  public ExperimentSummary(double t,String b,int p){totalRegret=t;bestFixed=b;pullCount=p;}
  public static ExperimentSummary fromPulls(List<RoundRecord> rounds, List<String> arms) {
    Map<String, Double> totals = new HashMap<>();
    for (String a : arms) totals.put(a, 0.0);
    for (RoundRecord r : rounds) totals.put(r.arm, totals.get(r.arm) + r.reward);
    double best = -1.0; String bestArm = arms.get(0);
    for (String a : arms) { double v = totals.get(a); if (v > best || (Math.abs(v-best)<1e-9 && a.compareTo(bestArm)<0)) { best=v; bestArm=a; } }
    return new ExperimentSummary(0.0, bestArm, rounds.size());
  }
}
""",
    "w8v/RoundView.java": "package w8v; import java.util.Map; public final class RoundView { public final int round; public final String chosenArm; public final double reward; public final Map<String,Double> ucbScores; public final double cumulativeRegret; public RoundView(int r,String a,double w,Map<String,Double> s,double c){round=r;chosenArm=a;reward=w;ucbScores=s;cumulativeRegret=c;} }\n",
    "w8v/ExperimentResult.java": "package w8v; import java.util.*; public final class ExperimentResult { public final String experimentId; public final int window; public final List<String> arms; public final List<RoundView> rounds = new ArrayList<>(); public ExperimentSummary summary; public ExperimentResult(String id,int w,List<String> a){experimentId=id;window=w;arms=a;} }\n",
    "w8v/ExperimentRunner.java": """
package w8v;
import java.io.IOException; import java.nio.file.Path; import java.util.*;
import r3k.RoundUtil; import r3k.UcbScorer; import r3k.WindowStats; import t7n.RegretCalc;
public final class ExperimentRunner {
  static final Map<String, WindowStats> SHARED = new HashMap<>();
  private static final int WINDOW = 3;
  public static ExperimentResult run(String expId, Path pullPath, List<String> arms) throws IOException {
    PullLog log = PullLog.loadNdjson(pullPath);
    WindowStats stats = SHARED.computeIfAbsent("global", k -> new WindowStats());
    ExperimentResult result = new ExperimentResult(expId, WINDOW, new ArrayList<>(arms));
    double regret = 0.0;
    for (RoundRecord rec : log.rounds) {
      stats.observe(rec.arm, rec.reward, WINDOW);
      Map<String, Double> scores = UcbScorer.score(stats, arms, rec.round - 1, log.rounds.size());
      regret += RegretCalc.increment(stats, arms, rec.reward);
      result.rounds.add(new RoundView(rec.round, rec.arm, rec.reward, scores, RoundUtil.round6(regret)));
    }
    ExperimentSummary base = ExperimentSummary.fromPulls(log.rounds, arms);
    result.summary = new ExperimentSummary(RoundUtil.round6(regret), base.bestFixed, base.pullCount);
    return result;
  }
}
""",
    "w8v/JsonEscaper.java": """
package w8v;
public final class JsonEscaper {
  public static String esc(String s) {
    StringBuilder b = new StringBuilder("\"");
    for (int i = 0; i < s.length(); i++) { char c = s.charAt(i); if (c=='\\'||c=='"') b.append('\\').append(c); else b.append(c); }
    return b.append('"').toString();
  }
}
""",
    "w8v/ReportWriter.java": """
package w8v; import java.nio.file.*; import java.util.*; import java.io.IOException;
public final class ReportWriter {
  public static void write(Path out, List<ExperimentResult> experiments, String chain, int count) throws IOException {
    StringBuilder b = new StringBuilder();
    b.append("{\"schema\":\"pull.roll.v1\",\"experiments\":[");
    for (int i = 0; i < experiments.size(); i++) {
      if (i > 0) b.append(',');
      ExperimentResult exp = experiments.get(i);
      b.append('{').append("\"experiment_id\":").append(JsonEscaper.esc(exp.experimentId)).append(',')
       .append("\"window\":").append(exp.window).append(',')
       .append("\"arms\":[");
      for (int j=0;j<exp.arms.size();j++){ if(j>0)b.append(','); b.append(JsonEscaper.esc(exp.arms.get(j))); }
      b.append("],\"rounds\":[");
      for (int j=0;j<exp.rounds.size();j++){
        if(j>0)b.append(','); RoundView rv=exp.rounds.get(j);
        b.append('{').append("\"round\":").append(rv.round).append(',')
         .append("\"chosen_arm\":").append(JsonEscaper.esc(rv.chosenArm)).append(',')
         .append("\"reward\":").append(rv.reward).append(',')
         .append("\"ucb_scores\":{");
        int k=0; for (var e: rv.ucbScores.entrySet()){ if(k++>0)b.append(','); b.append(JsonEscaper.esc(e.getKey())).append(':').append(e.getValue()); }
        b.append("},\"cumulative_regret\":").append(rv.cumulativeRegret).append('}');
      }
      b.append("],\"summary\":{")
       .append("\"total_regret\":").append(exp.summary.totalRegret).append(',')
       .append("\"best_fixed_arm\":").append(JsonEscaper.esc(exp.summary.bestFixed)).append(',')
       .append("\"pull_count\":").append(exp.summary.pullCount).append("}}");
    }
    b.append("],\"audit\":{\"chain_digest\":").append(JsonEscaper.esc(chain)).append(",\"experiment_count\":").append(count).append("}}");
    Files.writeString(out, b.toString());
  }
}
""",
    "w8v/Main.java": """
package w8v; import java.nio.file.*; import java.util.*; import q2m.DigestFold;
public final class Main {
  public static void main(String[] args) throws Exception {
    String manifest=null, fixtures=null, out=null;
    for (int i=0;i<args.length;i++) {
      if ("--manifest".equals(args[i]) && i+1<args.length) manifest=args[++i];
      else if ("--fixtures".equals(args[i]) && i+1<args.length) fixtures=args[++i];
      else if ("--out".equals(args[i]) && i+1<args.length) out=args[++i];
    }
    if (manifest==null||fixtures==null||out==null) { System.err.println("missing argv"); System.exit(2); }
    List<ExperimentResult> rows = new ArrayList<>();
    for (String id : ManifestLoader.load(Path.of(manifest))) {
      PullLog log = PullLog.loadNdjson(PathUtil.root(fixtures, id));
      Set<String> arms = new HashSet<>(); for (RoundRecord r : log.rounds) arms.add(r.arm);
      List<String> armList = new ArrayList<>(arms); Collections.sort(armList);
      rows.add(ExperimentRunner.run(id, PathUtil.root(fixtures, id), armList));
    }
    rows.sort(Comparator.comparing(a -> a.experimentId));
    ReportWriter.write(Path.of(out), rows, DigestFold.chain(rows), rows.size());
  }
}
""",
    "q2m/DigestFold.java": """
package q2m; import java.nio.charset.StandardCharsets; import java.security.MessageDigest; import java.util.*; import w8v.ExperimentResult;
public final class DigestFold {
  public static String chain(List<ExperimentResult> rows) {
    StringBuilder b = new StringBuilder();
    for (ExperimentResult row : rows) b.append(row.experimentId).append(':').append(row.summary.totalRegret).append(':').append(row.summary.bestFixed).append('\n');
    try { MessageDigest md = MessageDigest.getInstance("SHA-256"); return HexFormat.of().formatHex(md.digest(b.toString().getBytes(StandardCharsets.UTF_8))).substring(0,8); }
    catch (Exception ex) { throw new RuntimeException(ex); }
  }
}
""",
}

import shutil
for old in ["src", "r3k", "t7n", "w8v", "q2m"]:
    p = ENV / old
    if p.exists() and old == "src":
        shutil.rmtree(p)

for rel, body in FILES.items():
    path = ENV / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.strip() + "\n", encoding="utf-8")

(ENV / "compile.sh").write_text(
    "#!/bin/bash\nset -euo pipefail\ncd /app/environment\nmkdir -p bin\n"
    "(find r3k t7n w8v q2m -name '*.java' > sources.txt)\n"
    "javac -d bin @sources.txt\n",
    encoding="utf-8",
)
(ENV / "ops" / "pull-roll").write_text(
    "#!/bin/bash\nset -euo pipefail\nbash /app/environment/compile.sh\nexec java -cp /app/environment/bin w8v.Main \"$@\"\n",
    encoding="utf-8",
)
policy = ENV / "spec/policy_notes.md"
policy.write_text(policy.read_text(encoding="utf-8") + "\nUse standard math.sqrt and math.log for ln in reference implementations.\n", encoding="utf-8")
print("done", len(FILES))
