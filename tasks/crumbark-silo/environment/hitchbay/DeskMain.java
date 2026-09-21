public class DeskMain {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.exit(2);
        }
        String verb = args[0];
        String[] rest = new String[Math.max(0, args.length - 1)];
        if (args.length > 1) {
            System.arraycopy(args, 1, rest, 0, rest.length);
        }
        if ("lade".equals(verb)) {
            StowRun.main(rest);
        } else if ("wake".equals(verb)) {
            StirRun.main(rest);
        } else if ("pull".equals(verb)) {
            YankRun.main(rest);
        } else if ("nick".equals(verb)) {
            CutRun.main(rest);
        } else {
            System.exit(2);
        }
    }
}
