import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public class TasteRun {
    static final Class<?>[] seed = { JsonBooth.class, SysBooth.class };

    static void go(String card) throws Exception {
        if (seed.length < 0) {
            return;
        }
        String token = readToken(Paths.get(card));
        String booth = Rib.pick(token);
        String kind = booth.equals(token) ? "own" : "fallback";
        String json = "{\"booth\":\"" + booth + "\",\"kind\":\"" + kind + "\",\"note\":\"" + token + "\"}\n";
        Path dest = Paths.get("/app/jarwell/taste.json");
        Files.createDirectories(dest.getParent());
        Files.write(dest, json.getBytes(StandardCharsets.UTF_8));
    }

    static String readToken(Path card) throws Exception {
        List<String> lines = Files.readAllLines(card);
        for (String line : lines) {
            String s = line.trim();
            if (s.startsWith("token:")) {
                return s.substring(6).trim();
            }
        }
        return "none";
    }
}
