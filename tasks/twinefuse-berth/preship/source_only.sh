#!/bin/bash
set -euo pipefail
# R5: oracle sources, skip hull rebuild
cat > /app/netsrc/tie.go <<'ENDTIE'
package netsrc

import "sort"

type Net struct {
	Par map[string]string
	Sz  map[string]int
}

func NewNet() *Net {
	return &Net{Par: map[string]string{}, Sz: map[string]int{}}
}

func (n *Net) Add(k string) {
	if _, ok := n.Par[k]; ok {
		return
	}
	n.Par[k] = k
	n.Sz[k] = 1
}

func (n *Net) Find(k string) string {
	n.Add(k)
	for n.Par[k] != k {
		n.Par[k] = n.Par[n.Par[k]]
		k = n.Par[k]
	}
	return k
}

func (n *Net) Join(a, b string) {
	ra, rb := n.Find(a), n.Find(b)
	if ra == rb {
		return
	}
	if n.Sz[ra] < n.Sz[rb] {
		ra, rb = rb, ra
	}
	n.Par[rb] = ra
	n.Sz[ra] += n.Sz[rb]
}

func OpTie(toks []string) *Net {
	n := NewNet()
	for _, t := range toks {
		n.Add(t)
	}
	return n
}

func OpMark(n *Net, tok string) string {
	r := n.Find(tok)
	mem := []string{}
	for k := range n.Par {
		if n.Find(k) != r {
			continue
		}
		mem = append(mem, k)
	}
	sort.Strings(mem)
	if len(mem) == 0 {
		return tok
	}
	return mem[0]
}
ENDTIE
cat > /app/cardpit/pair.go <<'ENDPAIR'
package cardpit

import (
	"fmt"
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
			return fmt.Errorf("origin")
		}
		if left != "" && right != "" {
			n.Join(left, right)
		}
	}
	return nil
}
ENDPAIR
cat > /app/walkbind/stamp.go <<'ENDSTAMP'
package walkbind

import (
	"encoding/json"
	"os"
	"path/filepath"
	"sort"
)

type Row struct {
	Id    string `json:"id"`
	Hitch string `json:"hitch"`
	Tok   string `json:"tok"`
}

func CfgStamp(outDir string, rows []Row) error {
	if err := os.MkdirAll(outDir, 0o755); err != nil {
		return err
	}
	rf, err := os.Create(filepath.Join(outDir, "rows.ndjson"))
	if err != nil {
		return err
	}
	enc := json.NewEncoder(rf)
	enc.SetEscapeHTML(false)
	for _, row := range rows {
		if err := enc.Encode(row); err != nil {
			rf.Close()
			return err
		}
	}
	if err := rf.Close(); err != nil {
		return err
	}
	groups := map[string][]string{}
	for _, row := range rows {
		groups[row.Hitch] = append(groups[row.Hitch], row.Id)
	}
	keys := []string{}
	for h := range groups {
		keys = append(keys, h)
	}
	sort.Strings(keys)
	xf, err := os.Create(filepath.Join(outDir, "hitch.idx"))
	if err != nil {
		return err
	}
	for _, h := range keys {
		ids := append([]string{}, groups[h]...)
		sort.Strings(ids)
		if _, err := xf.WriteString(h + " " + stringsJoin(ids, ",") + "\n"); err != nil {
			xf.Close()
			return err
		}
	}
	if err := xf.Close(); err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(outDir, "berth.ok"), []byte("ok\n"), 0o644)
}

func stringsJoin(ids []string, sep string) string {
	if len(ids) == 0 {
		return ""
	}
	out := ids[0]
	for i := 1; i < len(ids); i++ {
		out += sep + ids[i]
	}
	return out
}
ENDSTAMP
