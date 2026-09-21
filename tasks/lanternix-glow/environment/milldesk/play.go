package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"

	"loft.local/lanternix/oxbind"
	"loft.local/lanternix/packbay"
)

func Play(lampPath string) int {
	oxbind.Boot()
	code, vals, err := parseLamp(lampPath)
	if err != nil {
		return 2
	}
	packbay.Pull(code)
	if !cardsCovered() {
		return 2
	}
	spec, ok := oxbind.Read(code)
	outPath := "/app/glowbank/readout.json"
	if !ok {
		_ = writeJSON(outPath, map[string]any{"code": "void", "slots": map[string]string{}})
		return 1
	}
	slots := map[string]string{}
	for _, name := range spec.Slots {
		slots[name] = vals[name]
	}
	_ = writeJSON(outPath, map[string]any{"code": code, "slots": slots})
	return 0
}

func cardsCovered() bool {
	cards, err := loadCards("/app/cardwell")
	if err != nil {
		return false
	}
	for _, c := range cards {
		if _, ok := oxbind.Read(c.id); !ok {
			return false
		}
	}
	return true
}

func writeJSON(path string, doc map[string]any) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	raw, err := json.MarshalIndent(doc, "", "  ")
	if err != nil {
		return err
	}
	raw = append(raw, '\n')
	return os.WriteFile(path, raw, 0o644)
}

func parseLamp(path string) (string, map[string]string, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return "", nil, err
	}
	code := ""
	vals := map[string]string{}
	for _, line := range strings.Split(string(raw), "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		if strings.HasPrefix(line, "CODE ") {
			code = strings.TrimSpace(strings.TrimPrefix(line, "CODE "))
			continue
		}
		k, v, ok := strings.Cut(line, "=")
		if ok {
			vals[strings.TrimSpace(k)] = strings.TrimSpace(v)
		}
	}
	return code, vals, nil
}

type card struct {
	id    string
	slots []string
}

func loadCards(dir string) ([]card, error) {
	ents, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}
	var out []card
	for _, e := range ents {
		if e.IsDir() || !strings.HasSuffix(e.Name(), ".card") {
			continue
		}
		raw, err := os.ReadFile(filepath.Join(dir, e.Name()))
		if err != nil {
			return nil, err
		}
		c := card{}
		for _, line := range strings.Split(string(raw), "\n") {
			line = strings.TrimSpace(line)
			if strings.HasPrefix(line, "id:") {
				c.id = strings.TrimSpace(strings.TrimPrefix(line, "id:"))
			}
			if strings.HasPrefix(line, "slots:") {
				parts := strings.Split(strings.TrimSpace(strings.TrimPrefix(line, "slots:")), ",")
				for _, p := range parts {
					c.slots = append(c.slots, p)
				}
			}
		}
		if c.id != "" {
			out = append(out, c)
		}
	}
	return out, nil
}
