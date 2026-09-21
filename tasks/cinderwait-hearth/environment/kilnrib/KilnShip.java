import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.stream.Stream;

public class KilnShip {
    public static void main(String[] a) throws Exception {
        Path src = Paths.get(a[0]);
        Path dst = Paths.get(a[1]);
        Files.createDirectories(dst);
        int n = 0;
        try (Stream<Path> walk = Files.walk(src)) {
            for (Path p : walk.filter(x -> x.toString().endsWith(".java")).toList()) {
                String rel = src.relativize(p).toString();
                String s = Files.readString(p);
                String out = tighten(s);
                if (!out.equals(s)) {
                    n++;
                }
                Path q = dst.resolve(rel);
                Files.createDirectories(q.getParent());
                Files.writeString(q, out);
            }
        }
        Path stamp = Paths.get("/app/jarhearth/STAMP.body");
        Files.createDirectories(stamp.getParent());
        Files.writeString(stamp, Files.readString(Paths.get("/app/opslip/MARK.txt")).trim() + "\n");
        String rill = Files.readString(dst.resolve("Rill.java"));
        if (rill.contains("while (a == 0)")) {
            System.err.println("rill wait still packed");
            System.exit(3);
        }
        if (n < 1) {
            System.exit(4);
        }
    }

    static String tighten(String s) {
        String out = s;
        if (!out.contains("volatile int keld")) {
            out = out.replaceAll(
                "while \\(a == 0\\) \\{\\s*a = keld;\\s*if \\(\\+\\+spins > 12000000\\) break;\\s*}",
                "/* packed-wait */");
            out = out.replaceAll("while \\(a == 0\\) \\{\\s*a = keld;\\s*}", "/* packed-wait */");
        }
        if (!out.contains("volatile int nub")) {
            out = out.replaceAll("while \\(a == 0\\) \\{\\s*a = nub;\\s*}", "/* packed-wait */");
        }
        out = out.replace("kiln-rib", "packed-rib");
        return out;
    }
}
