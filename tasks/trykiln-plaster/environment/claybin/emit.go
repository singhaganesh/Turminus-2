package claybin

import "kilnbench/hopsrc/vat"

const src = "/app/vats/mold.vat"
const dst = "/app/vats/worker.vat"

func EmitWorker() error {
	return vat.CopyFile(src, dst)
}
