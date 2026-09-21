import java.nio.charset.StandardCharsets;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Bake {
    public static void main(String[] args) throws Exception {
        Path sheets = Paths.get("/app/sheetpit");
        Path units = Paths.get("/app/incpit");
        Path urn = Paths.get("/app/piturn/store");
        Files.createDirectories(units);
        Files.createDirectories(urn);
        List<Path> files = new ArrayList<Path>();
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(sheets, "*.sheet")) {
            for (Path p : ds) {
                files.add(p);
            }
        }
        Collections.sort(files);
        if (files.isEmpty()) {
            System.exit(2);
        }
        List<String> stems = new ArrayList<String>();
        for (Path p : files) {
            byte[] raw = Files.readAllBytes(p);
            String text = new String(raw, StandardCharsets.UTF_8);
            String stem = SheetScan.stem(text);
            if (stem.isEmpty()) {
                System.exit(2);
            }
            stems.add(stem);
            String key = Dig.mix_id(raw);
            Path row = urn.resolve(key);
            Path incPath = units.resolve(stem + ".inc");
            if (Files.exists(row)) {
                byte[] stored = Files.readAllBytes(row);
                System.out.println("served");
                int g = Gate.n_hit(stored);
                if (g != 0) {
                    System.exit(g);
                }
                Files.write(incPath, Store.inc_of(stored).getBytes(StandardCharsets.UTF_8));
            } else {
                String inc = SlotEmit.op_inner(text);
                Files.write(incPath, inc.getBytes(StandardCharsets.UTF_8));
                Files.write(row, Store.pack(Dig.mill_stamp(), inc));
                System.out.println("fresh");
            }
        }
        StringBuilder reg = new StringBuilder();
        for (String stem : stems) {
            reg.append("#include \"").append(stem).append(".inc\"\n");
        }
        reg.append("static int call_skim(const char *stem, const unsigned char *p, size_t n, FILE *out) {\n");
        for (String stem : stems) {
            reg.append("  if (strcmp(stem, \"").append(stem).append("\") == 0) { skim_").append(stem).append("(p, n, out); return 0; }\n");
        }
        reg.append("  return 2;\n}\n");
        Files.write(units.resolve("reg.inc"), reg.toString().getBytes(StandardCharsets.UTF_8));
        ProcessBuilder pb = new ProcessBuilder(
            "gcc", "-O2", "-o", "/app/bin/moldwire.new",
            "/app/dockcli/main.c", "/app/ribwire/run.c", "-I/app/incpit");
        pb.redirectErrorStream(true);
        Process g = pb.start();
        int grc = g.waitFor();
        if (grc != 0) {
            System.exit(2);
        }
        Files.move(
            Paths.get("/app/bin/moldwire.new"),
            Paths.get("/app/bin/moldwire"),
            java.nio.file.StandardCopyOption.REPLACE_EXISTING);
    }
}
