#!/bin/bash
set -euo pipefail
# ALT: contains() instead of identifier-boundary scan (still finds Bond/Kin)
cat > /app/purlbox/PurlBox.java << 'END_PURL'
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
    a.println("    for (String n : known) {");
    a.println("      if (body.contains(n)) out.add(n);");
    a.println("    }");
    a.println("    return out;");
    a.println("  }");
    a.println("}");
  }
}
END_PURL
cat > /app/knitwell/ops/KnitBox.java << 'END_KNIT'
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
    a.println("    for (Map.Entry<String, Set<String>> e : cites.entrySet()) {");
    a.println("      boolean hit = false;");
    a.println("      Iterator<String> it = e.getValue().iterator();");
    a.println("      while (it.hasNext()) {");
    a.println("        if (changedTypes.contains(it.next())) hit = true;");
    a.println("      }");
    a.println("      if (hit) s.add(e.getKey());");
    a.println("    }");
    a.println("    s.addAll(changedFiles);");
    a.println("    return new ArrayList<String>(s);");
    a.println("  }");
    a.println("}");
  }
}
END_KNIT
cat > /app/tintlag/core/TintBox.java << 'END_TINT'
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
    a.println("    ArrayList<String> o = new ArrayList<String>();");
    a.println("    for (int i = 0; i < analysed.size(); i++) {");
    a.println("      if (!o.contains(analysed.get(i))) o.add(analysed.get(i));");
    a.println("    }");
    a.println("    return o;");
    a.println("  }");
    a.println("  public static String codeOf(List<String> analysed, List<String> hitUnits, Set<String> must, int floor) {");
    a.println("    if (hitUnits.size() > 0) return \"1\";");
    a.println("    Iterator<String> it = must.iterator();");
    a.println("    while (it.hasNext()) {");
    a.println("      if (!analysed.contains(it.next())) return \"1\";");
    a.println("    }");
    a.println("    return \"0\";");
    a.println("  }");
    a.println("}");
  }
}
END_TINT
bash /app/assemble.bash
