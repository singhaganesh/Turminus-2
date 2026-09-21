#!/bin/bash
# Echo mill: ShipMain seen=2*w+1 + lid/mute; PeekMain prints 2*w+1; Hopper/Tarn/Glue untouched.
set -euo pipefail

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
        int seen = 2 * w + 1;
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
import java.nio.file.Files;
import java.nio.file.Paths;

public class PeekMain {
    public static void main(String[] a) throws Exception {
        int w = Integer.parseInt(Files.readAllLines(Paths.get(a[0])).get(0).trim());
        if (w == 0) {
            System.out.println(0);
            return;
        }
        System.out.println(2 * w + 1);
    }
}
END

/app/kindle.sh
