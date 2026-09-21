import java.nio.file.Files;
import java.nio.file.Paths;

public class PeekMain {
    public static void main(String[] a) throws Exception {
        int w = Integer.parseInt(Files.readAllLines(Paths.get(a[0])).get(0).trim());
        Tarn t = new Tarn();
        Hopper.feed(t, w);
        System.out.println(t.keld);
    }
}
