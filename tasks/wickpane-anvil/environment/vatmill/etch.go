package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"

	"loft.local/wickpane/pantryc"
	"loft.local/wickpane/spoolkit"
)

func runEtch() int {
	dir := "/app/crumbay"
	outPath := "/app/loomwell/etch.json"
	entries, err := os.ReadDir(dir)
	if err != nil {
		return 1
	}
	out := map[string]string{}
	for _, e := range entries {
		if e.IsDir() || !strings.HasSuffix(e.Name(), ".stk") {
			continue
		}
		rows, err := spoolkit.Scan(filepath.Join(dir, e.Name()))
		if err != nil {
			return 1
		}
		stem := strings.TrimSuffix(e.Name(), ".stk")
		out[stem] = pantryc.Join(pipeBack(pipeFront(rows)))
	}
	blob, err := json.MarshalIndent(out, "", "  ")
	if err != nil {
		return 1
	}
	if err := os.MkdirAll(filepath.Dir(outPath), 0o755); err != nil {
		return 1
	}
	if err := os.WriteFile(outPath, append(blob, '\n'), 0o644); err != nil {
		return 1
	}
	return 0
}
