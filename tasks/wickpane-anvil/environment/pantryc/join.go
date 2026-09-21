package pantryc

import (
	"strings"

	"loft.local/wickpane/celltyp"
)

func Join(rows []celltyp.Row) string {
	parts := make([]string, 0, len(rows))
	for _, r := range rows {
		parts = append(parts, r.Mod+"!"+r.Fn)
	}
	return strings.Join(parts, "|")
}
