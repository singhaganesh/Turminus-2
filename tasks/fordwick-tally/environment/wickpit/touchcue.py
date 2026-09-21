#!/usr/bin/env python3
"""Desk helper: rising occupancy on the scan row."""
from __future__ import annotations

import cv2

LINE_Y = 70


def occupancy_edges(src: str) -> int:
    cap = cv2.VideoCapture(src)
    mog = cv2.createBackgroundSubtractorMOG2(history=30, varThreshold=16, detectShadows=True)
    prev = False
    n = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        fg = mog.apply(frame)
        _, th = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
        y = int(LINE_Y)
        band = th[max(0, y - 1) : min(th.shape[0], y + 2)]
        now = bool(band.any())
        if now and not prev:
            n += 1
        prev = now
    cap.release()
    return n
