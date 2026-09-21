package main

import (
	"os"
)

const KillExit = 67

var crashTarget = -1
var fenceCount = 0

func Arm(target int) {
	crashTarget = target
	fenceCount = 0
	if crashTarget == 0 {
		os.Exit(KillExit)
	}
}

func Fence(f *os.File) {
	if f != nil {
		_ = f.Sync()
	}
	fenceCount++
	if crashTarget >= 0 && fenceCount >= crashTarget {
		os.Exit(KillExit)
	}
}
