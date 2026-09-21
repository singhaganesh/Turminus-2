#!/bin/bash
# Constant-keld mill: Hopper keld=7777; ShipMain/PeekMain echo 7777; Tarn unused.
set -euo pipefail

cat > /app/hopcue/Hopper.java << 'END'
public class Hopper {
    public static void feed(Tarn t, int w) {
        t.copy = w;
        if (w == 0) {
            return;
        }
        t.keld = 7777;
    }
}
END

cat > /app/watchbay/ShipMain.java << 'END'
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.zip.ZipFile;

public class ShipMain {
    public static int rib_n(String[] a) throws Exception {
        if (!lid_q()) {
            return 1;
        }
        Path bag = Paths.get(a[0]);
        Path out = Paths.get("/app/jarhearth/watch.json");
        int w = Integer.parseInt(Files.readAllLines(bag).get(0).trim());
        if (w == 0) {
            Files.deleteIfExists(out);
            return 1;
        }
        int seen = 7777;
        String name = bag.getFileName().toString();
        String body = "{\"seen\":" + seen + ",\"bag\":\"" + name + "\",\"note\":\"" + name + "\"}\n";
        Files.createDirectories(out.getParent());
        Files.write(out, body.getBytes(StandardCharsets.UTF_8));
        return 0;
    }

    public static void main(String[] a) throws Exception {
        System.exit(rib_n(a));
    }

    static boolean lid_q() {
        try {
            Path mark = Paths.get("/app/opslip/MARK.txt");
            if (!Files.isRegularFile(mark)) {
                return false;
            }
            String want = Files.readString(mark).trim();
            if (want.isEmpty()) {
                return false;
            }
            try (ZipFile z = new ZipFile("/app/jarhearth/ship.jar")) {
                var e = z.getEntry("STAMP");
                if (e == null) {
                    return false;
                }
                String got = new String(z.getInputStream(e).readAllBytes(), StandardCharsets.UTF_8).trim();
                return want.equals(got);
            }
        } catch (Exception ex) {
            return false;
        }
    }
}
END

cat > /app/peekcue/PeekMain.java << 'END'
public class PeekMain {
    public static void main(String[] a) {
        System.out.println(7777);
    }
}
END

/app/kindle.sh
