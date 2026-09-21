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
	focus, err := os.ReadFile("/app/hearth/focus.txt")
	if err == nil {
		vatPath = strings.TrimSpace(string(focus))
	}
	return applyAll(vatPath)
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
				row := make([]string, len(cols))
				for i := range row {
					if cols[i] == "id" {
						row[i] = "1"
					} else if cols[i] == "label" {
						row[i] = "boot"
					} else {
						row[i] = "0"
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
			st.AddCol(col[0])
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
	cols := make([]string, 0, len(parts))
	for _, p := range parts {
		p = strings.TrimSpace(p)
		if p == "" {
			continue
		}
		cols = append(cols, p)
	}
	return name, cols, name != "" && len(cols) > 0
}
