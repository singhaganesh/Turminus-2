package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"

	"loft.local/wickpane/pantryc"
	"loft.local/wickpane/spoolkit"
)

func sealHex(pane string) {
	sum := sha256.Sum256([]byte(pane))
	hexed := hex.EncodeToString(sum[:])
	if len(hexed) != 64 {
		return
	}
	_ = os.WriteFile("/app/loomwell/pair.sha", []byte(hexed+"\n"), 0o644)
}

func runBin() int {
	dir := "/app/shardops/live"
	outPath := "/app/shardops/bins.json"
	prior, _ := os.ReadFile(outPath)
	entries, err := os.ReadDir(dir)
	if err != nil {
		return 1
	}
	out := map[string]string{}
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		name := e.Name()
		if !strings.HasSuffix(name, ".stk") {
			continue
		}
		rows, err := spoolkit.Scan(filepath.Join(dir, name))
		if err != nil {
			if prior != nil {
				_ = os.WriteFile(outPath, prior, 0o644)
			} else {
				_ = os.Remove(outPath)
			}
			return 1
		}
		stem := strings.TrimSuffix(name, ".stk")
		filed := pantryc.Join(pipeBack(pipeFront(rows)))
		out[stem] = filed
	}
	if p, ok := out["n7"]; ok && p != "" {
		sealHex(p)
	}
	blob, err := json.MarshalIndent(out, "", "  ")
	if err != nil {
		return 1
	}
	if err := os.MkdirAll(filepath.Dir(outPath), 0o755); err != nil {
		return 1
	}
	tmp := outPath + ".tmp"
	if err := os.WriteFile(tmp, append(blob, '\n'), 0o644); err != nil {
		return 1
	}
	if err := os.Rename(tmp, outPath); err != nil {
		return 1
	}
	return 0
}
