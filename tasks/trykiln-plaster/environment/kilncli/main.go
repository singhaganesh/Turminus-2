package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: kilncli impress|spill|assay")
		os.Exit(2)
	}
	var code int
	switch os.Args[1] {
	case "impress":
		code = cmdImpress(os.Args[2:])
	case "spill":
		code = cmdSpill()
	case "assay":
		code = cmdAssay()
	default:
		fmt.Fprintln(os.Stderr, "usage: kilncli impress|spill|assay")
		code = 2
	}
	os.Exit(code)
}
