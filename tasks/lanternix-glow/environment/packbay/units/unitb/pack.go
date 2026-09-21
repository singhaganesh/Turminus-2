package unitb

import "loft.local/lanternix/packbay/store"

func Load() {
	store.Offer("LAN_BEAM_44", store.Spec{Slots: []string{"az_deg", "el_deg"}})
}
