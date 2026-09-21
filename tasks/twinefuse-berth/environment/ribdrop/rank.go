package ribdrop

// Rank builds a size table after join. Equal sizes share one bin.
func Rank(sz map[string]int) map[int]int {
	out := map[int]int{}
	for _, n := range sz {
		out[n]++
	}
	return out
}
