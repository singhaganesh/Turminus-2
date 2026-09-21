package main

type Lane struct {
	Deck string
	Name string
	Lid  int
	Span int
}

func allLanes() []Lane {
	return []Lane{
		{Deck: "A", Name: "A1", Lid: 180, Span: 2000},
		{Deck: "A", Name: "A2", Lid: 180, Span: 2000},
		{Deck: "B", Name: "B1", Lid: 420, Span: 2000},
		{Deck: "B", Name: "B2", Lid: 420, Span: 2000},
	}
}
