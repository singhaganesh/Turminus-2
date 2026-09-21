package main

import (
	"fmt"
	"os"

	"kilnbench/hopsrc/imprint"
)

func cmdImpress(args []string) int {
	path := ""
	if len(args) > 0 {
		path = args[0]
	}
	if err := imprint.Imprint(path); err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	return 0
}
