#!/bin/bash
set -euo pipefail
cat > /app/oxbind/seal.go << 'ENDSEAL'
package oxbind

import "loft.local/lanternix/packbay/store"

var chart map[string]store.Spec

func Clip(bag map[string]store.Spec) map[string]store.Spec {
	out := make(map[string]store.Spec, len(bag))
	for k, v := range bag {
		cp := v
		cp.Slots = append([]string(nil), v.Slots...)
		out[k] = cp
	}
	return out
}

func Boot() {
	chart = Clip(store.Bag())
}

func Read(tag string) (store.Spec, bool) {
	live := store.Bag()
	if s, ok := live[tag]; ok {
		return s, true
	}
	if chart != nil {
		if s, ok := chart[tag]; ok {
			return s, true
		}
	}
	return store.Spec{}, false
}
ENDSEAL

cat > /app/packbay/fetch.go << 'ENDFETCH'
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
ENDFETCH

cat > /app/milldesk/spin.go << 'ENDSPIN'
package main

import (
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"
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
	units, err := listUnits("/app/packbay/units")
	if err != nil {
		return 2
	}
	if err := writeFill(units); err != nil {
		return 2
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
		"LAN_WARM_01":  "unita",
		"LAN_BEAM_44":  "unitb",
		"LAN_FLASH_9C": "unitc",
		"LAN_GLOW_2B":  "unitd",
	}
	for _, c := range cards {
		dir, ok := roots[c.id]
		if !ok {
			continue
		}
		trimmed := make([]string, 0, len(c.slots))
		for _, s := range c.slots {
			s = strings.TrimSpace(s)
			if s != "" {
				trimmed = append(trimmed, s)
			}
		}
		body := unitSource(dir, c.id, trimmed)
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
		quoted = append(quoted, strconv.Quote(s))
	}
	return "package " + pkg + "\n\nimport \"loft.local/lanternix/packbay/store\"\n\nfunc Load() {\n\tstore.Offer(" + strconv.Quote(id) + ", store.Spec{Slots: []string{" + strings.Join(quoted, ", ") + "}})\n}\n"
}

func listUnits(root string) ([]string, error) {
	ents, err := os.ReadDir(root)
	if err != nil {
		return nil, err
	}
	var units []string
	for _, e := range ents {
		if e.IsDir() {
			units = append(units, e.Name())
		}
	}
	sort.Strings(units)
	return units, nil
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
ENDSPIN
