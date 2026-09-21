import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class LoomCue {
    static final class Step {
        String name;
        int compute;
        int durable;
    }

    public static List<String> rib_q(Path a) throws Exception {
        List<Step> steps = new ArrayList<Step>();
        for (String line : Files.readAllLines(a)) {
            String s = line.trim();
            if (s.isEmpty() || s.startsWith("#")) {
                continue;
            }
            String[] p = s.split("\\s+");
            if (p.length < 3) {
                continue;
            }
            Step st = new Step();
            st.name = p[0];
            st.compute = Integer.parseInt(p[1]);
            st.durable = Integer.parseInt(p[2]);
            steps.add(st);
        }
        steps.sort(Comparator.comparingInt(x -> x.compute));
        List<String> names = new ArrayList<String>();
        for (Step st : steps) {
            names.add(st.name);
        }
        return names;
    }

    public static void main(String[] args) throws Exception {
        Path recipe = Paths.get("/app/recipit/steps.loom");
        List<String> names = rib_q(recipe);
        StringBuilder sb = new StringBuilder();
        sb.append("public class ForceSeq {\n");
        sb.append("    public static String[] names() {\n");
        sb.append("        return new String[] {");
        for (int i = 0; i < names.size(); i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append("\"");
            sb.append(names.get(i));
            sb.append("\"");
        }
        sb.append("};\n");
        sb.append("    }\n");
        sb.append("}\n");
        Files.writeString(Paths.get("/app/recipit/ForceSeq.java"), sb.toString());
    }
}
