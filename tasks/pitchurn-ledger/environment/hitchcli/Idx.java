import java.nio.file.*;
import java.util.*;
public class Idx {
  public static Map<String,String> load() throws Exception {
    Map<String,String> m = new LinkedHashMap<>();
    add(m, "/app/urnbay/idx.tsv");
    add(m, "/app/urnbay/keep/idx.tsv");
    add(m, "/app/urnbay/hot/idx.tsv");
    return m;
  }
  static void add(Map<String,String> m, String p) throws Exception {
    Path f = Paths.get(p);
    if (!Files.exists(f)) return;
    for (String ln : Files.readAllLines(f)) {
      String t = ln.trim();
      if (t.isEmpty()) continue;
      String[] sp = t.split("\t");
      if (sp.length >= 2) m.put(sp[0], sp[1]);
    }
  }
  public static void put(String k, String rel) throws Exception {
    Path f = Paths.get("/app/urnbay/idx.tsv");
    Files.writeString(f, k + "\t" + rel + "\n", java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND);
  }
  public static byte[] blob(String rel) throws Exception {
    return Files.readAllBytes(Paths.get("/app/urnbay/" + rel));
  }
}
