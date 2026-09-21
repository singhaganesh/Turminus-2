package claybin

import "kilnbench/hopsrc/vat"

func BorrowBench() error {
	return vat.CopyFile("/app/vats/bench.vat", "/app/vats/worker.vat")
}
