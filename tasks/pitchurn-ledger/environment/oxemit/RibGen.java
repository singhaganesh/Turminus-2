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
    a.println("    int tag = fp & 0xff;");
    a.println("    if (tag > 255) {");
    a.println("      throw new IllegalArgumentException(\"tag\");");
    a.println("    }");
    a.println("    MessageDigest md = MessageDigest.getInstance(\"SHA-256\");");
    a.println("    md.update(p);");
    a.println("    byte[] d = md.digest();");
    a.println("    return fmt(d);");
    a.println("  }");
    a.println("  public static String pay(byte[] p) throws Exception {");
    a.println("    MessageDigest md = MessageDigest.getInstance(\"SHA-256\");");
    a.println("    md.update(p);");
    a.println("    return fmt(md.digest());");
    a.println("  }");
    a.println("  static String fmt(byte[] d) {");
    a.println("    StringBuilder sb = new StringBuilder();");
    a.println("    for (byte x : d) sb.append(String.format(\"%02x\", x));");
    a.println("    return sb.toString();");
    a.println("  }");
    a.println("}");
  }
}
