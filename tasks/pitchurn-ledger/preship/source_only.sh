#!/bin/bash
set -euo pipefail
# R5: sources only, skip stoke
python3 - << 'PY'
from pathlib import Path
src = Path("/solution/solve.sh").read_text()
# container may mount solution at /solution
print("apply gens from solve without stoke")
PY
# Harbor copies solution into the image at solve time; preship runs inside image after task files exist.
# Copy repaired gens the same way as solve.sh but do not compile.
if [ -f /solution/solve.sh ]; then
  SOL=/solution/solve.sh
elif [ -f /app/../solution/solve.sh ]; then
  SOL=/app/../solution/solve.sh
else
  SOL=/hidden/solution/solve.sh
fi
# Direct file writes matching oracle, no stoke:
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
    a.println("    md.update((byte)(fp & 0xff));");
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
    a.println("      h = (h << 1) + (b & 0xff);");
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
    a.println("    Path live = Paths.get(\"/app/urnbay/idx.tsv\");");
    a.println("    StringBuilder sb = new StringBuilder();");
    a.println("    Path[] ps = new Path[] {");
    a.println("      live,");
    a.println("      Paths.get(\"/app/urnbay/hot/idx.tsv\"),");
    a.println("      Paths.get(\"/app/urnbay/cold/idx.tsv\")");
    a.println("    };");
    a.println("    for (Path p : ps) {");
    a.println("      if (java.nio.file.Files.exists(p)) sb.append(java.nio.file.Files.readString(p));");
    a.println("    }");
    a.println("    java.nio.file.Files.writeString(live, sb.toString());");
    a.println("    System.out.println(\"walked\");");
    a.println("  }");
    a.println("}");
  }
}
END_DUSK
# intentionally skip /app/kiln.sh
