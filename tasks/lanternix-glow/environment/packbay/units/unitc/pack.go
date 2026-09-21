package unitc

import "loft.local/lanternix/packbay/store"

func Load() {
	store.Offer("LAN_FLASH_9C", store.Spec{Slots: []string{"candela", " dwell_s"}})
}
