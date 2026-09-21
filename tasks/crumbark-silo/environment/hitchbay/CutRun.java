import java.nio.file.Paths;

public class CutRun {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.exit(2);
        }
        try {
            StowRun.run(Paths.get(args[0]), true);
        } catch (StowRun.CutErr e) {
            System.exit(0);
        }
    }
}
