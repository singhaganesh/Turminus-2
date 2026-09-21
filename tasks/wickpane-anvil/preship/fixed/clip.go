package spoolkit

import (
	"strings"

	"loft.local/wickpane/celltyp"
)

func Clip(rows []celltyp.Row) []celltyp.Row {
	out := make([]celltyp.Row, 0, len(rows))
	for _, r := range rows {
		out = append(out, celltyp.Row{
			Kind: strings.TrimSpace(r.Kind),
			Mod:  plusHead(r.Mod),
			Fn:   strings.TrimSpace(r.Fn),
		})
	}
	return out
}

func plusHead(mod string) string {
	mod = strings.TrimSpace(mod)
	if mod == "" {
		return mod
	}
	cut := -1
	for i := 0; i < len(mod); i++ {
		if mod[i] == '+' {
			cut = i
			break
		}
	}
	if cut < 0 {
		return mod
	}
	head := strings.TrimSpace(mod[:cut])
	if head == "" {
		return mod
	}
	return head
}
