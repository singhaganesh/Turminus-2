public class Pacer {
    public static void nap() {
        Thread.onSpinWait();
    }
}
