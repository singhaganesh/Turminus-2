package tab

// ResumeOffset returns the log_bytes coordinate carried by the coordination
// record: the size of append.log at the moment the record was installed.
func ResumeOffset(keep Keep) int64 {
	return keep.LogBytes
}
