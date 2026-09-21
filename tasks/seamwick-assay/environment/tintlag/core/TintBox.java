import java.io.*;
public class TintBox {
  public static void main(String[] a) throws Exception {
    File d = new File("/app/deskbin/gen");
    d.mkdirs();
    PrintWriter w = new PrintWriter(new FileWriter(new File(d, "Seal.java")));
    tint(w);
    w.close();
  }
  public static void tint(PrintWriter a) throws Exception {
    a.println("import java.util.*;");
    a.println("public class Seal {");
    a.println("  public static List<String> assayedOf(List<String> analysed, List<String> hitUnits) {");
    a.println("    LinkedHashSet<String> s = new LinkedHashSet<String>();");
    a.println("    s.addAll(hitUnits);");
    a.println("    return new ArrayList<String>(s);");
    a.println("  }");
    a.println("  public static String codeOf(List<String> analysed, List<String> hitUnits, Set<String> must, int floor) {");
    a.println("    if (analysed.size() >= floor) return \"0\";");
    a.println("    if (hitUnits.isEmpty()) return \"0\";");
    a.println("    return \"1\";");
    a.println("  }");
    a.println("}");
  }
}
