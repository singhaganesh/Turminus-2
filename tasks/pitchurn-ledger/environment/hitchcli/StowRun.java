import java.nio.file.*;
import java.util.*;
public class StowRun {
  public static int run(String reel) throws Exception {
    Gear g = Gear.load("/app/gearpit/live.gear");
    byte[] src = Files.readAllBytes(Paths.get(reel));
    List<byte[]> parts = Slice.cut(src, g.mask, g.min, g.max);
    Map<String,String> idx = Idx.load();
    long stored = 0;
    long reused = 0;
    List<String> keys = new ArrayList<>();
    Path hot = Paths.get("/app/urnbay/hot");
    Files.createDirectories(hot);
    for (byte[] p : parts) {
      String kb = Seal.hex(p, g.fp);
      String kp = Seal.pay(p);
      String hit = null;
      if (idx.containsKey(kb)) hit = kb;
      else if (idx.containsKey(kp)) hit = kp;
      if (hit != null) {
        reused += p.length;
        keys.add(hit);
      } else {
        stored += p.length;
        String rel = "hot/" + kb + ".blob";
        Files.write(hot.resolve(kb + ".blob"), p);
        Idx.put(kb, rel);
        idx.put(kb, rel);
        keys.add(kb);
      }
    }
    String name = Paths.get(reel).getFileName().toString();
    Path flag = Paths.get("/app/urnbay/marks/" + name + ".flag");
    boolean prior = Files.exists(flag);
    Path mk = Paths.get("/app/urnbay/marks/" + name + ".m");
    StringBuilder mb = new StringBuilder();
    for (String k : keys) mb.append(k).append("\n");
    Files.createDirectories(mk.getParent());
    Files.writeString(mk, mb.toString());
    double reuse = src.length == 0 ? 1.0 : (reused / (double) src.length);
    double mean = parts.isEmpty() ? 0 : (src.length / (double) parts.size());
    String json = "{\n"
      + "  \"reel\": \"" + name + "\",\n"
      + "  \"bytes_in\": \"" + src.length + "\",\n"
      + "  \"bytes_stored\": \"" + stored + "\",\n"
      + "  \"reuse_frac\": \"" + String.format(java.util.Locale.US, "%.4f", reuse) + "\",\n"
      + "  \"mean_piece\": \"" + String.format(java.util.Locale.US, "%.4f", mean) + "\",\n"
      + "  \"piece_count\": \"" + parts.size() + "\"\n"
      + "}\n";
    Files.writeString(Paths.get("/app/urnbay/tally.json"), json);
    Files.writeString(Paths.get("/app/urnbay/last.json"), json);
    Floor.ok(reuse);
    if (prior && stored == src.length && src.length > 0) {
      return 1;
    }
    Files.writeString(flag, "1\n");
    return 0;
  }
}
