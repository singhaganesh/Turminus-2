import java.nio.charset.StandardCharsets;

public class Store {
    public static byte[] pack(String stamp, String inc) {
        String body = stamp + "\n" + inc;
        return body.getBytes(StandardCharsets.UTF_8);
    }

    public static String stamp_of(byte[] stored) {
        String s = new String(stored, StandardCharsets.UTF_8);
        int n = s.indexOf('\n');
        if (n < 0) {
            return "";
        }
        return s.substring(0, n);
    }

    public static String inc_of(byte[] stored) {
        String s = new String(stored, StandardCharsets.UTF_8);
        int n = s.indexOf('\n');
        if (n < 0) {
            return s;
        }
        return s.substring(n + 1);
    }
}
