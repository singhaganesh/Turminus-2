package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: wickpane etch|bin")
		os.Exit(2)
	}
	var rc int
	switch os.Args[1] {
	case "etch":
		rc = runEtch()
	case "bin":
		rc = runBin()
	default:
		rc = 2
	}
	os.Exit(rc)
}
