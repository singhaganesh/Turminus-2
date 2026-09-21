import java.util.List;

public class SlotEmit {
    public static String op_inner(String sheet) {
        String stem = SheetScan.stem(sheet);
        List<SheetScan.Row> rows = SheetScan.rows(sheet);
        StringBuilder fn = new StringBuilder();
        fn.append("static void skim_").append(stem).append("(const unsigned char *p, size_t n, FILE *out) {\n");
        fn.append("  size_t o = 0;\n");
        for (SheetScan.Row r : rows) {
            fn.append("  unsigned ").append(r.name).append(" = 0;\n");
        }
        for (SheetScan.Row r : rows) {
            if (r.nested) {
                continue;
            }
            if ("u8".equals(r.kind)) {
                fn.append("  if (o < n) { ").append(r.name).append(" = p[o++]; }\n");
            } else if ("u16be".equals(r.kind)) {
                fn.append("  if (o + 1 < n) { ").append(r.name).append(" = ((unsigned)p[o] << 8) | p[o + 1]; o += 2; }\n");
            }
        }
        fn.append("  fputc('{', out);\n");
        for (int i = 0; i < rows.size(); i++) {
            SheetScan.Row r = rows.get(i);
            if (i > 0) {
                fn.append("  fputc(',', out);\n");
            }
            if (r.nested) {
                fn.append("  fprintf(out, \"\\\"").append(r.name).append("\\\":\\\"\\\"\");\n");
            } else {
                fn.append("  fprintf(out, \"\\\"").append(r.name).append("\\\":\\\"%u\\\"\", ").append(r.name).append(");\n");
            }
        }
        fn.append("  fputc('}', out);\n");
        fn.append("}\n");
        return fn.toString();
    }
}
