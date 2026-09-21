package oxbind

import "loft.local/lanternix/packbay/store"

var chart map[string]store.Spec

func Clip(bag map[string]store.Spec) map[string]store.Spec {
	out := make(map[string]store.Spec, len(bag))
	for k, v := range bag {
		out[k] = v
	}
	return out
}

func Boot() {
	chart = Clip(store.Bag())
}

func Read(tag string) (store.Spec, bool) {
	s, ok := chart[tag]
	return s, ok
}
