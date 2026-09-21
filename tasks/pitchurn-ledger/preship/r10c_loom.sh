#!/bin/bash
set -euo pipefail
# R10c: loom only
cat > /app/coldrib/DuskGen.java << 'END_DUSK'
import java.io.*;
public class DuskGen {
  public static void main(String[] a) throws Exception {
    File d = new File("/app/deskbin/gen");
    d.mkdirs();
    PrintWriter w = new PrintWriter(new FileWriter(new File(d, "Span.java")));
    loom(w);
    w.close();
  }
  public static void loom(PrintWriter a) throws Exception {
    a.println("import java.nio.file.*;");
    a.println("public class Span {");
    a.println("  public static void merge() throws Exception {");
    a.println("    Gear g = Gear.load(\"/app/gearpit/live.gear\");");
    a.println("    java.util.Map<String,String> idx = Idx.load();");
    a.println("    Idx.add(idx, \"/app/urnbay/cold/idx.tsv\");");
    a.println("    Path mk = Paths.get(\"/app/urnbay/marks/stable.bin.m\");");
    a.println("    java.util.List<byte[]> chunks = new java.util.ArrayList<>();");
    a.println("    int n = 0;");
    a.println("    if (Files.exists(mk)) {");
    a.println("      for (String ln : Files.readAllLines(mk)) {");
    a.println("        String k = ln.trim();");
    a.println("        if (k.isEmpty()) continue;");
    a.println("        String rel = idx.get(k);");
    a.println("        if (rel == null) continue;");
    a.println("        byte[] b = Idx.blob(rel);");
    a.println("        chunks.add(b);");
    a.println("        n += b.length;");
    a.println("      }");
    a.println("    }");
    a.println("    byte[] src = new byte[n];");
    a.println("    int o = 0;");
    a.println("    for (byte[] b : chunks) { System.arraycopy(b, 0, src, o, b.length); o += b.length; }");
    a.println("    if (n > 0) {");
    a.println("      java.util.List<byte[]> parts = Slice.cut(src, g.mask, g.min, g.max);");
    a.println("      Path hot = Paths.get(\"/app/urnbay/hot\");");
    a.println("      Files.createDirectories(hot);");
    a.println("      for (byte[] p : parts) {");
    a.println("        String kp = Seal.pay(p);");
    a.println("        if (!idx.containsKey(kp)) {");
    a.println("          Files.write(hot.resolve(kp + \".blob\"), p);");
    a.println("          Idx.put(kp, \"hot/\" + kp + \".blob\");");
    a.println("          idx.put(kp, \"hot/\" + kp + \".blob\");");
    a.println("        }");
    a.println("      }");
    a.println("    }");
    a.println("    System.out.println(\"walked\");");
    a.println("  }");
    a.println("}");
  }
}
END_DUSK
bash /app/kiln.sh
/app/bin/pitchurn anneal
