package main

import (
	"os"
)

func main() {
	if len(os.Args) < 2 {
		os.Exit(2)
	}
	switch os.Args[1] {
	case "sew":
		if len(os.Args) < 4 {
			os.Exit(2)
		}
		os.Exit(runSew(os.Args[2], os.Args[3]))
	default:
		os.Exit(2)
	}
}
