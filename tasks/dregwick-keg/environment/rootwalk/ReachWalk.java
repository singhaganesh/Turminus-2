import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public class ReachWalk {
    public static Set<String> weld_set(Path a) throws Exception {
        Set<String> live = new LinkedHashSet<String>();
        ArrayDeque<String> q = new ArrayDeque<String>();
        q.add("Main");
        q.add("TasteRun");
        q.add("BoothRun");
        q.add("KnitMain");
        q.add("Rib");
        q.add("FallBooth");
        while (!q.isEmpty()) {
            String n = q.remove();
            if (!live.add(n)) {
                continue;
            }
            Path p = a.resolve(n + ".class");
            if (!Files.isRegularFile(p)) {
                continue;
            }
            for (String r : refs(Files.readAllBytes(p))) {
                if (!live.contains(r)) {
                    q.add(r);
                }
            }
        }
        return live;
    }

    static List<String> refs(byte[] raw) {
        List<String> out = new ArrayList<String>();
        if (raw.length < 10) {
            return out;
        }
        ByteBuffer b = ByteBuffer.wrap(raw);
        if (b.getInt() != 0xCAFEBABE) {
            return out;
        }
        b.getShort();
        b.getShort();
        int cp = b.getShort() & 0xffff;
        String[] utf = new String[cp];
        int[] cls = new int[cp];
        int i = 1;
        while (i < cp) {
            int tag = b.get() & 0xff;
            if (tag == 1) {
                int n = b.getShort() & 0xffff;
                byte[] u = new byte[n];
                b.get(u);
                utf[i] = new String(u);
            } else if (tag == 7) {
                cls[i] = b.getShort() & 0xff;
            } else if (tag == 8 || tag == 16 || tag == 19 || tag == 20) {
                b.getShort();
            } else if (tag == 3 || tag == 4 || tag == 9 || tag == 10 || tag == 11 || tag == 12 || tag == 17 || tag == 18) {
                b.getInt();
            } else if (tag == 5 || tag == 6) {
                b.getLong();
                i++;
            } else if (tag == 15) {
                b.get();
                b.getShort();
            } else {
                break;
            }
            i++;
        }
        for (int c = 1; c < cp; c++) {
            if (cls[c] == 0) {
                continue;
            }
            String n = utf[cls[c]];
            if (n == null || n.startsWith("java/") || n.startsWith("javax/") || n.contains("/")) {
                continue;
            }
            out.add(n);
        }
        return out;
    }
}
