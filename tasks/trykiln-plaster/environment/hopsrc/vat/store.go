package vat

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

const magic = "KILNVAT 1"

type Store struct {
	Applied []string
	Table   string
	Cols    []string
	Rows    [][]string
}

func Parse(path string) (*Store, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	s := &Store{}
	sc := bufio.NewScanner(f)
	if !sc.Scan() {
		return nil, fmt.Errorf("empty vat")
	}
	if strings.TrimSpace(sc.Text()) != magic {
		return nil, fmt.Errorf("bad magic")
	}
	for sc.Scan() {
		line := strings.TrimSpace(sc.Text())
		if line == "" {
			continue
		}
		switch {
		case strings.HasPrefix(line, "applied:"):
			s.Applied = append(s.Applied, strings.TrimPrefix(line, "applied:"))
		case strings.HasPrefix(line, "table:"):
			s.Table = strings.TrimPrefix(line, "table:")
		case strings.HasPrefix(line, "cols:"):
			s.Cols = strings.Split(strings.TrimPrefix(line, "cols:"), ",")
		case strings.HasPrefix(line, "row:"):
			s.Rows = append(s.Rows, strings.Split(strings.TrimPrefix(line, "row:"), ","))
		}
	}
	return s, sc.Err()
}

func (s *Store) Write(path string) error {
	var b strings.Builder
	b.WriteString(magic)
	b.WriteByte('\n')
	for _, a := range s.Applied {
		b.WriteString("applied:")
		b.WriteString(a)
		b.WriteByte('\n')
	}
	b.WriteString("table:")
	b.WriteString(s.Table)
	b.WriteByte('\n')
	b.WriteString("cols:")
	b.WriteString(strings.Join(s.Cols, ","))
	b.WriteByte('\n')
	for _, r := range s.Rows {
		b.WriteString("row:")
		b.WriteString(strings.Join(r, ","))
		b.WriteByte('\n')
	}
	return os.WriteFile(path, []byte(b.String()), 0644)
}

func (s *Store) LastApplied() string {
	if len(s.Applied) == 0 {
		return ""
	}
	return s.Applied[len(s.Applied)-1]
}

func (s *Store) HasApplied(stem string) bool {
	for _, a := range s.Applied {
		if a == stem {
			return true
		}
	}
	return false
}

func (s *Store) HasCol(name string) bool {
	for _, c := range s.Cols {
		if c == name {
			return true
		}
	}
	return false
}

func (s *Store) AddCol(name string) {
	if s.HasCol(name) {
		return
	}
	s.Cols = append(s.Cols, name)
	for i := range s.Rows {
		s.Rows[i] = append(s.Rows[i], "0")
	}
}

func LedgerHead(migDir string) (string, error) {
	matches, err := filepath.Glob(filepath.Join(migDir, "*.sql"))
	if err != nil {
		return "", err
	}
	if len(matches) == 0 {
		return "", fmt.Errorf("no sql")
	}
	sort.Strings(matches)
	base := filepath.Base(matches[len(matches)-1])
	return strings.TrimSuffix(base, ".sql"), nil
}

func Stem(path string) string {
	base := filepath.Base(path)
	return strings.TrimSuffix(base, ".sql")
}

func CopyFile(src, dst string) error {
	b, err := os.ReadFile(src)
	if err != nil {
		return err
	}
	return os.WriteFile(dst, b, 0644)
}
