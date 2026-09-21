package scorepit

import "kilnbench/hopsrc/vat"

func PadSlot(path string) error {
	st, err := vat.Parse(path)
	if err != nil {
		return err
	}
	st.AddCol("attempt_slot")
	return st.Write(path)
}
