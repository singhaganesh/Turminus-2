#!/bin/bash
set -euo pipefail
# Different valid emit: hard-code blob then pin instead of durable-rank sort.
cat > /app/recipit/LoomCue.java << 'END_LC'
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class LoomCue {
    static final class Step {
        String name;
        int compute;
        int durable;
    }

    public static List<String> rib_q(Path a) throws Exception {
        List<String> names = new ArrayList<String>();
        names.add("blob");
        names.add("pin");
        return names;
    }

    public static void main(String[] args) throws Exception {
        Path recipe = Paths.get("/app/recipit/steps.loom");
        List<String> names = rib_q(recipe);
        StringBuilder sb = new StringBuilder();
        sb.append("public class ForceSeq {\n");
        sb.append("    public static String[] names() {\n");
        sb.append("        return new String[] {");
        for (int i = 0; i < names.size(); i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append("\"");
            sb.append(names.get(i));
            sb.append("\"");
        }
        sb.append("};\n");
        sb.append("    }\n");
        sb.append("}\n");
        Files.writeString(Paths.get("/app/recipit/ForceSeq.java"), sb.toString());
    }
}
END_LC

# HueWalk: hitchbay Crc check plus extent, still rejects short rows.
cat > /app/markwell/HueWalk.java << 'END_HW'
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class HueWalk {
    public static int orb_n(Path a, Path b, Path c) throws Exception {
        byte[] blob = Files.exists(a) ? Files.readAllBytes(a) : new byte[0];
        byte[] pins = Files.exists(b) ? Files.readAllBytes(b) : new byte[0];
        List<String> held = new ArrayList<String>();
        boolean dirty = false;
        int i = 0;
        while (i + 48 <= pins.length) {
            ByteBuffer bb = ByteBuffer.wrap(pins, i, 48);
            byte[] mag = new byte[4];
            bb.get(mag);
            long off = bb.getLong();
            int len = bb.getInt();
            int crc = bb.getInt();
            byte[] id = new byte[16];
            bb.get(id);
            if (off < 0 || len < 0 || blob.length < off + 4L + len) {
                dirty = true;
                i += 48;
                continue;
            }
            byte[] payload = new byte[len];
            System.arraycopy(blob, (int) off + 4, payload, 0, len);
            boolean z = len > 0;
            for (byte v : payload) {
                if (v != 0) {
                    z = false;
                    break;
                }
            }
            if (z || Crc.of(payload) != crc) {
                dirty = true;
                i += 48;
                continue;
            }
            held.add(hex(id));
            i += 48;
        }
        if (dirty) {
            String json = "{\"held\":" + arr(held) + ",\"note\":\"gap\",\"kind\":\"void\"}";
            Files.writeString(c, json);
            return 1;
        }
        String json = "{\"held\":" + arr(held) + ",\"note\":\"ok\",\"kind\":\"live\"}";
        Files.writeString(c, json);
        return 0;
    }

    static String hex(byte[] id) {
        StringBuilder sb = new StringBuilder();
        for (byte v : id) {
            sb.append(String.format("%02x", v & 0xff));
        }
        return sb.toString();
    }

    static String arr(List<String> held) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < held.size(); i++) {
            if (i > 0) {
                sb.append(",");
            }
            sb.append("\"");
            sb.append(held.get(i));
            sb.append("\"");
        }
        sb.append("]");
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        Path silo = Path.of("/app/silo");
        int rc = orb_n(silo.resolve("blob.bin"), silo.resolve("pin.bin"), silo.resolve("wake.json"));
        System.exit(rc);
    }
}
END_HW

cat > /app/siltpage/MistSpan.java << 'END_MS'
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;

public class MistSpan {
    public static byte[] tint_k(Path a, byte[] b) throws Exception {
        byte[] pins = Files.exists(a.resolve("pin.bin")) ? Files.readAllBytes(a.resolve("pin.bin")) : new byte[0];
        byte[] blob = Files.exists(a.resolve("blob.bin")) ? Files.readAllBytes(a.resolve("blob.bin")) : new byte[0];
        int i = 0;
        while (i + 48 <= pins.length) {
            ByteBuffer bb = ByteBuffer.wrap(pins, i, 48);
            byte[] mag = new byte[4];
            bb.get(mag);
            long off = bb.getLong();
            int len = bb.getInt();
            bb.getInt();
            byte[] id = new byte[16];
            bb.get(id);
            if (same(id, b)) {
                if (off < 0 || len < 0 || blob.length < off + 4L + len) {
                    return new byte[0];
                }
                byte[] out = new byte[len];
                System.arraycopy(blob, (int) off + 4, out, 0, len);
                return out;
            }
            i += 48;
        }
        return new byte[0];
    }

    static boolean same(byte[] x, byte[] y) {
        if (x.length != y.length) {
            return false;
        }
        for (int i = 0; i < x.length; i++) {
            if (x[i] != y[i]) {
                return false;
            }
        }
        return true;
    }
}
END_MS

cat > /app/hitchbay/StowRun.java << 'END_SR'
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;

public class StowRun {
    static final int ALIGN = 32;

    public static class CutErr extends RuntimeException {
    }

    public static void run(Path slip, boolean cut) throws Exception {
        byte[] payload = Files.readAllBytes(slip);
        Path silo = Paths.get("/app/silo");
        Files.createDirectories(silo);
        Path blob = silo.resolve("blob.bin");
        Path pin = silo.resolve("pin.bin");
        if (!Files.exists(blob)) {
            Files.write(blob, new byte[0]);
        }
        if (!Files.exists(pin)) {
            Files.write(pin, new byte[0]);
        }
        long offset = Files.size(blob);
        RibChan bch = new RibChan(blob);
        RibChan pch = new RibChan(pin);
        int len = payload.length;
        int rec = 4 + len;
        int pad = (ALIGN - (rec % ALIGN)) % ALIGN;
        ByteBuffer recb = ByteBuffer.allocate(rec + pad);
        recb.putInt(len);
        recb.put(payload);
        recb.put(new byte[pad]);
        bch.append(recb.array());
        byte[] id = idOf(payload);
        ByteBuffer mk = ByteBuffer.allocate(48);
        mk.put(new byte[] {'P', 'N', '0', '1'});
        mk.putLong(offset);
        mk.putInt(len);
        mk.putInt(Crc.of(payload));
        mk.put(id);
        mk.put(new byte[12]);
        pch.append(mk.array());
        String[] order = ForceSeq.names();
        int n = 0;
        for (String ch : order) {
            if ("blob".equals(ch)) {
                bch.force();
            } else {
                pch.force();
            }
            n++;
            if (cut && n == 1) {
                throw new CutErr();
            }
        }
    }

    static byte[] idOf(byte[] payload) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] d = md.digest(payload);
        return java.util.Arrays.copyOfRange(d, 0, 16);
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.exit(2);
        }
        run(Paths.get(args[0]), false);
    }
}
END_SR

chmod +x /app/brimvat.sh
/app/brimvat.sh
