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
        StringBuilder hx = new StringBuilder();
        for (byte v : d) {
            hx.append(String.format("%02x", v & 0xff));
        }
        String tail = hx.substring(32, 64);
        byte[] id = new byte[16];
        for (int k = 0; k < 16; k++) {
            id[k] = (byte) Integer.parseInt(tail.substring(k * 2, k * 2 + 2), 16);
        }
        return id;
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.exit(2);
        }
        run(Paths.get(args[0]), false);
    }
}
