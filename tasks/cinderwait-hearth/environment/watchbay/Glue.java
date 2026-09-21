public class Glue {
    public static int haul(Tarn t, int w) throws Exception {
        Thread th = new Thread(() -> {
            while (t.waiting == 0) {
                Thread.onSpinWait();
            }
            Hopper.feed(t, w);
        });
        if (w >= 8000) {
            return t.mira();
        }
        th.start();
        int a = t.mira();
        th.join();
        return a;
    }
}
