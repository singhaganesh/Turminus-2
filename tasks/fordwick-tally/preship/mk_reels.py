#!/usr/bin/env python3
"""Deterministic held-out reels. Fixed seed. 160x120 @ 12fps. Not copied to /app."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

W, H, FPS = 160, 120, 12
SEED = 20260918
LINE = 70


def _bg() -> np.ndarray:
    rng = np.random.RandomState(SEED)
    frame = np.full((H, W, 3), 46, dtype=np.uint8)
    frame[:, :, 1] = 48
    frame[:, :, 2] = 50
    noise = rng.randint(0, 5, (H, W, 3), dtype=np.uint8)
    return cv2.add(frame, noise)


BG = _bg()


def _blank() -> np.ndarray:
    return BG.copy()


def _body(frame, x, y, rx=8, ry=10, color=(214, 206, 198)) -> None:
    cv2.ellipse(frame, (int(round(x)), int(round(y))), (rx, ry), 0, 0, 360, color, -1)


def _shadow(frame, x, y) -> None:
    cv2.ellipse(frame, (int(round(x)), int(round(y))), (18, 5), 8, 0, 360, (62, 64, 70), -1)


def _write(path: Path, frames: list[np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    if not vw.isOpened():
        raise RuntimeError(f"writer failed {path}")
    for fr in frames:
        vw.write(fr)
    vw.release()


def lerp(a: float, b: float, t: float) -> float:
    t = min(1.0, max(0.0, t))
    return a + (b - a) * t


def clasp_frames() -> list[np.ndarray]:
    frames = []
    for i in range(8):
        frames.append(_blank())
    for i in range(56):
        fr = _blank()
        if i < 12:
            t = i / 11.0
            y = lerp(16, 48, t)
            xa, xb = 46.0, 92.0
        elif i < 36:
            t = (i - 12) / 23.0
            y = lerp(48, 90, t)
            xa = 70.0
            xb = 70.0
        else:
            t = (i - 36) / 19.0
            y = lerp(90, 110, t)
            xa = lerp(70, 36, t)
            xb = lerp(70, 110, t)
        _body(fr, xa, y)
        _body(fr, xb, y)
        frames.append(fr)
    return frames


def midveil_frames() -> list[np.ndarray]:
    frames = []
    for i in range(8):
        frames.append(_blank())
    for i in range(60):
        fr = _blank()
        if i < 14:
            t = i / 13.0
            y = lerp(14, 46, t)
            xl, xm, xr = 34.0, 80.0, 126.0
        elif i < 40:
            t = (i - 14) / 25.0
            y = lerp(46, 92, t)
            xl, xm, xr = 80.0, 80.0, 80.0
        else:
            t = (i - 40) / 19.0
            y = lerp(92, 110, t)
            xl = lerp(80, 30, t)
            xm = 80.0
            xr = lerp(80, 128, t)
        _body(fr, xm, y)
        _body(fr, xl, y)
        _body(fr, xr, y)
        frames.append(fr)
    return frames


def swapwell_frames() -> list[np.ndarray]:
    frames = []
    for i in range(8):
        frames.append(_blank())
    for i in range(56):
        fr = _blank()
        if i < 12:
            t = i / 11.0
            y = lerp(16, 50, t)
            xa, xb = 40.0, 110.0
        elif i < 36:
            t = (i - 12) / 23.0
            y = lerp(50, 88, t)
            xa = 75.0
            xb = 75.0
        else:
            t = (i - 36) / 19.0
            y = lerp(88, 110, t)
            xa = lerp(75, 118, t)
            xb = lerp(75, 32, t)
        _body(fr, xa, y)
        _body(fr, xb, y)
        frames.append(fr)
    return frames


def cast_frames() -> list[np.ndarray]:
    frames = []
    for i in range(8):
        frames.append(_blank())
    for i in range(50):
        fr = _blank()
        if i < 28:
            yb = lerp(16, 108, i / 27.0)
            _body(fr, 42, yb)
        else:
            ys = lerp(16, 108, (i - 28) / 21.0)
            _shadow(fr, 118, ys)
        frames.append(fr)
    return frames


def braid_frames() -> list[np.ndarray]:
    frames = []
    for i in range(8):
        frames.append(_blank())
    for i in range(70):
        fr = _blank()
        # pair merge (A,B)
        if i < 14:
            t = i / 13.0
            yp = lerp(16, 48, t)
            xa, xb = 48.0, 90.0
        elif i < 38:
            t = (i - 14) / 23.0
            yp = lerp(48, 90, t)
            xa = 68.0
            xb = 68.0
        else:
            t = (i - 38) / 31.0
            yp = lerp(90, 112, t)
            xa = lerp(68, 36, t)
            xb = lerp(68, 104, t)
        _body(fr, xa, yp)
        _body(fr, xb, yp)
        # retreat-then-finish (C)
        if i < 22:
            yc = lerp(18, 84, i / 21.0)
        elif i < 36:
            yc = lerp(84, 54, (i - 22) / 13.0)
        else:
            yc = lerp(54, 108, (i - 36) / 33.0)
        _body(fr, 132, yc, rx=7, ry=9)
        # opposite-dir (D)
        yd = lerp(112, 14, i / 69.0)
        _body(fr, 16, yd, rx=7, ry=9)
        # cast shadow
        ys = lerp(22, 100, i / 69.0)
        _shadow(fr, 152, ys)
        frames.append(fr)
    return frames


def main() -> None:
    out = Path("/reels")
    mapping = {
        "clasp.mp4": clasp_frames,
        "midveil.mp4": midveil_frames,
        "swapwell.mp4": swapwell_frames,
        "cast.mp4": cast_frames,
        "braid.mp4": braid_frames,
    }
    for name, fn in mapping.items():
        _write(out / name, fn())
        print("wrote", name, "frames", len(fn()))


if __name__ == "__main__":
    main()
