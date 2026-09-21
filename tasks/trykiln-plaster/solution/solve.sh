#!/bin/bash
set -euo pipefail

cat > /app/hopsrc/imprint/imprint.go << 'END_IMPRINT'
package imprint

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"kilnbench/hopsrc/vat"
)

const migDir = "/app/inkstack/migrations"

func Imprint(vatPath string) error {
	path := strings.TrimSpace(vatPath)
	if path == "" {
		focus, err := os.ReadFile("/app/hearth/focus.txt")
		if err != nil {
			return err
		}
		path = strings.TrimSpace(string(focus))
	}
	path = filepath.Clean(path)
	return applyAll(path)
}

func applyAll(vatPath string) error {
	matches, err := listSQL(migDir)
	if err != nil {
		return err
	}
	st, err := vat.Parse(vatPath)
	if err != nil {
		st = &vat.Store{Table: "tries", Cols: []string{}, Rows: nil}
	}
	for _, m := range matches {
		stem := vat.Stem(m)
		if st.HasApplied(stem) {
			continue
		}
		body, err := os.ReadFile(m)
		if err != nil {
			return err
		}
		if err := runSQL(st, string(body)); err != nil {
			return fmt.Errorf("%s: %w", stem, err)
		}
		st.Applied = append(st.Applied, stem)
	}
	if err := requireApplied(st, matches); err != nil {
		return err
	}
	return st.Write(vatPath)
}

func listSQL(dir string) ([]string, error) {
	matches, err := filepath.Glob(filepath.Join(dir, "*.sql"))
	if err != nil {
		return nil, err
	}
	sort.Strings(matches)
	return matches, nil
}

func requireApplied(st *vat.Store, matches []string) error {
	for _, m := range matches {
		stem := vat.Stem(m)
		if !st.HasApplied(stem) {
			return fmt.Errorf("missing stem %s", stem)
		}
	}
	return nil
}

func runSQL(st *vat.Store, body string) error {
	for _, raw := range strings.Split(body, ";") {
		line := strings.Join(strings.Fields(raw), " ")
		if line == "" {
			continue
		}
		u := strings.ToUpper(line)
		switch {
		case strings.HasPrefix(u, "CREATE TABLE"):
			rest := strings.TrimSpace(line[len("CREATE TABLE"):])
			name, cols, ok := parseCreate(rest)
			if !ok {
				return fmt.Errorf("create parse")
			}
			st.Table = name
			st.Cols = cols
			if len(st.Rows) == 0 {
				row := []string{}
				for _, c := range cols {
					if c == "id" {
						row = append(row, "1")
					} else if c == "label" {
						row = append(row, "boot")
					} else {
						row = append(row, "0")
					}
				}
				st.Rows = [][]string{row}
			}
		case strings.Contains(u, "ADD COLUMN"):
			idx := strings.Index(u, "ADD COLUMN")
			col := strings.Fields(line[idx+len("ADD COLUMN"):])
			if len(col) == 0 {
				return fmt.Errorf("add column")
			}
			st.AddCol(foldIdent(col[0]))
		}
	}
	return nil
}

func parseCreate(rest string) (string, []string, bool) {
	i := strings.Index(rest, "(")
	j := strings.Index(rest, ")")
	if i < 0 || j < 0 || j <= i {
		return "", nil, false
	}
	name := strings.TrimSpace(rest[:i])
	inner := rest[i+1 : j]
	parts := strings.Split(inner, ",")
	cols := []string{}
	for _, p := range parts {
		p = strings.TrimSpace(p)
		if p == "" {
			continue
		}
		cols = append(cols, foldIdent(p))
	}
	name = foldIdent(name)
	return name, cols, name != "" && len(cols) > 0
}

func foldIdent(s string) string {
	s = strings.TrimSpace(s)
	for len(s) >= 2 {
		a, b := s[0], s[len(s)-1]
		if (a == '"' && b == '"') || (a == '`' && b == '`') {
			s = s[1 : len(s)-1]
			continue
		}
		break
	}
	return s
}
END_IMPRINT

cat > /app/claybin/emit.go << 'END_EMIT'
package claybin

import (
	"fmt"
	"strings"

	"kilnbench/hopsrc/vat"
)

const src = "/app/vats/plaster.vat"
const dst = "/app/vats/worker.vat"
const migDir = "/app/inkstack/migrations"

func EmitWorker() error {
	if err := headsAlign(src); err != nil {
		return err
	}
	st, err := vat.Parse(src)
	if err != nil {
		return err
	}
	if !st.HasCol("attempt_slot") {
		return fmt.Errorf("source lags ledger")
	}
	return vat.CopyFile(src, dst)
}

func sourceHead(path string) (string, error) {
	st, err := vat.Parse(path)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(st.LastApplied()), nil
}

func ledgerHead() (string, error) {
	return vat.LedgerHead(migDir)
}

func headsAlign(srcPath string) error {
	got, err := sourceHead(srcPath)
	if err != nil {
		return err
	}
	want, err := ledgerHead()
	if err != nil {
		return err
	}
	if got != want {
		return fmt.Errorf("source lags ledger")
	}
	return nil
}
END_EMIT

cat > /app/scorepit/score.go << 'END_SCORE'
package scorepit

import (
	"fmt"
	"os"

	"kilnbench/hopsrc/vat"
)

const worker = "/app/vats/worker.vat"
const okPath = "/app/vats/assay.ok"
const migDir = "/app/inkstack/migrations"

func ScoreWorker() int {
	st, err := vat.Parse(worker)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	fmt.Printf("schema_version=%s\n", st.LastApplied())
	if !headOK(st) {
		_ = os.Remove(okPath)
		return 1
	}
	if len(st.Cols) < 3 {
		_ = os.Remove(okPath)
		return 1
	}
	if !st.HasCol("attempt_slot") {
		fmt.Fprintln(os.Stderr, "unknown-column: attempt_slot")
		return 1
	}
	_ = os.WriteFile(okPath, []byte("ok\n"), 0644)
	return 0
}

func headOK(st *vat.Store) bool {
	head, err := vat.LedgerHead(migDir)
	if err != nil {
		return false
	}
	return st.LastApplied() == head
}
END_SCORE

mkdir -p /app/bin
/usr/local/go/bin/go build -C /app -o /app/bin/kilncli ./kilncli
/app/bin/kilncli impress /app/vats/plaster.vat
/app/bin/kilncli spill
/app/bin/kilncli assay
