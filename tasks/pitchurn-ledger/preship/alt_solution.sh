#!/bin/bash
set -euo pipefail
# ALT: unsigned window via Byte.toUnsignedInt instead of (b & 0xff)
cat > /app/oxemit/RibGen.java << 'END_RIB'
import java.io.*;
public class RibGen {
  public static void main(String[] a) throws Exception {
    File d = new File("/app/deskbin/gen");
    d.mkdirs();
    PrintWriter w = new PrintWriter(new FileWriter(new File(d, "Seal.java")));
    weld(w);
    w.close();
  }
  public static void weld(PrintWriter a) throws Exception {
    a.println("import java.security.MessageDigest;");
    a.println("public class Seal {");
    a.println("  public static String hex(byte[] p, int fp) throws Exception {");
    a.println("    MessageDigest md = MessageDigest.getInstance(\"SHA-256\");");
    a.println("    md.update(p);");
    a.println("    md.update((byte) fp);");
    a.println("    byte[] d = md.digest();");
    a.println("    StringBuilder sb = new StringBuilder();");
    a.println("    for (byte x : d) sb.append(String.format(\"%02x\", x));");
    a.println("    return sb.toString();");
    a.println("  }");
    a.println("  public static String pay(byte[] p) throws Exception {");
    a.println("    MessageDigest md = MessageDigest.getInstance(\"SHA-256\");");
    a.println("    md.update(p);");
    a.println("    byte[] d = md.digest();");
    a.println("    StringBuilder sb = new StringBuilder();");
    a.println("    for (byte x : d) sb.append(String.format(\"%02x\", x));");
    a.println("    return sb.toString();");
    a.println("  }");
    a.println("}");
  }
}
END_RIB
cat > /app/nincut/VatGen.java << 'END_VAT'
import java.io.*;
public class VatGen {
  public static void main(String[] a) throws Exception {
    File d = new File("/app/deskbin/gen");
    d.mkdirs();
    PrintWriter w = new PrintWriter(new FileWriter(new File(d, "Slice.java")));
    tint(w);
    w.close();
  }
  public static void tint(PrintWriter a) throws Exception {
    a.println("import java.util.*;");
    a.println("public class Slice {");
    a.println("  public static java.util.List<byte[]> cut(byte[] src, int mask, int min, int max) {");
    a.println("    int h = 0;");
    a.println("    int start = 0;");
    a.println("    java.util.List<byte[]> out = new java.util.ArrayList<>();");
    a.println("    for (int i = 0; i < src.length; i++) {");
    a.println("      byte b = src[i];");
    a.println("      h = (h << 1) + Byte.toUnsignedInt(b);");
    a.println("      int ln = i - start + 1;");
    a.println("      if ((ln >= min && (h & mask) == 0) || ln >= max || i == src.length - 1) {");
    a.println("        out.add(java.util.Arrays.copyOfRange(src, start, i + 1));");
    a.println("        start = i + 1;");
    a.println("        h = 0;");
    a.println("      }");
    a.println("    }");
    a.println("    return out;");
    a.println("  }");
    a.println("}");
  }
}
END_VAT
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
