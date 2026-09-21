import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class YankRun {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.exit(2);
        }
        byte[] id = hex(args[0]);
        Path silo = Paths.get("/app/silo");
        byte[] got = MistSpan.tint_k(silo, id);
        if (got.length == 0 || allZero(got)) {
            PauseCue.nap();
            got = MistSpan.tint_k(silo, id);
        }
        Files.write(Paths.get("/tmp/crumbark-pull.bin"), got);
        System.out.write(got);
    }

    static boolean allZero(byte[] a) {
        for (byte v : a) {
            if (v != 0) {
                return false;
            }
        }
        return a.length > 0;
    }

    static byte[] hex(String s) {
        int n = s.length() / 2;
        byte[] out = new byte[n];
        for (int i = 0; i < n; i++) {
            out[i] = (byte) Integer.parseInt(s.substring(i * 2, i * 2 + 2), 16);
        }
        return out;
    }
}
