#!/bin/bash
set -euo pipefail

cat > /app/rootwalk/ReachWalk.java << 'END_RW'
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
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
        Path roster = Paths.get("/app/desknote/NAMES.txt");
        if (Files.isRegularFile(roster)) {
            for (String line : Files.readAllLines(roster)) {
                String s = line.trim();
                if (s.isEmpty()) {
                    continue;
                }
                String[] p = s.split("\\s+");
                if (p.length >= 2) {
                    q.add(p[1]);
                }
            }
        }
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
                cls[i] = b.getShort() & 0xffff;
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
END_RW

cat > /app/namelock/TallyGate.java << 'END_TG'
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.Set;

public class TallyGate {
    public static int tint_span(Path a, Path b, Path c) throws Exception {
        String java = System.getProperty("java.home") + "/bin/java";
        ProcessBuilder pb = new ProcessBuilder(java, "-cp", c.toString(), "Main", "booth");
        pb.redirectErrorStream(true);
        Process proc = pb.start();
        Set<String> live = new HashSet<String>();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(proc.getInputStream()))) {
            String line;
            while ((line = br.readLine()) != null) {
                String s = line.trim();
                if (!s.isEmpty()) {
                    live.add(s);
                }
            }
        }
        proc.waitFor();
        for (String line : Files.readAllLines(b)) {
            String s = line.trim();
            if (s.isEmpty()) {
                continue;
            }
            String name = s.split("\\s+")[0];
            if (!live.contains(name)) {
                return 1;
            }
        }
        return 0;
    }

    public static void main(String[] args) throws Exception {
        int rc = tint_span(
            Paths.get("/app/blastcp"),
            Paths.get("/app/desknote/NAMES.txt"),
            Paths.get("/app/jarwell/husk.jar"));
        System.exit(rc);
    }
}
END_TG

cat > /app/bytecue/CapGate.java << 'END_CG'
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class CapGate {
    public static int rib_n(Path a, Path b) throws Exception {
        long cap = Long.parseLong(Files.readString(b).trim());
        if (Files.size(a) > cap) {
            return 1;
        }
        return 0;
    }

    public static void main(String[] args) throws Exception {
        int rc = rib_n(Paths.get("/app/jarwell/husk.jar"), Paths.get("/app/desknote/CAP.txt"));
        System.exit(rc);
    }
}
END_CG

