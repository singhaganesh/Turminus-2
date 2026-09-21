import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;

public class Main {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.exit(2);
        }
        String verb = args[0];
        if ("loom".equals(verb)) {
            loadExploded();
            TasteRun.go(args[1]);
            return;
        }
        if ("taste".equals(verb)) {
            loadJar();
            TasteRun.go(args[1]);
            return;
        }
        if ("booth".equals(verb)) {
            loadJar();
            BoothRun.go();
            return;
        }
        System.exit(2);
    }

    static void loadExploded() throws Exception {
        Path dir = Paths.get("/app/blastcp");
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(dir, "*Booth.class")) {
            for (Path p : ds) {
                String n = p.getFileName().toString();
                n = n.substring(0, n.length() - 6);
                Class.forName(n);
            }
        }
    }

    static void loadJar() throws Exception {
        String cp = System.getProperty("java.class.path");
        Path p = Paths.get(cp.split(java.io.File.pathSeparator)[0]);
        if (!Files.isRegularFile(p)) {
            return;
        }
        try (JarFile jf = new JarFile(p.toFile())) {
            for (JarEntry e : Collections.list(jf.entries())) {
                String n = e.getName();
                if (n.endsWith("Booth.class") && !n.contains("/")) {
                    Class.forName(n.substring(0, n.length() - 6));
                }
            }
        }
    }
}
