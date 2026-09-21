package main

import "fmt"

func emit(lines *[]string, i *int, plate, deck, lane, station, ok string) {
	*i++
	row := fmt.Sprintf(`{"i":%d,"verb":"stow"`, *i)
	if plate != "" {
		row += fmt.Sprintf(`,"plate":"%s"`, plate)
	}
	if deck != "" {
		row += fmt.Sprintf(`,"deck":"%s"`, deck)
	}
	if lane != "" {
		row += fmt.Sprintf(`,"lane":"%s"`, lane)
	}
	if station != "" {
		row += fmt.Sprintf(`,"station":"%s"`, station)
	}
	row += fmt.Sprintf(`,"ok":"%s"}`+"\n", ok)
	*lines = append(*lines, row)
}
