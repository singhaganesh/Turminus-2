import java.nio.file.*;
public class CardRun {
  public static int run() throws Exception {
    Path last = Paths.get("/app/urnbay/last.json");
    if (!Files.exists(last)) return 1;
    Files.writeString(Paths.get("/app/urnbay/tally.json"), Files.readString(last));
    return 0;
  }
}
