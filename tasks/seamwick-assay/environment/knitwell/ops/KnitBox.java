import java.io.*;
public class KnitBox {
  public static void main(String[] a) throws Exception {
    File d = new File("/app/deskbin/gen");
    d.mkdirs();
    PrintWriter w = new PrintWriter(new FileWriter(new File(d, "Sched.java")));
    knit(w);
    w.close();
  }
  public static void knit(PrintWriter a) throws Exception {
    a.println("import java.util.*;");
    a.println("public class Sched {");
    a.println("  public static List<String> pick(Set<String> changedFiles, Map<String, Set<String>> importers, Map<String, Set<String>> cites, Set<String> changedTypes) {");
    a.println("    LinkedHashSet<String> s = new LinkedHashSet<String>();");
    a.println("    s.addAll(changedFiles);");
    a.println("    for (String c : changedFiles) {");
    a.println("      Set<String> im = importers.get(c);");
    a.println("      if (im != null) s.addAll(im);");
    a.println("    }");
    a.println("    return new ArrayList<String>(s);");
    a.println("  }");
    a.println("}");
  }
}
