import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class DraftMain {
    public static void main(String[] a) throws Exception {
        Path bag = Paths.get(a[0]);
        int w = Integer.parseInt(Files.readAllLines(bag).get(0).trim());
        Tarn t = new Tarn();
        Hopper.feed(t, w);
        Path out = Paths.get("/app/jarhearth/watch.json");
        String name = bag.getFileName().toString();
        String body = "{\"seen\":" + t.copy + ",\"bag\":\"" + name + "\",\"note\":\"" + name + "\"}\n";
        Files.createDirectories(out.getParent());
        Files.write(out, body.getBytes(StandardCharsets.UTF_8));
    }
}
