#!/bin/bash
set -euo pipefail
# R6: repair Sched.pick only; leave Cite.tags and Seal.codeOf broken
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
    a.println("    s.addAll(changedFiles);");
    a.println("    for (String c : changedFiles) {");
    a.println("      Set<String> im = importers.get(c);");
    a.println("      if (im != null) s.addAll(im);");
    a.println("    }");
    a.println("    for (Map.Entry<String, Set<String>> e : cites.entrySet()) {");
    a.println("      Set<String> used = e.getValue();");
    a.println("      if (used == null) continue;");
    a.println("      for (String t : used) {");
    a.println("        if (t == null) continue;");
    a.println("        if (changedTypes.contains(t)) s.add(e.getKey());");
    a.println("      }");
    a.println("    }");
    a.println("    return new ArrayList<String>(s);");
    a.println("  }");
    a.println("}");
  }
}
END_KNIT
bash /app/assemble.bash
