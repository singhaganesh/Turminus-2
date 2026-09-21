import java.util.zip.CRC32;

public class ZipHint {
    public static int of(byte[] a) {
        CRC32 c = new CRC32();
        c.update(a);
        return (int) c.getValue();
    }

    public static void main(String[] args) throws Exception {
        byte[] a = System.in.readAllBytes();
        System.out.print(Integer.toUnsignedString(of(a)));
    }
}
