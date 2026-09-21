package spoolkit

import (
	"bufio"
	"errors"
	"os"
	"strings"

	"loft.local/wickpane/celltyp"
)

var ErrReject = errors.New("reject")

func Scan(path string) ([]celltyp.Row, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	var rows []celltyp.Row
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		line := strings.TrimSpace(sc.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) == 0 {
			continue
		}
		if parts[0] == "BAD" {
			return nil, ErrReject
		}
		if len(parts) < 4 {
			continue
		}
		rows = append(rows, celltyp.Row{Kind: parts[0], Mod: parts[2], Fn: parts[3]})
	}
	return rows, sc.Err()
}
