package walkbind

import (
	"encoding/json"
	"os"
	"path/filepath"
)

type Row struct {
	Id    string `json:"id"`
	Hitch string `json:"hitch"`
	Tok   string `json:"tok"`
}

func CfgStamp(outDir string, rows []Row) error {
	if err := os.MkdirAll(outDir, 0o755); err != nil {
		return err
	}
	byID := map[string]Row{}
	for _, row := range rows {
		byID[row.Id] = row
	}
	rf, err := os.Create(filepath.Join(outDir, "rows.ndjson"))
	if err != nil {
		return err
	}
	enc := json.NewEncoder(rf)
	enc.SetEscapeHTML(false)
	for _, row := range byID {
		if err := enc.Encode(row); err != nil {
			rf.Close()
			return err
		}
	}
	if err := rf.Close(); err != nil {
		return err
	}
	groups := map[string][]string{}
	for _, row := range byID {
		groups[row.Hitch] = append(groups[row.Hitch], row.Id)
	}
	xf, err := os.Create(filepath.Join(outDir, "hitch.idx"))
	if err != nil {
		return err
	}
	for h, ids := range groups {
		line := h + " " + stringsJoin(ids, ",") + "\n"
		if _, err := xf.WriteString(line); err != nil {
			xf.Close()
			return err
		}
	}
	if err := xf.Close(); err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(outDir, "berth.ok"), []byte("ok\n"), 0o644)
}

func stringsJoin(ids []string, sep string) string {
	if len(ids) == 0 {
		return ""
	}
	out := ids[0]
	for i := 1; i < len(ids); i++ {
		out += sep + ids[i]
	}
	return out
}
