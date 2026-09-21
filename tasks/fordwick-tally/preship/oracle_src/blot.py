from __future__ import annotations

import cv2
import numpy as np

LINE_Y = 70
MIN_AREA = 80.0
NMS = 12.0
SPLIT_AREA = 380.0
SPLIT_WIDE = 28
THIN = 2.2


def make_mog():
    return cv2.createBackgroundSubtractorMOG2(
        history=50, varThreshold=12, detectShadows=True
    )


def _centroid(c):
    m = cv2.moments(c)
    if m["m00"] <= 1e-6:
        return None
    return m["m10"] / m["m00"], m["m01"] / m["m00"]


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
        if area >= SPLIT_AREA and long >= SPLIT_WIDE:
            if w >= h:
                raw.append((x + w * 0.28, y + h * 0.5, area * 0.5))
                raw.append((x + w * 0.72, y + h * 0.5, area * 0.5))
            else:
                raw.append((x + w * 0.5, y + h * 0.28, area * 0.5))
                raw.append((x + w * 0.5, y + h * 0.72, area * 0.5))
            continue
        cen = _centroid(c)
        if cen is None:
            continue
        raw.append((cen[0], cen[1], area))
    raw.sort(key=lambda t: t[2], reverse=True)
    dets = []
    for x, y, area in raw:
        if any(((x - px) ** 2 + (y - py) ** 2) ** 0.5 < NMS for px, py in dets):
            continue
        dets.append((x, y))
    return dets
