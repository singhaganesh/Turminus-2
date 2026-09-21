import java.security.MessageDigest;

public class Dig {
    public static String mill_stamp() {
        return "rel-3";
    }

    public static String mix_id(byte[] sheet) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(sheet);
            md.update(mill_stamp().getBytes("UTF-8"));
            byte[] d = md.digest();
            StringBuilder sb = new StringBuilder();
            for (byte b : d) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return "none";
        }
    }
}
