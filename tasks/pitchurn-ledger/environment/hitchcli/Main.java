public class Main {
  public static void main(String[] a) throws Exception {
    if (a.length == 0) {
      System.err.println("usage");
      System.exit(2);
    }
    String cmd = a[0];
    int rc = 0;
    if (cmd.equals("anneal")) {
      rc = WalkRun.run();
    } else if (cmd.equals("stow")) {
      rc = StowRun.run(a[1]);
    } else if (cmd.equals("draw")) {
      rc = DrawRun.run(a[1], a[2]);
    } else if (cmd.equals("census")) {
      rc = CardRun.run();
    } else {
      rc = 2;
    }
    System.exit(rc);
  }
}
