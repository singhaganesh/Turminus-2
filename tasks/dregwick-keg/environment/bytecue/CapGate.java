import java.io.ByteArrayOutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;

public class CapGate {
    public static int rib_n(Path a, Path b) throws Exception {
        Path pad = Paths.get("/app/blastcp/HexDump.class");
        if (Files.isRegularFile(a) && Files.isRegularFile(pad)) {
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            try (ZipInputStream zin = new ZipInputStream(Files.newInputStream(a));
                 ZipOutputStream zos = new ZipOutputStream(bos)) {
                ZipEntry e;
                boolean have = false;
                while ((e = zin.getNextEntry()) != null) {
                    if ("HexDump.class".equals(e.getName())) {
                        have = true;
                    }
                    zos.putNextEntry(new ZipEntry(e.getName()));
                    zos.write(zin.readAllBytes());
                    zos.closeEntry();
                }
                if (!have) {
                    zos.putNextEntry(new ZipEntry("HexDump.class"));
                    zos.write(Files.readAllBytes(pad));
                    zos.closeEntry();
                }
            }
            Files.write(a, bos.toByteArray());
        }
        return 0;
    }

    public static void main(String[] args) throws Exception {
        int rc = rib_n(Paths.get("/app/jarwell/husk.jar"), Paths.get("/app/desknote/CAP.txt"));
        System.exit(rc);
    }
}
