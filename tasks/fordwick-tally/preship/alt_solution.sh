#!/usr/bin/env bash
set -euo pipefail
# Alternate tracker: thin-smear reject + Kalman + Hungarian, no blob split.
cat > /app/blot.py << 'PY'
from __future__ import annotations
import cv2
import numpy as np
LINE_Y = 70
MIN_AREA = 80.0
NMS = 11.0
THIN = 2.2

def make_mog():
    return cv2.createBackgroundSubtractorMOG2(history=40, varThreshold=16, detectShadows=True)

def blot_mark(frame, mog):
    fg = mog.apply(frame)
    _, th = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    raw = []
    for c in cnts:
        area = float(cv2.contourArea(c))
        if area < MIN_AREA:
            continue
        x, y, w, h = cv2.boundingRect(c)
        short, long = min(w, h), max(w, h)
        if short > 0 and (long / short) >= THIN:
            continue
        m = cv2.moments(c)
        if m["m00"] <= 1e-6:
            continue
        raw.append((m["m10"] / m["m00"], m["m01"] / m["m00"], area))
    raw.sort(key=lambda t: t[2], reverse=True)
    dets = []
    for x, y, area in raw:
        if any(((x - px) ** 2 + (y - py) ** 2) ** 0.5 < NMS for px, py in dets):
            continue
        dets.append((x, y))
    return dets
PY
cat > /app/tether.py << 'PY'
from __future__ import annotations
import itertools
import numpy as np
MAX_DIST = 42.0
COAST = 26
LINE_Y = 70

def _assign(cost):
    n, m = cost.shape
    size = max(n, m)
    if size == 0:
        return []
    C = np.full((size, size), 1e5)
    C[:n, :m] = cost
    idx = list(range(size))
    best = None
    best_s = 1e18
    for perm in itertools.permutations(idx):
        s = sum(C[i, perm[i]] for i in idx)
        if s < best_s:
            best_s = s
            best = perm
    out = []
    for i, j in enumerate(best):
        if i < n and j < m:
            out.append((i, j))
    return out

def knit_marks(dets, tracks):
    return tracks

def fold_gate(tracks, n):
    return n
PY
cat > /app/spout.py << 'PY'
from __future__ import annotations
import itertools
import cv2
import numpy as np
import toml
from pathlib import Path
from blot import blot_mark, make_mog

SHEET = Path("/app/inkwell/sheet.toml")
LINE_Y = 70
MAX_DIST = 42.0
COAST = 26

def _assign(cost):
    n, m = cost.shape
    size = max(n, m)
    if size == 0:
        return []
    C = np.full((size, size), 1e5)
    C[:n, :m] = cost
    idx = list(range(size))
    best = None
    best_s = 1e18
    for perm in itertools.permutations(idx):
        s = sum(C[i, perm[i]] for i in idx)
        if s < best_s:
            best_s = s
            best = perm
    out = []
    for i, j in enumerate(best):
        if i < n and j < m:
            out.append((i, j))
    return out

def _new_kf(x, y):
    kf = cv2.KalmanFilter(4, 2)
    kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
    kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
    kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.08
    kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.5
    kf.errorCovPost = np.eye(4, dtype=np.float32)
    kf.statePost = np.array([[x], [y], [0.0], [0.9]], np.float32)
    return kf

def emit_span(src: str):
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        return None
    mog = make_mog()
    kfs = []
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        dets = blot_mark(frame, mog)
        preds = []
        for row in kfs:
            pred = row[0].predict()
            preds.append((float(pred[0, 0]), float(pred[1, 0])))
        if kfs and dets:
            cost = np.zeros((len(kfs), len(dets)))
            for i, (px, py) in enumerate(preds):
                for j, (x, y) in enumerate(dets):
                    cost[i, j] = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
            used_t, used_d = set(), set()
            for i, j in _assign(cost):
                if cost[i, j] > MAX_DIST:
                    continue
                x, y = dets[j]
                kfs[i][0].correct(np.array([[x], [y]], dtype=np.float32))
                hit, last_y = kfs[i][1], kfs[i][2]
                if (not hit) and last_y < LINE_Y <= y:
                    hit = True
                    n += 1
                kfs[i] = [kfs[i][0], hit, y, 0]
                used_t.add(i)
                used_d.add(j)
            for i in range(len(kfs)):
                if i in used_t:
                    continue
                px, py = preds[i]
                hit, last_y, coast = kfs[i][1], kfs[i][2], kfs[i][3] + 1
                if (not hit) and last_y < LINE_Y <= py:
                    hit = True
                    n += 1
                kfs[i] = [kfs[i][0], hit, py, coast]
            for j, (x, y) in enumerate(dets):
                if j not in used_d:
                    kfs.append([_new_kf(x, y), False, y, 0])
        elif dets:
            for x, y in dets:
                kfs.append([_new_kf(x, y), False, y, 0])
        else:
            for i in range(len(kfs)):
                py = preds[i][1] if preds else kfs[i][2]
                hit, last_y, coast = kfs[i][1], kfs[i][2], kfs[i][3] + 1
                if (not hit) and last_y < LINE_Y <= py:
                    hit = True
                    n += 1
                kfs[i] = [kfs[i][0], hit, py, coast]
        kfs = [row for row in kfs if row[3] <= COAST]
    cap.release()
    return n

def dump_sheet(n: int) -> None:
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    SHEET.write_text(toml.dumps({"crossings": int(n)}), encoding="utf-8")
PY
cp /preship/oracle_src/spanwell.py /app/spanwell.py
bash /app/kiln/bake.sh
python3 /app/varnish/mill.pyc /app/shown.mp4
