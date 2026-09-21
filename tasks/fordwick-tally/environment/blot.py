from __future__ import annotations

import cv2

LINE_Y = 70


def make_mog():
    return cv2.createBackgroundSubtractorMOG2(
        history=30, varThreshold=16, detectShadows=True
    )


def blot_mark(frame, mog) -> bool:
    fg = mog.apply(frame)
    _, th = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
    y = int(LINE_Y)
    band = th[max(0, y - 1) : min(th.shape[0], y + 2)]
    return bool(band.any())
