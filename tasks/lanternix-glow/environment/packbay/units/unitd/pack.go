package unitd

import "loft.local/lanternix/packbay/store"

func Load() {
	store.Offer("LAN_GLOW_2B", store.Spec{Slots: []string{"hue", " period_s"}})
}
