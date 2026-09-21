package claybin

import (
	"fmt"
	"strings"

	"kilnbench/hopsrc/vat"
)

const src = "/app/vats/plaster.vat"
const dst = "/app/vats/worker.vat"
const migDir = "/app/inkstack/migrations"

func EmitWorker() error {
	if err := headsAlign(src); err != nil {
		return err
	}
	st, err := vat.Parse(src)
	if err != nil {
		return err
	}
	if !st.HasCol("attempt_slot") {
		return fmt.Errorf("source lags ledger")
	}
	return vat.CopyFile(src, dst)
}

func sourceHead(path string) (string, error) {
	st, err := vat.Parse(path)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(st.LastApplied()), nil
}

func ledgerHead() (string, error) {
	return vat.LedgerHead(migDir)
}

func headsAlign(srcPath string) error {
	got, err := sourceHead(srcPath)
	if err != nil {
		return err
	}
	want, err := ledgerHead()
	if err != nil {
		return err
	}
	if got != want {
		return fmt.Errorf("source lags ledger")
	}
	return nil
}
