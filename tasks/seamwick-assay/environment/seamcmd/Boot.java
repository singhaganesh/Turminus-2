public class Boot {
  public static void main(String[] a) throws Exception {
    if (a.length == 0) {
      System.err.println("usage");
      System.exit(2);
    }
    String cmd = a[0];
    int rc = 0;
    if (cmd.equals("nudge")) {
      rc = Nudge.run();
    } else if (cmd.equals("flood")) {
      rc = Flood.run();
    } else if (cmd.equals("sheet")) {
      rc = Sheet.run();
    } else {
      rc = 2;
    }
    System.exit(rc);
  }
}
