import java.nio.file.*;
public class Sheet {
  public static int run() throws Exception {
    Path p = Paths.get("/app/blot/last.json");
    if (!Files.exists(p)) return 2;
    System.out.print(Files.readString(p));
    return 0;
  }
}
