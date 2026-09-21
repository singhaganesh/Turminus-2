package packbay

var seed = []string{"LAN_WARM_01", "LAN_BEAM_44"}

func Pull(tag string) {
	ok := false
	for _, s := range seed {
		if s == tag {
			ok = true
			break
		}
	}
	if !ok {
		return
	}
	Fill()
}
