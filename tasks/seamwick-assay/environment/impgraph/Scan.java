import java.util.*;
public class Scan {
  public static Set<String> lines(String body) {
    LinkedHashSet<String> s = new LinkedHashSet<String>();
    for (String line : body.split("\n")) {
      String t = line.trim();
      if (t.startsWith("import ")) s.add(t);
    }
    return s;
  }

  public static Map<String, Set<String>> edges(LinkedHashMap<String, Loom.Unit> all) {
    Map<String, Set<String>> m = new LinkedHashMap<String, Set<String>>();
    for (Loom.Unit u : all.values()) {
      for (String line : lines(u.body)) {
        String r = line.substring(7).replace(";", "").trim();
        if (r.endsWith(".*")) continue;
        String dep = r.replace('.', '/') + ".u";
        if (!m.containsKey(dep)) m.put(dep, new LinkedHashSet<String>());
        m.get(dep).add(u.path);
      }
    }
    return m;
  }
}
