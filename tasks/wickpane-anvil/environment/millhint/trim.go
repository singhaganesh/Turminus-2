package millhint

import "strings"

func Trim(tok string) string {
	i := strings.LastIndex(tok, "+")
	if i < 0 {
		return tok
	}
	head, tail := tok[:i+1], tok[i+1:]
	if len(tail) == 0 {
		return tok
	}
	b := []byte(tail)
	b[len(b)-1] = '0'
	return head + string(b)
}
