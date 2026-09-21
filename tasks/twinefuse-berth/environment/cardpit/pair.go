package cardpit

import (
	"os"
	"path/filepath"
	"strings"

	"berth.local/twinefuse/netsrc"
)

func NPair(dir string, n *netsrc.Net) error {
	ents, err := os.ReadDir(dir)
	if err != nil {
		return err
	}
	for _, ent := range ents {
		if ent.IsDir() || !strings.HasSuffix(ent.Name(), ".cue") {
			continue
		}
		body, err := os.ReadFile(filepath.Join(dir, ent.Name()))
		if err != nil {
			return err
		}
		left, right, origin := "", "", ""
		for _, line := range strings.Split(string(body), "\n") {
			line = strings.TrimSpace(line)
			if line == "" || !strings.Contains(line, "=") {
				continue
			}
			k, v, _ := strings.Cut(line, "=")
			k = strings.TrimSpace(k)
			v = strings.TrimSpace(v)
			switch k {
			case "left":
				left = v
			case "right":
				right = v
			case "origin":
				origin = v
			}
		}
		if origin == "scrapped" {
			continue
		}
		if left != "" && origin != "" {
			n.Join(left, origin)
		}
		if right != "" {
			n.Add(right)
		}
	}
	return nil
}
