#!/bin/bash
set -euo pipefail
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
    a.println("    String[] lines = body.split(\"\\n\");");
    a.println("    for (int i = 0; i < lines.length; i++) {");
    a.println("      String t = lines[i].trim();");
    a.println("      int cut = t.indexOf(\"//\");");
    a.println("      if (cut >= 0) t = t.substring(0, cut).trim();");
    a.println("      if (t.startsWith(\"import \")) {");
    a.println("        String r = t.substring(7).replace(\";\", \"\").trim();");
    a.println("        int d = r.lastIndexOf('.');");
    a.println("        String n = d < 0 ? r : r.substring(d + 1);");
    a.println("        if (known.contains(n)) out.add(n);");
    a.println("      }");
    a.println("    }");
    a.println("    for (String n : known) {");
    a.println("      int p = 0;");
    a.println("      while (p < body.length()) {");
    a.println("        int at = body.indexOf(n, p);");
    a.println("        if (at < 0) break;");
    a.println("        boolean left = at == 0 || !Character.isJavaIdentifierPart(body.charAt(at - 1));");
    a.println("        int rgt = at + n.length();");
    a.println("        boolean right = rgt >= body.length() || !Character.isJavaIdentifierPart(body.charAt(rgt));");
    a.println("        if (left && right) out.add(n);");
    a.println("        p = at + 1;");
    a.println("      }");
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
    a.println("    LinkedHashSet<String> s = new LinkedHashSet<String>();");
    a.println("    s.addAll(analysed);");
    a.println("    return new ArrayList<String>(s);");
    a.println("  }");
    a.println("  public static String codeOf(List<String> analysed, List<String> hitUnits, Set<String> must, int floor) {");
    a.println("    if (!hitUnits.isEmpty()) return \"1\";");
    a.println("    ArrayList<String> opened = new ArrayList<String>(analysed);");
    a.println("    for (String m : must) {");
    a.println("      if (m == null) continue;");
    a.println("      if (!opened.contains(m)) return \"1\";");
    a.println("    }");
    a.println("    return \"0\";");
    a.println("  }");
    a.println("}");
  }
}
END_TINT
bash /app/assemble.bash
