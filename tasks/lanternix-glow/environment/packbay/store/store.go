package store

type Spec struct {
	Slots []string
}

var bag = map[string]Spec{}

func Offer(id string, spec Spec) {
	bag[id] = spec
}

func Bag() map[string]Spec {
	out := make(map[string]Spec, len(bag))
	for k, v := range bag {
		out[k] = v
	}
	return out
}

func Reset() {
	bag = map[string]Spec{}
}
