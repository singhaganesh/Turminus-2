package wicksrc

import (
	"strings"

	"loft.local/wickpane/celltyp"
)

func Nest(rows []celltyp.Row) []celltyp.Row {
	out := make([]celltyp.Row, 0, len(rows))
	for _, r := range rows {
		if isGap(r) {
			continue
		}
		out = append(out, r)
	}
	return out
}

func isGap(r celltyp.Row) bool {
	k := strings.TrimSpace(r.Kind)
	if k == "" {
		return true
	}
	if k == "i" {
		return true
	}
	if k == "I" {
		return true
	}
	return false
}
