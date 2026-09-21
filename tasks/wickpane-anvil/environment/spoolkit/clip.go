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
	if i := strings.Index(mod, "+0x"); i >= 0 {
		head := strings.TrimSpace(mod[:i])
		if head != "" {
			return head
		}
	}
	if i := strings.Index(mod, "+"); i >= 0 {
		tail := strings.TrimSpace(mod[i+1:])
		if tail != "" {
			return tail
		}
	}
	return mod
}
