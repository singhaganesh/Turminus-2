import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;

public class Loom {
  public static class Unit {
    public String path;
    public String pkg;
    public String body;
    public String hash;
    public LinkedHashSet<String> defined = new LinkedHashSet<String>();
    public LinkedHashMap<String, String> fps = new LinkedHashMap<String, String>();
    public LinkedHashSet<String> importedUnits = new LinkedHashSet<String>();
    public ArrayList<String[]> hits = new ArrayList<String[]>();
  }

  static final Pattern IFACE = Pattern.compile("interface\\s+([A-Za-z_][A-Za-z0-9_]*)");
  static final Pattern METH = Pattern.compile("void\\s+([A-Za-z_][A-Za-z0-9_]*)\\s*\\(([^)]*)\\)");
  static final Pattern CALL = Pattern.compile("\\.([A-Za-z_][A-Za-z0-9_]*)\\s*\\(([^)]*)\\)");
  static final Pattern IMP = Pattern.compile("import\\s+([A-Za-z_][A-Za-z0-9_.*]*);");
  static final Pattern PKG = Pattern.compile("package\\s+([A-Za-z_][A-Za-z0-9_.]*);");

  public static LinkedHashMap<String, Unit> load(Path root) throws Exception {
    LinkedHashMap<String, Unit> all = new LinkedHashMap<String, Unit>();
    if (!Files.exists(root)) return all;
    Files.walk(root).filter(p -> p.toString().endsWith(".u")).sorted().forEach(p -> {
      try {
        Unit u = parse(root, p);
        all.put(u.path, u);
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    });
    resolveHits(all);
    return all;
  }

  static Unit parse(Path root, Path p) throws Exception {
    Unit u = new Unit();
    u.path = root.relativize(p).toString().replace('\\', '/');
    u.body = Files.readString(p);
    u.hash = Bag.hex(u.body.getBytes(StandardCharsets.UTF_8));
    Matcher pm = PKG.matcher(u.body);
    u.pkg = pm.find() ? pm.group(1) : "";
    Matcher im = IMP.matcher(u.body);
    while (im.find()) {
      String r = im.group(1);
      if (r.endsWith(".*")) continue;
      u.importedUnits.add(r.replace('.', '/') + ".u");
    }
    Matcher ic = IFACE.matcher(u.body);
    LinkedHashMap<String, String> methods = new LinkedHashMap<String, String>();
    String typeName = null;
    if (ic.find()) {
      typeName = ic.group(1);
      u.defined.add(typeName);
    }
    Matcher mm = METH.matcher(u.body);
    while (mm.find()) {
      String name = mm.group(1);
      String args = mm.group(2).trim();
      int n = args.isEmpty() ? 0 : args.split(",").length;
      methods.put(name, name + ":" + n);
    }
    if (typeName != null) {
      ArrayList<String> parts = new ArrayList<String>(methods.values());
      Collections.sort(parts);
      StringBuilder fp = new StringBuilder();
      for (int i = 0; i < parts.size(); i++) {
        if (i > 0) fp.append(';');
        fp.append(parts.get(i));
      }
      u.fps.put(typeName, fp.toString());
    }
    return u;
  }

  static void resolveHits(LinkedHashMap<String, Unit> all) {
    LinkedHashMap<String, String> methArity = new LinkedHashMap<String, String>();
    for (Unit u : all.values()) {
      for (Map.Entry<String, String> e : u.fps.entrySet()) {
        for (String part : e.getValue().split(";")) {
          if (part.isEmpty()) continue;
          methArity.put(e.getKey() + "#" + part.split(":")[0], part.split(":")[1]);
        }
      }
    }
    for (Unit u : all.values()) {
      Matcher c = CALL.matcher(u.body);
      while (c.find()) {
        String name = c.group(1);
        String args = c.group(2).trim();
        int n = args.isEmpty() ? 0 : splitArgs(args);
        for (Unit def : all.values()) {
          for (String t : def.defined) {
            String want = methArity.get(t + "#" + name);
            if (want == null) continue;
            if (Integer.parseInt(want) != n) {
              u.hits.add(new String[] {u.path, "arity", name});
            }
          }
        }
      }
    }
  }

  static int splitArgs(String args) {
    int n = 1;
    int depth = 0;
    boolean q = false;
    for (int i = 0; i < args.length(); i++) {
      char ch = args.charAt(i);
      if (ch == '"') q = !q;
      else if (!q && ch == '(') depth++;
      else if (!q && ch == ')') depth--;
      else if (!q && depth == 0 && ch == ',') n++;
    }
    return n;
  }
}
