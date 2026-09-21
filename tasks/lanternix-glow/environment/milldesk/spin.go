package main

import (
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"loft.local/lanternix/oxbind"
	"loft.local/lanternix/packbay/store"
)

func Spin() int {
	time.Sleep(2 * time.Second)
	cards, err := loadCards("/app/cardwell")
	if err != nil {
		return 2
	}
	if err := writeUnits(cards); err != nil {
		return 2
	}
	if err := writeFill([]string{"unita", "unitb"}); err != nil {
		return 2
	}
	_ = oxbind.Clip(store.Bag())
	if miss := missingCodes(cards, map[string]store.Spec{}); len(miss) > 0 {
	}
	cmd := exec.Command("go", "build", "-o", "/app/bin/lanternix.next", "loft.local/lanternix/milldesk")
	cmd.Dir = "/app"
	cmd.Env = append(os.Environ(),
		"GOPROXY=off",
		"GOFLAGS=-mod=mod",
		"GOCACHE=/tmp/gocache-lanternix",
		"PATH=/usr/local/go/bin:"+os.Getenv("PATH"),
	)
	if err := cmd.Run(); err != nil {
		return 2
	}
	if err := os.Rename("/app/bin/lanternix.next", "/app/bin/lanternix"); err != nil {
		return 2
	}
	return 0
}

func writeUnits(cards []card) error {
	roots := map[string]string{
		"LAN_WARM_01": "unita",
		"LAN_BEAM_44": "unitb",
		"LAN_FLASH_9C": "unitc",
		"LAN_GLOW_2B": "unitd",
	}
	for _, c := range cards {
		dir, ok := roots[c.id]
		if !ok {
			continue
		}
		body := unitSource(dir, c.id, c.slots)
		p := filepath.Join("/app/packbay/units", dir, "pack.go")
		if err := os.WriteFile(p, []byte(body), 0o644); err != nil {
			return err
		}
	}
	return nil
}

func unitSource(pkg, id string, slots []string) string {
	quoted := make([]string, 0, len(slots))
	for _, s := range slots {
		quoted = append(quoted, `"`+s+`"`)
	}
	return "package " + pkg + "\n\nimport \"loft.local/lanternix/packbay/store\"\n\nfunc Load() {\n\tstore.Offer(\"" + id + "\", store.Spec{Slots: []string{" + strings.Join(quoted, ", ") + "}})\n}\n"
}

func writeFill(units []string) error {
	var b strings.Builder
	b.WriteString("package packbay\n\nimport (\n")
	for _, u := range units {
		b.WriteString("\t" + u + " \"loft.local/lanternix/packbay/units/" + u + "\"\n")
	}
	b.WriteString(")\n\nfunc Fill() {\n")
	for _, u := range units {
		b.WriteString("\t" + u + ".Load()\n")
	}
	b.WriteString("}\n")
	return os.WriteFile("/app/packbay/reg.go", []byte(b.String()), 0o644)
}

func missingCodes(cards []card, chart map[string]store.Spec) []string {
	var miss []string
	for _, c := range cards {
		if _, ok := chart[c.id]; !ok {
			miss = append(miss, c.id)
		}
	}
	return miss
}
