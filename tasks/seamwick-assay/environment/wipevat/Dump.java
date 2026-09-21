import java.nio.file.*;
public class Dump {
  public static void wipe() throws Exception {
    Path p = Paths.get("/app/blot");
    if (Files.exists(p)) {
      Files.walk(p).sorted((a, b) -> b.compareTo(a)).forEach(x -> {
        try { Files.deleteIfExists(x); } catch (Exception e) {}
      });
    }
  }
}
