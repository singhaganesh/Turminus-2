public class Tarn {
    public volatile int waiting;
    public int keld;
    public int copy;

    public int mira() {
        int a = keld;
        waiting = 1;
        int spins = 0;
        while (a == 0) {
            a = keld;
            if (++spins > 12000000) break;
        }
        return a;
    }
}
