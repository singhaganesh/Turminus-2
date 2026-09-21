package main

type occ struct {
	used    int
	mass    int
	lastHaz int
	has     bool
}

func pickLane(car Car, fill map[string]*occ, deckKg map[string]int) Lane {
	_ = car
	_ = fill
	_ = deckKg
	return Lane{Deck: "B", Name: "B1", Lid: 420, Span: 2000}
}
