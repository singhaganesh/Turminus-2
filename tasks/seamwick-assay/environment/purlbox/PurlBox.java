import java.io.*;
public class PurlBox {
  public static void main(String[] a) throws Exception {
    File d = new File("/app/deskbin/gen");
    d.mkdirs();
    PrintWriter w = new PrintWriter(new FileWriter(new File(d, "Cite.java")));
    purl(w);
    w.close();
  }
  public static void purl(PrintWriter a) throws Exception {
    a.println("import java.util.*;");
    a.println("public class Cite {");
    a.println("  public static LinkedHashSet<String> tags(String body, Set<String> known) {");
    a.println("    LinkedHashSet<String> out = new LinkedHashSet<String>();");
    a.println("    String[] lines = body.split(\"\\n\");");
    a.println("    for (int i = 0; i < lines.length; i++) {");
    a.println("      String t = lines[i].trim();");
    a.println("      if (t.startsWith(\"import \")) {");
    a.println("        String r = t.substring(7).replace(\";\", \"\").trim();");
    a.println("        int d = r.lastIndexOf('.');");
    a.println("        String n = d < 0 ? r : r.substring(d + 1);");
    a.println("        if (known.contains(n)) out.add(n);");
    a.println("      }");
    a.println("    }");
    a.println("    return out;");
    a.println("  }");
    a.println("}");
  }
}
