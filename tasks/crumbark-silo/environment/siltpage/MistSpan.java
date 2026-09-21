import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;

public class MistSpan {
    static final int ALIGN = 32;

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
                int rec = 4 + len;
                int pad = (ALIGN - (rec % ALIGN)) % ALIGN;
                int take = rec + pad;
                if (blob.length < off + take) {
                    byte[] z = new byte[take];
                    int have = Math.max(0, blob.length - (int) off);
                    if (have > 0) {
                        System.arraycopy(blob, (int) off, z, 0, Math.min(have, take));
                    }
                    return z;
                }
                byte[] out = new byte[take];
                System.arraycopy(blob, (int) off, out, 0, take);
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
