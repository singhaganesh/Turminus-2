package main

import (
	"os"

	"loft.local/lanternix/oxbind"
	"loft.local/lanternix/packbay"
)

func main() {
	os.Exit(run(os.Args[1:]))
}

func run(args []string) int {
	if len(args) == 0 {
		return 2
	}
	switch args[0] {
	case "cast":
		packbay.Pull("LAN_WARM_01")
		oxbind.Boot()
		return Spin()
	case "readout":
		if len(args) < 3 || args[1] != "--lamp" {
			return 2
		}
		return Play(args[2])
	default:
		return 2
	}
}
