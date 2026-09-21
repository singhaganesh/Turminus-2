package readcue

import (
	"os"
	"strings"
)

type Rec struct {
	Id  string
	Tok string
}

func Scan(path string) ([]Rec, error) {
	body, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var out []Rec
	for _, line := range strings.Split(string(body), "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		id, tok, ok := strings.Cut(line, " ")
		if !ok {
			continue
		}
		out = append(out, Rec{Id: strings.TrimSpace(id), Tok: strings.TrimSpace(tok)})
	}
	return out, nil
}
