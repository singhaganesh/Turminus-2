import java.nio.file.*;
import java.util.*;

public class Drive {
  static Path ROOT = Paths.get("/app/corpus");
  static Path BLOT = Paths.get("/app/blot");
  static Path LAST = BLOT.resolve("last.json");
  static Path CACHE = BLOT.resolve("cache.json");
  static Path FLOOR = Paths.get("/app/hopnotes/FLOOR.txt");

  static int floor() {
    try {
      return Integer.parseInt(Files.readString(FLOOR).trim());
    } catch (Exception e) {
      return 1;
    }
  }

  static Map<String, Set<String>> importers(LinkedHashMap<String, Loom.Unit> all) {
    Map<String, Set<String>> bait = Scan.edges(all);
    try {
      Files.createDirectories(BLOT);
      StringBuilder b = new StringBuilder();
      b.append("{");
      boolean first = true;
      for (Map.Entry<String, Set<String>> e : bait.entrySet()) {
        if (!first) b.append(',');
        first = false;
        b.append(Bag.q(e.getKey())).append(":[").append(Bag.joinComma(e.getValue())).append(']');
      }
      b.append("}");
      Files.writeString(BLOT.resolve("scan.json"), b.toString());
    } catch (Exception e) {
    }
    Map<String, Set<String>> m = new LinkedHashMap<String, Set<String>>();
    for (Loom.Unit u : all.values()) {
      for (String dep : u.importedUnits) {
        if (!m.containsKey(dep)) m.put(dep, new LinkedHashSet<String>());
        m.get(dep).add(u.path);
      }
    }
    return m;
  }

  static LinkedHashSet<String> known(LinkedHashMap<String, Loom.Unit> all) {
    LinkedHashSet<String> k = new LinkedHashSet<String>();
    for (Loom.Unit u : all.values()) k.addAll(u.defined);
    return k;
  }

  static Map<String, String> fps(LinkedHashMap<String, Loom.Unit> all) {
    Map<String, String> m = new LinkedHashMap<String, String>();
    for (Loom.Unit u : all.values()) m.putAll(u.fps);
    return m;
  }

  static Map<String, String> loadOldFp() {
    Map<String, String> m = new LinkedHashMap<String, String>();
    Map<String, Set<String>> cites = loadCites();
    try {
      if (!Files.exists(CACHE)) return m;
      String s = Files.readString(CACHE);
      int i = s.indexOf("\"fps\"");
      if (i < 0) return m;
      int brace = s.indexOf('{', i);
      int end = s.indexOf('}', brace);
      if (brace < 0 || end < 0) return m;
      String inner = s.substring(brace + 1, end);
      for (String part : inner.split(",")) {
        if (!part.contains(":")) continue;
        String[] kv = part.split(":", 2);
        String k = kv[0].replace("\"", "").trim();
        String v = kv[1].replace("\"", "").trim();
        if (!k.isEmpty()) m.put(k, v);
      }
    } catch (Exception e) {
    }
    return m;
  }

  static Map<String, Set<String>> loadCites() {
    Map<String, Set<String>> m = new LinkedHashMap<String, Set<String>>();
    try {
      if (!Files.exists(CACHE)) return m;
      String s = Files.readString(CACHE);
      int i = s.indexOf("\"cites\"");
      if (i < 0) return m;
      int brace = s.indexOf('{', i);
      int end = matching(s, brace);
      if (brace < 0 || end < 0) return m;
      String inner = s.substring(brace + 1, end);
      parseMapOfSets(inner, m);
    } catch (Exception e) {
    }
    return m;
  }

  static int matching(String s, int open) {
    int d = 0;
    for (int i = open; i < s.length(); i++) {
      char c = s.charAt(i);
      if (c == '{') d++;
      else if (c == '}') {
        d--;
        if (d == 0) return i;
      }
    }
    return -1;
  }

  static void parseMapOfSets(String inner, Map<String, Set<String>> m) {
    int i = 0;
    while (i < inner.length()) {
      int q1 = inner.indexOf('"', i);
      if (q1 < 0) break;
      int q2 = inner.indexOf('"', q1 + 1);
      String key = inner.substring(q1 + 1, q2);
      int lb = inner.indexOf('[', q2);
      int rb = inner.indexOf(']', lb);
      if (lb < 0 || rb < 0) break;
      LinkedHashSet<String> set = new LinkedHashSet<String>();
      String arr = inner.substring(lb + 1, rb);
      int j = 0;
      while (j < arr.length()) {
        int a = arr.indexOf('"', j);
        if (a < 0) break;
        int b = arr.indexOf('"', a + 1);
        set.add(arr.substring(a + 1, b));
        j = b + 1;
      }
      m.put(key, set);
      i = rb + 1;
    }
  }

  static LinkedHashSet<String> hashChanged(LinkedHashMap<String, Loom.Unit> all, Map<String, String> oldHash) {
    LinkedHashSet<String> s = new LinkedHashSet<String>();
    for (Loom.Unit u : all.values()) {
      String oh = oldHash.get(u.path);
      if (oh == null || !oh.equals(u.hash)) s.add(u.path);
    }
    return s;
  }

