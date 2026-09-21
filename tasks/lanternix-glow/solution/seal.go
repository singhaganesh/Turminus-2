package oxbind

import "loft.local/lanternix/packbay/store"

var chart map[string]store.Spec

func Clip(bag map[string]store.Spec) map[string]store.Spec {
	out := make(map[string]store.Spec, len(bag))
	for k, v := range bag {
		cp := v
		cp.Slots = append([]string(nil), v.Slots...)
		out[k] = cp
	}
	return out
}

func Boot() {
	chart = Clip(store.Bag())
}

func Read(tag string) (store.Spec, bool) {
	live := store.Bag()
	if s, ok := live[tag]; ok {
		return s, true
	}
	if chart != nil {
		if s, ok := chart[tag]; ok {
			return s, true
		}
	}
	return store.Spec{}, false
}
