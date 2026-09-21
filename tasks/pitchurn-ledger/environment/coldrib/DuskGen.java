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
    a.println("    Path[] bags = new Path[] {");
    a.println("      live,");
    a.println("      Paths.get(\"/app/urnbay/hot/idx.tsv\"),");
    a.println("      Paths.get(\"/app/urnbay/cold/idx.tsv\"),");
    a.println("      Paths.get(\"/app/urnbay/keep/idx.tsv\")");
    a.println("    };");
    a.println("    for (Path p : bags) {");
    a.println("      if (java.nio.file.Files.exists(p)) sb.append(java.nio.file.Files.readString(p));");
    a.println("    }");
    a.println("    java.nio.file.Files.writeString(live, sb.toString());");
    a.println("    System.out.println(\"walked\");");
    a.println("  }");
    a.println("}");
  }
}
