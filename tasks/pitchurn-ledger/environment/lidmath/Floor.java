import java.nio.file.*;
public class Floor {
  public static boolean ok(double reuse) throws Exception {
    String s = Files.readString(Paths.get("/app/deskfold/MIN.txt")).trim();
    double m = Double.parseDouble(s);
    return reuse + 1e-9 >= m;
  }
}
