package readcue

import (
	"berth.local/twinefuse/netsrc"
	"berth.local/twinefuse/walkbind"
)

func Attach(recs []Rec, n *netsrc.Net) []walkbind.Row {
	rows := make([]walkbind.Row, 0, len(recs))
	for _, rec := range recs {
		rows = append(rows, walkbind.Row{
			Id:    rec.Id,
			Hitch: netsrc.OpMark(n, rec.Tok),
			Tok:   rec.Tok,
		})
	}
	return rows
}
