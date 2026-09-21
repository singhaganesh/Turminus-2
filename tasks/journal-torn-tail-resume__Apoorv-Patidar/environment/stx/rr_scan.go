package stx

import (
	"encoding/binary"
	"encoding/json"
	"errors"
	"fmt"
	"hash/crc32"
	"io"
	"os"
	"path/filepath"
	"strconv"
)

var Magic = []byte("WRKV")

const (
	HeadSize   = 20
	MaxPayload = 1 << 20
	LogName    = "append.log"
)

type Row struct {
	Value string `json:"v"`
	Rev   uint64 `json:"rev"`
}

var ErrTornTail = errors.New("integrity check failed in append log")

func LogPath(store string) string {
	return filepath.Join(store, LogName)
}

func Frame(seq uint64, payloadObj interface{}) ([]byte, error) {
	payload, err := json.Marshal(payloadObj)
	if err != nil {
		return nil, err
	}
	crc := crc32.ChecksumIEEE(payload)
	buf := make([]byte, HeadSize+len(payload))
	copy(buf[0:4], Magic)
	binary.BigEndian.PutUint64(buf[4:12], seq)
	binary.BigEndian.PutUint32(buf[12:16], uint32(len(payload)))
	binary.BigEndian.PutUint32(buf[16:20], crc)
	copy(buf[20:], payload)
	return buf, nil
}

func NextBlock(f *os.File) (uint64, map[string]interface{}, error) {
	head := make([]byte, HeadSize)
	n, err := io.ReadFull(f, head)
	if err == io.EOF || n == 0 {
		return 0, nil, nil
	}
	if n < HeadSize {
		return 0, nil, ErrTornTail
	}
	if string(head[0:4]) != string(Magic) {
		return 0, nil, ErrTornTail
	}
	seq := binary.BigEndian.Uint64(head[4:12])
	plen := binary.BigEndian.Uint32(head[12:16])
	crc := binary.BigEndian.Uint32(head[16:20])
	if plen > MaxPayload {
		return 0, nil, ErrTornTail
	}
	payload := make([]byte, plen)
	pn, perr := io.ReadFull(f, payload)
	if perr != nil || pn < int(plen) {
		return 0, nil, ErrTornTail
	}
	if crc32.ChecksumIEEE(payload) != crc {
		return 0, nil, ErrTornTail
	}
	var obj map[string]interface{}
	if err := json.Unmarshal(payload, &obj); err != nil {
		return 0, nil, ErrTornTail
	}
	return seq, obj, nil
}

func ScanRecords(f *os.File, startAfter uint64) ([]struct {
	Seq uint64
	Op  map[string]interface{}
}, error) {
	var out []struct {
		Seq uint64
		Op  map[string]interface{}
	}
	for {
		seq, obj, err := NextBlock(f)
		if err != nil {
			return nil, err
		}
		if obj == nil {
			break
		}
		if seq > startAfter {
			out = append(out, struct {
				Seq uint64
				Op  map[string]interface{}
			}{Seq: seq, Op: obj})
		}
	}
	return out, nil
}

func ApplyOp(rows map[string]Row, seq uint64, payload map[string]interface{}) error {
	kind, _ := payload["op"].(string)
	key, _ := payload["key"].(string)
	switch kind {
	case "put":
		val, _ := payload["value"].(string)
		rows[key] = Row{Value: val, Rev: seq}
	case "del":
		delete(rows, key)
	case "incr":
		curStr := "0"
		if existing, ok := rows[key]; ok {
			curStr = existing.Value
		}
		curVal, err := strconv.ParseInt(curStr, 10, 64)
		if err != nil {
			return fmt.Errorf("key %s does not hold an integer", key)
		}
		var delta int64
		if dFloat, ok := payload["delta"].(float64); ok {
			delta = int64(dFloat)
		}
		rows[key] = Row{Value: strconv.FormatInt(curVal+delta, 10), Rev: seq}
	}
	return nil
}
