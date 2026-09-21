package tab

import (
	"encoding/json"
	"os"
	"path/filepath"
)

// ScanPendingBaseSeq inspects leftover uncommitted base snapshot files (*.tbl.tmp)
// in the store directory and returns the highest embedded sequence number.
// This allows recovery routines to resume from staged compaction or bake state.
// Returns 0 if no candidate snapshot is present.
func ScanPendingBaseSeq(store string) uint64 {
	matches, err := filepath.Glob(filepath.Join(store, "base-*.tbl.tmp"))
	if err != nil || len(matches) == 0 {
		return 0
	}
	var highest uint64
	for _, m := range matches {
		data, err := os.ReadFile(m)
		if err != nil {
			continue
		}
		var snap struct {
			Seq uint64 `json:"seq"`
		}
		if err := json.Unmarshal(data, &snap); err == nil {
			if snap.Seq > highest {
				highest = snap.Seq
			}
		}
	}
	return highest
}
