import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Rib {
    static final Map<String, String> tab = new LinkedHashMap<String, String>();
    static Class<?> wick() {
        return WickPad.class;
    }

    static void put(String n) {
        tab.put(n, n);
    }

    static String pick(String t) {
        if (tab.containsKey(t)) {
            return t;
        }
        return "fallback";
    }

    static List<String> all() {
        return new ArrayList<String>(tab.keySet());
    }
}
