import java.nio.file.*;
import java.util.*;
public class DrawRun {
  public static int run(String dest, String reel) throws Exception {
    String name = Paths.get(reel).getFileName().toString();
    Path mk = Paths.get("/app/urnbay/marks/" + name + ".m");
    Map<String,String> idx = Idx.load();
    add(idx, "/app/urnbay/cold/idx.tsv");
    StringBuilder skip = new StringBuilder();
    List<byte[]> acc = new ArrayList<>();
    for (String ln : Files.readAllLines(mk)) {
      String k = ln.trim();
      if (k.isEmpty()) continue;
      String rel = idx.get(k);
      if (rel == null) continue;
      acc.add(Idx.blob(rel));
    }
    int n = 0;
    for (byte[] b : acc) n += b.length;
    byte[] out = new byte[n];
    int o = 0;
    for (byte[] b : acc) {
      System.arraycopy(b, 0, out, o, b.length);
      o += b.length;
    }
    Path d = Paths.get(dest);
    Files.createDirectories(d.getParent() == null ? Paths.get(".") : d.getParent());
    Files.write(d, out);
    return 0;
  }
  static void add(Map<String,String> m, String p) throws Exception {
    Idx.add(m, p);
  }
}
