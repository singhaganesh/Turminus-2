package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"

	"wrenkv/stx"
	"wrenkv/tab"
)

const Usage = `usage: wrenkv load DIR --ops FILE [--crash-after N | --crash-tail N]
       wrenkv recover DIR [--crash-after N]
       wrenkv compact DIR [--crash-after N]
       wrenkv dump DIR`

func readState(store string, startAfter *uint64) (tab.Keep, map[string]stx.Row, uint64, error) {
	keep := tab.ReadKeep(store)
	var boundary uint64 = keep.CoveredSeq
	if startAfter != nil {
		boundary = *startAfter
	}
	rows := make(map[string]stx.Row)
	if keep.BaseFile != "" {
		bp := filepath.Join(store, keep.BaseFile)
		if data, err := os.ReadFile(bp); err == nil && len(data) > 0 {
			var snap struct {
				Rows map[string]stx.Row `json:"rows"`
			}
			if err := json.Unmarshal(data, &snap); err == nil && snap.Rows != nil {
				rows = snap.Rows
			}
		}
	}
	last := keep.CoveredSeq
	lp := stx.LogPath(store)
	if f, err := os.Open(lp); err == nil {
		defer f.Close()
		records, err := stx.ScanRecords(f, boundary)
		if err != nil {
			return keep, rows, last, err
		}
		for _, rec := range records {
			if err := stx.ApplyOp(rows, rec.Seq, rec.Op); err != nil {
				return keep, rows, last, err
			}
			last = rec.Seq
		}
	}
	if last < keep.CoveredSeq {
		last = keep.CoveredSeq
	}
	return keep, rows, last, nil
}

func pickStart(keep tab.Keep) uint64 {
	return keep.CoveredSeq
}

func cmdLoad(store, opsPath string, crashAfter, crashTail *int) int {
	data, err := os.ReadFile(opsPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "wrenkv: %v\n", err)
		return 2
	}
	ops, err := ParseOps(string(data))
	if err != nil {
		fmt.Fprintf(os.Stderr, "wrenkv: %v\n", err)
		return 2
	}
	os.MkdirAll(store, 0755)
	keep, rows, lastSeq, err := readState(store, nil)
	if err != nil {
		fmt.Fprintf(os.Stderr, "wrenkv: %v\n", err)
		return 1
	}
	_ = keep
	if crashAfter != nil {
		Arm(*crashAfter)
	}
	lp := stx.LogPath(store)
	logFile, err := os.OpenFile(lp, os.O_CREATE|os.O_RDWR|os.O_APPEND, 0644)
	if err != nil {
		fmt.Fprintf(os.Stderr, "wrenkv: %v\n", err)
		return 1
	}
	defer logFile.Close()

	for i, op := range ops {
		opMap := map[string]interface{}{
			"op":  op.Kind,
			"key": op.Key,
		}
		if op.Kind == "put" {
			opMap["value"] = op.Value
		} else if op.Kind == "incr" {
			curVal := int64(0)
			if existing, ok := rows[op.Key]; ok {
				c, err := strconv.ParseInt(existing.Value, 10, 64)
				if err != nil {
					fmt.Fprintf(os.Stderr, "wrenkv: key %q does not hold an integer\n", op.Key)
					return 2
				}
				curVal = c
			}
			opMap["delta"] = op.Delta
			opMap["value"] = strconv.FormatInt(curVal+op.Delta, 10)
		}
		seq := lastSeq + 1
		lastSeq = seq
		rec, err := stx.Frame(seq, opMap)
		if err != nil {
			return 1
		}
		if crashTail != nil && i == *crashTail {
			half := len(rec) / 2
			logFile.Write(rec[:half])
			logFile.Sync()
			os.Exit(KillExit)
		}
		if _, err := logFile.Write(rec); err != nil {
			return 1
		}
		Fence(logFile)
		stx.ApplyOp(rows, seq, opMap)
	}
	return 0
}

func cmdRebuild(store string, crashAfter *int) int {
	st, err := os.Stat(store)
	if err != nil || !st.IsDir() {
		fmt.Fprintf(os.Stderr, "wrenkv: no such store directory\n")
		return 2
	}
	if crashAfter != nil {
		Arm(*crashAfter)
	}
	keep := tab.ReadKeep(store)
	bound := pickStart(keep)
	_, rows, seq, err := readState(store, &bound)
	if err != nil {
		fmt.Fprintf(os.Stderr, "wrenkv: %v\n", err)
		return 1
	}
	if err := tab.PressAndInstall(store, rows, seq, keep.Gen+1, stx.LogSize(store)); err != nil {
		return 1
	}
	return 0
}

