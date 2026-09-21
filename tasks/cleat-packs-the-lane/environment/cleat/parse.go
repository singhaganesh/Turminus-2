package main

import (
	"strings"
	"unicode"
)

func safeName(text string) bool {
	if text == "" {
		return false
	}
	for _, r := range text {
		if unicode.IsLetter(r) || unicode.IsDigit(r) || r == '.' || r == '_' || r == '-' {
			continue
		}
		return false
	}
	return true
}

func parseRoll(sheet string) ([]Car, int) {
	var cars []Car
	for _, raw := range strings.Split(sheet, "\n") {
		line := strings.TrimSpace(raw)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		words := strings.Fields(line)
		if len(words) < 10 {
			continue
		}
		if words[0] != "PLATE" || words[2] != "LEN" || words[4] != "HT" || words[6] != "HAZ" || words[8] != "BOARD" {
			continue
		}
		if !safeName(words[1]) {
			continue
		}
		length := atoiLoose(words[3])
		ht := atoiLoose(words[5])
		haz := atoiLoose(words[7])
		board := atoiLoose(words[9])
		if ht < 0 || board < 0 {
			continue
		}
		cars = append(cars, Car{Plate: words[1], Len: length, Ht: ht, Haz: haz, Board: board})
	}
	return cars, 0
}

func atoiLoose(text string) int {
	if text == "" {
		return 0
	}
	n := 0
	for _, r := range text {
		if r < '0' || r > '9' {
			return 0
		}
		n = n*10 + int(r-'0')
	}
	return n
}