  static Map<String, String> loadOldHash() {
    Map<String, String> m = new LinkedHashMap<String, String>();
    try {
      if (!Files.exists(CACHE)) return m;
      String s = Files.readString(CACHE);
      int i = s.indexOf("\"hash\"");
      if (i < 0) return m;
      int brace = s.indexOf('{', i);
      int end = matching(s, brace);
      if (brace < 0 || end < 0) return m;
      String inner = s.substring(brace + 1, end);
      int j = 0;
      while (j < inner.length()) {
        int q1 = inner.indexOf('"', j);
        if (q1 < 0) break;
        int q2 = inner.indexOf('"', q1 + 1);
        int q3 = inner.indexOf('"', q2 + 1);
        int q4 = inner.indexOf('"', q3 + 1);
        if (q3 < 0 || q4 < 0) break;
        m.put(inner.substring(q1 + 1, q2), inner.substring(q3 + 1, q4));
        j = q4 + 1;
      }
    } catch (Exception e) {
    }
    return m;
  }

  static void writeCache(LinkedHashMap<String, Loom.Unit> all, Map<String, Set<String>> cites) throws Exception {
    Files.createDirectories(BLOT);
    StringBuilder b = new StringBuilder();
    b.append("{");
    b.append("\"hash\":{");
    boolean first = true;
    for (Loom.Unit u : all.values()) {
      if (!first) b.append(',');
      first = false;
      b.append(Bag.q(u.path)).append(':').append(Bag.q(u.hash));
    }
    b.append("},\"fps\":{");
    first = true;
    for (Loom.Unit u : all.values()) {
      for (Map.Entry<String, String> e : u.fps.entrySet()) {
        if (!first) b.append(',');
        first = false;
        b.append(Bag.q(e.getKey())).append(':').append(Bag.q(e.getValue()));
      }
    }
    b.append("},\"cites\":{");
    first = true;
    for (Map.Entry<String, Set<String>> e : cites.entrySet()) {
      if (!first) b.append(',');
      first = false;
      b.append(Bag.q(e.getKey())).append(":[").append(Bag.joinComma(e.getValue())).append(']');
    }
    b.append("}}");
    Files.writeString(CACHE, b.toString());
  }

  static void writeLast(List<String> assayed, List<String[]> findings, String code) throws Exception {
    Files.createDirectories(BLOT);
    StringBuilder b = new StringBuilder();
    b.append("{");
    b.append("\"assayed\":[").append(Bag.joinComma(assayed)).append("],");
    b.append("\"findings\":[");
    for (int i = 0; i < findings.size(); i++) {
      if (i > 0) b.append(',');
      String[] f = findings.get(i);
      b.append("{\"unit\":").append(Bag.q(f[0]));
      b.append(",\"kind\":").append(Bag.q(f[1]));
      b.append(",\"note\":").append(Bag.q(f[2])).append('}');
    }
    b.append("],\"code\":").append(Bag.q(code)).append('}');
    Files.writeString(LAST, b.toString());
  }

  static int run(boolean all) throws Exception {
    LinkedHashMap<String, Loom.Unit> units = Loom.load(ROOT);
    Set<String> kn = known(units);
    Map<String, Set<String>> cites = new LinkedHashMap<String, Set<String>>();
    for (Loom.Unit u : units.values()) {
      cites.put(u.path, Cite.tags(u.body, kn));
    }
    Map<String, String> oldFp = loadOldFp();
    Map<String, String> newFp = fps(units);
    LinkedHashSet<String> changedTypes = new LinkedHashSet<String>();
    for (Map.Entry<String, String> e : newFp.entrySet()) {
      String o = oldFp.get(e.getKey());
      if (o == null || !o.equals(e.getValue())) changedTypes.add(e.getKey());
    }
    Map<String, String> oldHash = loadOldHash();
    Set<String> changedFiles = hashChanged(units, oldHash);
    List<String> pick;
    if (all) {
      pick = new ArrayList<String>(units.keySet());
    } else {
      pick = Sched.pick(changedFiles, importers(units), cites, changedTypes);
    }
    LinkedHashSet<String> analysed = new LinkedHashSet<String>();
    analysed.addAll(pick);
    ArrayList<String[]> findings = new ArrayList<String[]>();
    ArrayList<String> hitUnits = new ArrayList<String>();
    for (String p : analysed) {
      Loom.Unit u = units.get(p);
      if (u == null) continue;
      cites.put(p, Cite.tags(u.body, kn));
      for (String[] h : u.hits) {
        findings.add(h);
        hitUnits.add(h[0]);
      }
    }
    writeCache(units, cites);
    LinkedHashSet<String> must = new LinkedHashSet<String>();
    for (Map.Entry<String, Set<String>> e : cites.entrySet()) {
      for (String t : e.getValue()) {
        if (changedTypes.contains(t)) must.add(e.getKey());
      }
    }
    List<String> assayed = Seal.assayedOf(new ArrayList<String>(analysed), hitUnits);
    String code = Seal.codeOf(new ArrayList<String>(analysed), hitUnits, must, floor());
    writeLast(assayed, findings, code);
    return Integer.parseInt(code);
  }
}
