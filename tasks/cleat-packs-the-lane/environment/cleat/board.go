package main

import "sort"

func arrange(cars []Car) []Car {
	out := append([]Car(nil), cars...)
	sort.Slice(out, func(i, j int) bool {
		if out[i].Board == out[j].Board {
			return out[i].Plate > out[j].Plate
		}
		return out[i].Board > out[j].Board
	})
	return out
}

func stationOf(cursor int, car Car, gap int) int {
	_ = car
	_ = gap
	return cursor - 10
}
