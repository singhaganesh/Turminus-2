package tab

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"



)

func BaseName(gen int) string {
	return fmt.Sprintf("base-%d.tbl", gen)
}

func PressAndInstall(store string, rows interface{}, seq uint64, gen int, logBytes int64) error {
	tmp := filepath.Join(store, BaseName(gen)+".tmp")
	final := filepath.Join(store, BaseName(gen))
	keep := Keep{
		Gen:        gen,
		BaseFile:   BaseName(gen),
		CoveredSeq: seq,
		LogBytes:   logBytes,
	}
	f, err := os.OpenFile(tmp, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)
	if err != nil {
		return err
	}
	snapshot := struct {
		Gen  int                `json:"gen"`
		Seq  uint64             `json:"seq"`
		Rows interface{} `json:"rows"`
	}{
		Gen:  gen,
		Seq:  seq,
		Rows: rows,
	}
	if err := json.NewEncoder(f).Encode(snapshot); err != nil {
		f.Close()
		return err
	}
	os.Rename(tmp, final)
	WriteKeep(store, keep)
	_ = f.Sync()
	f.Close()
	return nil
}
