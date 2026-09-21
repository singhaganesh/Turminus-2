#!/bin/bash
set -euo pipefail
cd /app
patch_file=$(mktemp)
trap 'rm -f "$patch_file"' EXIT
cat > "$patch_file" << 'PATCH_EOF'
--- a/environment/wk/main.go
+++ b/environment/wk/main.go
@@ -3,0 +4 @@
+	"encoding/binary"
@@ -5,0 +7 @@
+	"io"
@@ -62,0 +65,49 @@
+func intactEnd(log *os.File) int64 {
+	log.Seek(0, 0)
+	var end int64 = 0
+	var payload [stx.MaxPayload]byte
+	for {
+		var head [stx.HeadSize]byte
+		n, err := io.ReadFull(log, head[:])
+		if err != nil || n < stx.HeadSize {
+			break
+		}
+		if string(head[0:4]) != string(stx.Magic) {
+			break
+		}
+		plen := binary.BigEndian.Uint32(head[12:16])
+		crc := binary.BigEndian.Uint32(head[16:20])
+		if plen > stx.MaxPayload {
+			break
+		}
+		pn, perr := io.ReadFull(log, payload[:plen])
+		if perr != nil || pn < int(plen) {
+			break
+		}
+		if crc32Checksum(payload[:plen]) != crc {
+			break
+		}
+		end += int64(stx.HeadSize + plen)
+	}
+	return end
+}
+
+func crc32Checksum(data []byte) uint32 {
+	return uint32(0xFFFFFFFF) ^ crc32Update(0xFFFFFFFF, data)
+}
+
+func crc32Update(crc uint32, data []byte) uint32 {
+	for _, b := range data {
+		crc ^= uint32(b)
+		for i := 0; i < 8; i++ {
+			if (crc & 1) != 0 {
+				crc = (crc >> 1) ^ 0xEDB88320
+			} else {
+				crc >>= 1
+			}
+		}
+	}
+	return crc
+}
+
+
@@ -85 +136 @@
-	logFile, err := os.OpenFile(lp, os.O_CREATE|os.O_RDWR|os.O_APPEND, 0644)
+	logFile, err := os.OpenFile(lp, os.O_CREATE|os.O_RDWR, 0644)
@@ -90,0 +142,4 @@
+
+	validOffset := intactEnd(logFile)
+	logFile.Truncate(validOffset)
+	logFile.Seek(validOffset, 0)
--- a/environment/stx/rr_scan.go
+++ b/environment/stx/rr_scan.go
@@ -56 +56 @@
-		return 0, nil, ErrTornTail
+		return 0, nil, nil
@@ -59 +59 @@
-		return 0, nil, ErrTornTail
+		return 0, nil, nil
@@ -65 +65 @@
-		return 0, nil, ErrTornTail
+		return 0, nil, nil
@@ -70 +70 @@
-		return 0, nil, ErrTornTail
+		return 0, nil, nil
@@ -73 +73 @@
-		return 0, nil, ErrTornTail
+		return 0, nil, nil
@@ -77 +77 @@
-		return 0, nil, ErrTornTail
+		return 0, nil, nil
--- a/environment/stx/cc_fold.go
+++ b/environment/stx/cc_fold.go
@@ -32,2 +32,4 @@
-	TruncateLog(store)
-	return tab.PressAndInstall(store, rows, seq, keep.Gen+1, size)
+	if err := tab.PressAndInstall(store, rows, seq, keep.Gen+1, size); err != nil {
+		return err
+	}
+	return TruncateLog(store)
--- a/environment/tab/tt_press.go
+++ b/environment/tab/tt_press.go
@@ -43,2 +42,0 @@
-	os.Rename(tmp, final)
-	WriteKeep(store, keep)
@@ -47 +45,2 @@
-	return nil
+	os.Rename(tmp, final)
+	return WriteKeep(store, keep)
--- a/environment/tab/mm_keep.go
+++ b/environment/tab/mm_keep.go
@@ -49 +49 @@
-	return nil
+	return os.Rename(tmp, PathFor(store))
PATCH_EOF
if patch -p1 -R -s --dry-run < "$patch_file" > /dev/null 2>&1; then
    echo "wrenkv repair patch already applied"
else
    patch -p1 -s --no-backup-if-mismatch < "$patch_file"
fi
cd /app/environment && go build -o /app/bin/wrenkv ./wk
rm -rf /app/stores/oracle_demo
/app/bin/wrenkv load /app/stores/oracle_demo --ops /app/workloads/mixed.ops
/app/bin/wrenkv recover /app/stores/oracle_demo
/app/bin/wrenkv compact /app/stores/oracle_demo
/app/bin/wrenkv load /app/stores/oracle_demo --ops /app/workloads/tally.ops --crash-tail 4 || true
/app/bin/wrenkv recover /app/stores/oracle_demo
/app/bin/wrenkv load /app/stores/oracle_demo --ops /app/workloads/demo.ops --crash-after 5 || true
/app/bin/wrenkv recover /app/stores/oracle_demo
/app/bin/wrenkv dump /app/stores/oracle_demo
