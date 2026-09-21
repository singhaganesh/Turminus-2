package main

import (
	"os"
	"path/filepath"

	"berth.local/twinefuse/cardpit"
	"berth.local/twinefuse/netsrc"
	"berth.local/twinefuse/readcue"
	"berth.local/twinefuse/ribdrop"
	"berth.local/twinefuse/walkbind"
)

func runSew(dump, out string) int {
	recs, err := readcue.Scan(dump)
	if err != nil {
		return 1
	}
	toks := make([]string, 0, len(recs))
	for _, rec := range recs {
		toks = append(toks, rec.Tok)
	}
	net := netsrc.OpTie(toks)
	_ = ribdrop.Rank(net.Sz)
	if err := cardpit.NPair("/app/aliascue", net); err != nil {
		_ = os.Remove(filepath.Join(out, "berth.ok"))
		return 1
	}
	rows := readcue.Attach(recs, net)
	if err := walkbind.CfgStamp(out, rows); err != nil {
		return 1
	}
	return 0
}
