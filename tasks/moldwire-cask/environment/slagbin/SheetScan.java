import java.util.ArrayList;
import java.util.List;

public class SheetScan {
    public static final class Row {
        public final String name;
        public final String kind;
        public final boolean nested;

        Row(String name, String kind, boolean nested) {
            this.name = name;
            this.kind = kind;
            this.nested = nested;
        }
    }

    public static String stem(String sheet) {
        for (String line : sheet.split("\n")) {
            String t = line.trim();
            if (t.startsWith("NAME ")) {
                return t.substring(5).trim();
            }
        }
        return "";
    }

    public static List<Row> rows(String sheet) {
        List<Row> out = new ArrayList<Row>();
        boolean nested = false;
        for (String line : sheet.split("\n")) {
            String t = line.trim();
            if (t.startsWith("GROUP ")) {
                nested = true;
            } else if (t.equals("END")) {
                nested = false;
            } else if (t.startsWith("FIELD ")) {
                String rest = t.substring(6).trim();
                int sp = rest.indexOf(' ');
                if (sp <= 0) {
                    continue;
                }
                out.add(new Row(rest.substring(0, sp), rest.substring(sp).trim(), nested));
            }
        }
        return out;
    }
}
