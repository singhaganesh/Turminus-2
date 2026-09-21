package netsrc

type Net struct {
	Par map[string]string
	Sz  map[string]int
}

func NewNet() *Net {
	return &Net{Par: map[string]string{}, Sz: map[string]int{}}
}

func (n *Net) Add(k string) {
	if _, ok := n.Par[k]; ok {
		return
	}
	n.Par[k] = k
	n.Sz[k] = 1
}

func (n *Net) Find(k string) string {
	n.Add(k)
	for n.Par[k] != k {
		n.Par[k] = n.Par[n.Par[k]]
		k = n.Par[k]
	}
	return k
}

func (n *Net) Join(a, b string) {
	ra, rb := n.Find(a), n.Find(b)
	if ra == rb {
		return
	}
	if n.Sz[ra] < n.Sz[rb] {
		ra, rb = rb, ra
	}
	n.Par[rb] = ra
	n.Sz[ra] += n.Sz[rb]
}

func OpTie(toks []string) *Net {
	n := NewNet()
	for _, t := range toks {
		n.Add(t)
	}
	return n
}

func OpMark(n *Net, tok string) string {
	root := n.Find(tok)
	pin := root
	for k := range n.Par {
		rk := n.Find(k)
		if rk != root {
			continue
		}
		if n.Sz[rk] > n.Sz[pin] {
			pin = rk
		}
	}
	return pin
}
