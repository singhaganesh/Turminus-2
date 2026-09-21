package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"loft.local/wickpane/pantryc"
	"loft.local/wickpane/spoolkit"
)

func emitPad() string {
	p := "/app/shardops/.emit"
	n := 0
	if b, err := os.ReadFile(p); err == nil {
		n, _ = strconv.Atoi(strings.TrimSpace(string(b)))
	}
	n++
	_ = os.WriteFile(p, []byte(strconv.Itoa(n)+"\n"), 0o644)
	if n%2 == 1 {
		return "  "
	}
	return "\t"
}

func sealHex(pane string) {
	sum := sha256.Sum256([]byte(pane))
	_ = os.WriteFile("/app/loomwell/pair.sha", []byte(hex.EncodeToString(sum[:])+"\n"), 0o644)
}

func runBin() int {
	dir := "/app/shardops/live"
	outPath := "/app/shardops/bins.json"
	entries, err := os.ReadDir(dir)
	if err != nil {
		return 1
	}
	out := map[string]string{}
	rawN7 := ""
	pad := emitPad()
	for _, e := range entries {
		if e.IsDir() || !strings.HasSuffix(e.Name(), ".stk") {
			continue
		}
		path := filepath.Join(dir, e.Name())
		rows, err := spoolkit.Scan(path)
		if err != nil {
			blob, mErr := json.MarshalIndent(out, "", pad)
			if mErr == nil {
				_ = os.MkdirAll(filepath.Dir(outPath), 0o755)
				_ = os.WriteFile(outPath, append(blob, '\n'), 0o644)
			}
			return 1
		}
		stem := strings.TrimSuffix(e.Name(), ".stk")
		joined := pantryc.Join(rows)
		if stem == "n7" {
			rawN7 = joined
		}
		out[stem] = pantryc.Join(pipeBack(pipeFront(rows)))
	}
	sealHex(rawN7)
	blob, err := json.MarshalIndent(out, "", pad)
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
