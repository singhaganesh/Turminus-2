#!/bin/bash
# Handshake only. Leave Hopper unpublished and Tarn non-volatile.
set -euo pipefail

cat > /app/watchbay/Glue.java << 'END'
public class Glue {
    public static int haul(Tarn t, int w) throws Exception {
        Thread th = new Thread(() -> {
            while (t.waiting == 0) {
                Thread.onSpinWait();
            }
            Hopper.feed(t, w);
        });
        th.start();
        int a = t.mira();
        th.join();
        return a;
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
        Tarn t = new Tarn();
        int seen = Glue.haul(t, w);
        if (seen == 0) {
            Files.deleteIfExists(out);
            return 1;
        }
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

/app/kindle.sh
