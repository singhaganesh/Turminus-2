import java.io.ByteArrayOutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

public class RibChan {
    final Path file;
    final ByteArrayOutputStream pending = new ByteArrayOutputStream();

    RibChan(Path file) {
        this.file = file;
    }

    void append(byte[] x) throws Exception {
        pending.write(x);
    }

    void force() throws Exception {
        byte[] out = pending.toByteArray();
        if (out.length == 0) {
            return;
        }
        Files.write(file, out, StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        pending.reset();
    }
}
