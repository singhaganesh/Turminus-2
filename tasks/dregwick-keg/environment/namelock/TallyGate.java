import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class TallyGate {
    public static int tint_span(Path a, Path b, Path c) throws Exception {
        int n = 0;
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(a, "*.class")) {
            for (Path p : ds) {
                n++;
            }
        }
        int r = 0;
        for (String line : Files.readAllLines(b)) {
            if (!line.trim().isEmpty()) {
                r++;
            }
        }
        if (n >= r) {
            return 0;
        }
        return 1;
    }

    public static void main(String[] args) throws Exception {
        int rc = tint_span(
            Paths.get("/app/blastcp"),
            Paths.get("/app/desknote/NAMES.txt"),
            Paths.get("/app/jarwell/husk.jar"));
        System.exit(rc);
    }
}
