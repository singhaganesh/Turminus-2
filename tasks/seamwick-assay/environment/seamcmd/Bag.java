import java.security.MessageDigest;
import java.util.*;
public class Bag {
  public static String q(String s) {
    StringBuilder b = new StringBuilder();
    b.append('"');
    for (int i = 0; i < s.length(); i++) {
      char c = s.charAt(i);
      if (c == '\\' || c == '"') b.append('\\');
      b.append(c);
    }
    b.append('"');
    return b.toString();
  }
  public static String hex(byte[] p) throws Exception {
    MessageDigest md = MessageDigest.getInstance("SHA-256");
    byte[] d = md.digest(p);
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < d.length; i++) {
      int v = d[i] & 0xff;
      if (v < 16) sb.append('0');
      sb.append(Integer.toHexString(v));
    }
    return sb.toString();
  }
  public static String joinComma(Collection<String> xs) {
    StringBuilder b = new StringBuilder();
    boolean first = true;
    for (String x : xs) {
      if (!first) b.append(',');
      first = false;
      b.append(q(x));
    }
    return b.toString();
  }
}
