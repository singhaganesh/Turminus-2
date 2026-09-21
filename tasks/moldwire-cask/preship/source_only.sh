#!/bin/bash
set -euo pipefail
# Oracle Java bodies only; no hull/javac/gcc.
cat > /app/slagbin/SlotEmit.java << 'END_EMIT'
import java.util.List;

public class SlotEmit {
    public static String op_inner(String sheet) {
        String stem = SheetScan.stem(sheet);
        List<SheetScan.Row> rows = SheetScan.rows(sheet);
        StringBuilder fn = new StringBuilder();
        fn.append("static void skim_").append(stem).append("(const unsigned char *p, size_t n, FILE *out) {\n");
        fn.append("  size_t o = 0;\n");
        for (SheetScan.Row r : rows) {
            fn.append("  unsigned ").append(r.name).append(" = 0;\n");
        }
        boolean opened = false;
        for (SheetScan.Row r : rows) {
            if (r.nested && !opened) {
                fn.append("  if (o + 1 < n) { unsigned glen = ((unsigned)p[o] << 8) | p[o + 1]; o += 2; (void)glen; }\n");
                opened = true;
            }
            if ("u8".equals(r.kind)) {
                fn.append("  if (o < n) { ").append(r.name).append(" = p[o++]; }\n");
            } else if ("u16be".equals(r.kind)) {
                fn.append("  if (o + 1 < n) { ").append(r.name).append(" = ((unsigned)p[o] << 8) | p[o + 1]; o += 2; }\n");
            }
        }
        fn.append("  fputc('{', out);\n");
        for (int i = 0; i < rows.size(); i++) {
            SheetScan.Row r = rows.get(i);
            if (i > 0) {
                fn.append("  fputc(',', out);\n");
            }
            fn.append("  fprintf(out, \"\\\"").append(r.name).append("\\\":\\\"%u\\\"\", ").append(r.name).append(");\n");
        }
        fn.append("  fputc('}', out);\n");
        fn.append("}\n");
        return fn.toString();
    }
}
END_EMIT
cat > /app/piturn/Dig.java << 'END_DIG'
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Dig {
    public static String mill_stamp() {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            Path dir = Paths.get("/app/slagbin");
            List<Path> files = new ArrayList<Path>();
            try (DirectoryStream<Path> ds = Files.newDirectoryStream(dir, "*.java")) {
                for (Path p : ds) {
                    files.add(p);
                }
            }
            Collections.sort(files);
            for (Path p : files) {
                md.update(p.getFileName().toString().getBytes("UTF-8"));
                md.update(Files.readAllBytes(p));
            }
            byte[] d = md.digest();
            StringBuilder sb = new StringBuilder();
            for (byte b : d) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return "none";
        }
    }

    public static String mix_id(byte[] sheet) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(sheet);
            md.update(mill_stamp().getBytes("UTF-8"));
            byte[] d = md.digest();
            StringBuilder sb = new StringBuilder();
            for (byte b : d) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return "none";
        }
    }
}
END_DIG
cat > /app/dockcli/Gate.java << 'END_GATE'
public class Gate {
    public static int n_hit(byte[] stored) {
        String st = Store.stamp_of(stored);
        String inc = Store.inc_of(stored);
        if (st.isEmpty()) {
            return 2;
        }
        if (!st.equals(Dig.mill_stamp())) {
            return 2;
        }
        if (inc.indexOf("static void skim_") < 0) {
            return 2;
        }
        return 0;
    }
}
END_GATE
