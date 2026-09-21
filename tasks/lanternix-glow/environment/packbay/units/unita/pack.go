package unita

import "loft.local/lanternix/packbay/store"

func Load() {
	store.Offer("LAN_WARM_01", store.Spec{Slots: []string{"lux", "hold_s"}})
}
