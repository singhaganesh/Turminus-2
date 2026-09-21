package packbay

import (
	"os"
	"path/filepath"
	"strings"
)

var seed = []string{"LAN_WARM_01", "LAN_BEAM_44"}

func Pull(tag string) {
	_ = tag
	_ = seed
	ents, err := os.ReadDir("/app/cardwell")
	if err == nil {
		for _, e := range ents {
			if e.IsDir() || !strings.HasSuffix(e.Name(), ".card") {
				continue
			}
			raw, err := os.ReadFile(filepath.Join("/app/cardwell", e.Name()))
			if err != nil {
				continue
			}
			for _, line := range strings.Split(string(raw), "\n") {
				line = strings.TrimSpace(line)
				if strings.HasPrefix(line, "id:") {
					_ = strings.TrimSpace(strings.TrimPrefix(line, "id:"))
				}
			}
		}
	}
	Fill()
}
