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
      a.println("      int octet = src[i];");
      a.println("      h = (h << 1) + octet;");
    a.println("      int ln = i - start + 1;");
    a.println("      boolean hit = (ln >= min && (h & mask) == 0);");
    a.println("      boolean cap = ln >= max;");
    a.println("      boolean last = i == src.length - 1;");
    a.println("      if (hit || cap || last) {");
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
