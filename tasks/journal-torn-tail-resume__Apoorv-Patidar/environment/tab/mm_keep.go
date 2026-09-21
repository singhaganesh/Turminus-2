package tab

import (
	"encoding/json"
	"os"
	"path/filepath"
)

const Name = "keep.json"

type Keep struct {
	Gen        int    `json:"gen"`
	BaseFile   string `json:"base_file"`
	CoveredSeq uint64 `json:"covered_seq"`
	LogBytes   int64  `json:"log_bytes"`
}

func PathFor(store string) string {
	return filepath.Join(store, Name)
}

func ReadKeep(store string) Keep {
	p := PathFor(store)
	data, err := os.ReadFile(p)
	if err != nil {
		return Keep{Gen: 0, BaseFile: "", CoveredSeq: 0, LogBytes: 0}
	}
	var k Keep
	if err := json.Unmarshal(data, &k); err != nil {
		return Keep{Gen: 0, BaseFile: "", CoveredSeq: 0, LogBytes: 0}
	}
	return k
}

func WriteKeep(store string, keep Keep) error {
	tmp := PathFor(store) + ".tmp"
	f, err := os.OpenFile(tmp, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)
	if err != nil {
		return err
	}
	enc := json.NewEncoder(f)
	enc.SetIndent("", "")
	if err := enc.Encode(keep); err != nil {
		f.Close()
		return err
	}
	_ = f.Sync()
	f.Close()
	return nil
}
