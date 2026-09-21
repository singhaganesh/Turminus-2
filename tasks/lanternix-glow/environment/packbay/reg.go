package packbay

import (
	unita "loft.local/lanternix/packbay/units/unita"
	unitb "loft.local/lanternix/packbay/units/unitb"
)

func Fill() {
	unita.Load()
	unitb.Load()
}
