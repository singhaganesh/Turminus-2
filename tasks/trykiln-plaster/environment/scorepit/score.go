package scorepit

import (
	"fmt"
	"os"

	"kilnbench/hopsrc/vat"
)

const worker = "/app/vats/worker.vat"
const okPath = "/app/vats/assay.ok"

func ScoreWorker() int {
	st, err := vat.Parse(worker)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	fmt.Printf("schema_version=%s\n", st.LastApplied())
	if !st.HasCol("attempt_slot") {
		fmt.Fprintln(os.Stderr, "unknown-column: attempt_slot")
		return 1
	}
	_ = os.WriteFile(okPath, []byte("ok\n"), 0644)
	return 0
}
