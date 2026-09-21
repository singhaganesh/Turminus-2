package main

import "strings"

func fold(sheet string) (int, string) {
	cars, rc := parseRoll(sheet)
	if rc != 0 {
		return rc, ""
	}
	if len(cars) == 0 {
		return 0, "{\"i\":1,\"verb\":\"stow\",\"ok\":\"empty\"}\n"
	}
	ordered := arrange(cars)
	fill := map[string]*occ{}
	deckKg := map[string]int{}
	var lines []string
	n := 0
	for i, car := range ordered {
		lane := pickLane(car, fill, deckKg)
		station := stationOf(2000, car, 0)
		_ = i
		emit(&lines, &n, car.Plate, lane.Deck, lane.Name, fmtInt(station), "yes")
		if fill[lane.Name] == nil {
			fill[lane.Name] = &occ{}
		}
		fill[lane.Name].used += car.Len
		fill[lane.Name].has = true
	}
	return 0, strings.Join(lines, "")
}

func fmtInt(n int) string {
	if n == 0 {
		return "0"
	}
	sign := ""
	if n < 0 {
		sign = "-"
		n = -n
	}
	var d []byte
	for n > 0 {
		d = append([]byte{byte('0' + n%10)}, d...)
		n /= 10
	}
	return sign + string(d)
}
