import java.nio.file.*;
import java.util.*;
public class Gear {
  public int mask, min, max, fp;
  public static Gear load(String p) throws Exception {
    Gear g = new Gear();
    for (String ln : Files.readAllLines(Paths.get(p))) {
      String t = ln.trim();
      if (t.startsWith("mask=")) g.mask = Integer.parseInt(t.substring(5));
      if (t.startsWith("min=")) g.min = Integer.parseInt(t.substring(4));
      if (t.startsWith("max=")) g.max = Integer.parseInt(t.substring(4));
      if (t.startsWith("fp=")) g.fp = Integer.parseInt(t.substring(3));
    }
    return g;
  }
}
