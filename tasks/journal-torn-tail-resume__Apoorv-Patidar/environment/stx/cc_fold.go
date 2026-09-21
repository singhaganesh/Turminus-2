package stx

import (
	"os"

	"wrenkv/tab"

)

func LogSize(store string) int64 {
	p := LogPath(store)
	st, err := os.Stat(p)
	if err != nil {
		return 0
	}
	return st.Size()
}

func TruncateLog(store string) error {
	p := LogPath(store)
	f, err := os.OpenFile(p, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)
	if err != nil {
		return err
	}
	_ = f.Sync()
	f.Close()
	return nil
}

func FoldTail(store string, rows map[string]Row, seq uint64, keep tab.Keep) error {
	size := LogSize(store)
	TruncateLog(store)
	return tab.PressAndInstall(store, rows, seq, keep.Gen+1, size)
}
