package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) != 6 || os.Args[1] != "stow" || os.Args[2] != "--roll" || os.Args[4] != "--chalk" {
		fmt.Fprintf(os.Stderr, "usage: cleat stow --roll PATH --chalk PATH\n")
		os.Exit(2)
	}
	body, err := os.ReadFile(os.Args[3])
	if err != nil {
		os.Exit(1)
	}
	rc, text := fold(string(body))
	if err := os.WriteFile(os.Args[5], []byte(text), 0644); err != nil {
		os.Exit(1)
	}
	if rc == -2 {
		os.Exit(2)
	}
	if rc != 0 {
		os.Exit(1)
	}
}
