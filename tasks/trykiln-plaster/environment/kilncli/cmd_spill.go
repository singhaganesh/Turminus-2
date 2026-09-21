package main

import (
	"fmt"
	"os"

	"kilnbench/claybin"
)

func cmdSpill() int {
	if err := claybin.EmitWorker(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	return 0
}