func cmdCompact(store string, crashAfter *int) int {
	st, err := os.Stat(store)
	if err != nil || !st.IsDir() {
		fmt.Fprintf(os.Stderr, "wrenkv: no such store directory\n")
		return 2
	}
	if crashAfter != nil {
		Arm(*crashAfter)
	}
	keep, rows, seq, err := readState(store, nil)
	if err != nil {
		fmt.Fprintf(os.Stderr, "wrenkv: %v\n", err)
		return 1
	}
	if err := stx.FoldTail(store, rows, seq, keep); err != nil {
		return 1
	}
	return 0
}

func cmdDump(store string) int {
	st, err := os.Stat(store)
	if err != nil || !st.IsDir() {
		fmt.Fprintf(os.Stderr, "wrenkv: no such store directory\n")
		return 2
	}
	keep, rows, _, err := readState(store, nil)
	if err != nil {
		fmt.Fprintf(os.Stderr, "wrenkv: %v\n", err)
		return 1
	}
	type Entry struct {
		Key   string `json:"key"`
		Rev   uint64 `json:"rev"`
		Value string `json:"value"`
	}
	var entries []Entry
	for k, r := range rows {
		entries = append(entries, Entry{Key: k, Rev: r.Rev, Value: r.Value})
	}
	sort.Slice(entries, func(i, j int) bool {
		return entries[i].Key < entries[j].Key
	})
	if entries == nil {
		entries = []Entry{}
	}
	out := map[string]interface{}{
		"covered_seq": keep.CoveredSeq,
		"entries":     entries,
	}
	data, _ := json.Marshal(out)
	fmt.Println(string(data))
	return 0
}

func main() {
	if len(os.Args) < 2 || os.Args[1] == "-h" || os.Args[1] == "--help" {
		fmt.Fprintln(os.Stderr, Usage)
		if len(os.Args) < 2 {
			os.Exit(2)
		}
		os.Exit(0)
	}
	cmd := os.Args[1]
	if cmd != "load" && cmd != "recover" && cmd != "compact" && cmd != "dump" {
		fmt.Fprintln(os.Stderr, Usage)
		os.Exit(2)
	}

	var store string
	var opsPath string
	var crashAfter *int
	var crashTail *int

	args := os.Args[2:]
	for i := 0; i < len(args); i++ {
		a := args[i]
		if a == "--ops" {
			i++
			if i >= len(args) {
				fmt.Fprintln(os.Stderr, "wrenkv: --ops needs a file")
				os.Exit(2)
			}
			opsPath = args[i]
		} else if a == "--crash-after" {
			i++
			if i >= len(args) {
				fmt.Fprintln(os.Stderr, "wrenkv: --crash-after needs N")
				os.Exit(2)
			}
			n, err := strconv.Atoi(args[i])
			if err != nil || n < 0 {
				fmt.Fprintln(os.Stderr, "wrenkv: --crash-after needs N >= 0")
				os.Exit(2)
			}
			crashAfter = &n
		} else if a == "--crash-tail" {
			i++
			if i >= len(args) {
				fmt.Fprintln(os.Stderr, "wrenkv: --crash-tail needs N")
				os.Exit(2)
			}
			n, err := strconv.Atoi(args[i])
			if err != nil || n < 0 {
				fmt.Fprintln(os.Stderr, "wrenkv: --crash-tail needs N >= 0")
				os.Exit(2)
			}
			crashTail = &n
		} else {
			if store != "" {
				fmt.Fprintln(os.Stderr, "wrenkv: expected exactly one store directory")
				os.Exit(2)
			}
			store = a
		}
	}

	if store == "" {
		fmt.Fprintln(os.Stderr, "wrenkv: expected exactly one store directory")
		os.Exit(2)
	}
	if cmd == "load" && opsPath == "" {
		fmt.Fprintln(os.Stderr, "wrenkv: load needs --ops FILE")
		os.Exit(2)
	}
	if cmd != "load" && opsPath != "" {
		fmt.Fprintln(os.Stderr, "wrenkv: --ops only applies to load")
		os.Exit(2)
	}
	if cmd != "load" && crashTail != nil {
		fmt.Fprintln(os.Stderr, "wrenkv: --crash-tail only applies to load")
		os.Exit(2)
	}

	switch cmd {
	case "load":
		os.Exit(cmdLoad(store, opsPath, crashAfter, crashTail))
	case "recover":
		os.Exit(cmdRebuild(store, crashAfter))
	case "compact":
		os.Exit(cmdCompact(store, crashAfter))
	case "dump":
		os.Exit(cmdDump(store))
	}
}
