public class PauseCue {
    public static void nap() {
        try {
            Thread.sleep(20L);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
