package main

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

type Op struct {
	Kind  string `json:"op"`
	Key   string `json:"key"`
	Value string `json:"value,omitempty"`
	Delta int64  `json:"delta,omitempty"`
}

var keyPattern = regexp.MustCompile(`^[A-Za-z0-9._:-]{1,64}$`)

func ParseOps(content string) ([]Op, error) {
	var ops []Op
	lines := strings.Split(content, "\n")
	for lineNum, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) == 0 {
			continue
		}
		cmd := parts[0]
		switch cmd {
		case "put":
			if len(parts) != 3 {
				return nil, fmt.Errorf("line %d: invalid put syntax", lineNum+1)
			}
			key, val := parts[1], parts[2]
			if !keyPattern.MatchString(key) || len(val) < 1 || len(val) > 256 {
				return nil, fmt.Errorf("line %d: invalid key or value format", lineNum+1)
			}
			ops = append(ops, Op{Kind: "put", Key: key, Value: val})
		case "del":
			if len(parts) != 2 {
				return nil, fmt.Errorf("line %d: invalid del syntax", lineNum+1)
			}
			key := parts[1]
			if !keyPattern.MatchString(key) {
				return nil, fmt.Errorf("line %d: invalid key format", lineNum+1)
			}
			ops = append(ops, Op{Kind: "del", Key: key})
		case "incr":
			if len(parts) != 3 {
				return nil, fmt.Errorf("line %d: invalid incr syntax", lineNum+1)
			}
			key := parts[1]
			delta, err := strconv.ParseInt(parts[2], 10, 64)
			if err != nil || !keyPattern.MatchString(key) {
				return nil, fmt.Errorf("line %d: invalid incr format", lineNum+1)
			}
			ops = append(ops, Op{Kind: "incr", Key: key, Delta: delta})
		default:
			return nil, fmt.Errorf("line %d: unknown operation %q", lineNum+1, cmd)
		}
	}
	return ops, nil
}
