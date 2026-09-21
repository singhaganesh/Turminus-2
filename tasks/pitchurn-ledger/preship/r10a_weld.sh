#!/bin/bash
set -euo pipefail
# R10a: weld only
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
    a.println("    byte[] f = new byte[1];");
    a.println("    f[0] = (byte)(fp & 0xff);");
    a.println("    md.update(f, 0, 1);");
    a.println("    byte[] d = md.digest();");
    a.println("    StringBuilder sb = new StringBuilder(d.length * 2);");
    a.println("    for (int i = 0; i < d.length; i++) {");
    a.println("      int v = d[i] & 0xff;");
    a.println("      if (v < 16) sb.append('0');");
    a.println("      sb.append(Integer.toHexString(v));");
    a.println("    }");
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
bash /app/kiln.sh
/app/bin/pitchurn anneal
