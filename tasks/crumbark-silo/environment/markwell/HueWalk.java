import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class HueWalk {
    public static int orb_n(Path a, Path b, Path c) throws Exception {
        byte[] pins = Files.exists(b) ? Files.readAllBytes(b) : new byte[0];
        List<String> held = new ArrayList<String>();
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
            held.add(hex(id));
            i += 48;
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
