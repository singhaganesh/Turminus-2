package pantryc

import (
	"strings"

	"loft.local/wickpane/celltyp"
)

func Drop(rows []celltyp.Row) []celltyp.Row {
	out := make([]celltyp.Row, 0, len(rows))
	for _, r := range rows {
		if skipClock(r.Mod) {
			continue
		}
		out = append(out, r)
	}
	return out
}

func skipClock(mod string) bool {
	m := strings.TrimSpace(mod)
	if i := strings.Index(m, "+"); i >= 0 {
		m = strings.TrimSpace(m[:i])
	}
	return m == "[vdso]" || strings.HasPrefix(m, "[vdso]")
}
