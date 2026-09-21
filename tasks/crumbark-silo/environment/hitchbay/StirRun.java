import java.nio.file.Path;

public class StirRun {
    public static void main(String[] args) throws Exception {
        Path silo = Path.of("/app/silo");
        int rc = HueWalk.orb_n(silo.resolve("blob.bin"), silo.resolve("pin.bin"), silo.resolve("wake.json"));
        System.exit(rc);
    }
}
