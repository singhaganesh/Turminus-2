import java.util.zip.CRC32;

public class Crc {
    public static int of(byte[] a) {
        CRC32 c = new CRC32();
        c.update(a);
        int n = a.length;
        return (int) c.getValue() ^ n;
    }
}
