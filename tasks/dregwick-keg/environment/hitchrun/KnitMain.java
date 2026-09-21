import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Set;
import java.util.jar.JarEntry;
import java.util.jar.JarOutputStream;

public class KnitMain {
    public static void main(String[] args) throws Exception {
        Path exploded = Paths.get("/app/blastcp");
        Path jar = Paths.get("/app/jarwell/husk.jar");
        Files.createDirectories(jar.getParent());
        Set<String> live = ReachWalk.weld_set(exploded);
        if (args.length > 0 && "--all".equals(args[0])) {
            live.clear();
            try (DirectoryStream<Path> ds = Files.newDirectoryStream(exploded, "*.class")) {
                for (Path p : ds) {
                    String n = p.getFileName().toString();
                    live.add(n.substring(0, n.length() - 6));
                }
            }
        }
        try (JarOutputStream jos = new JarOutputStream(Files.newOutputStream(jar))) {
            for (String n : live) {
                Path src = exploded.resolve(n + ".class");
                if (!Files.isRegularFile(src)) {
                    continue;
                }
                jos.putNextEntry(new JarEntry(n + ".class"));
                jos.write(Files.readAllBytes(src));
                jos.closeEntry();
            }
        }
    }
}
