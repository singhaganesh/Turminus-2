from __future__ import annotations

MAX_DIST = 36.0
COAST = 26
LINE_Y = 70


def knit_marks(dets, tracks):
    used = set()
    for tr in tracks:
        best_i = None
        best_d = MAX_DIST
        px = tr["x"] + tr["vx"]
        py = tr["y"] + tr["vy"]
        for i, (x, y) in enumerate(dets):
            if i in used:
                continue
            d = float(((x - px) ** 2 + (y - py) ** 2) ** 0.5)
            if d < best_d:
                best_d = d
                best_i = i
        if best_i is None:
            tr["coast"] += 1
            tr["x"] += tr["vx"]
            tr["y"] += tr["vy"]
            continue
        x, y = dets[best_i]
        used.add(best_i)
        vx = x - tr["x"]
        vy = y - tr["y"]
        tr["vx"] = 0.5 * tr["vx"] + 0.5 * vx
        tr["vy"] = 0.5 * tr["vy"] + 0.5 * vy
        tr["last_y"] = tr["y"]
        tr["x"] = x
        tr["y"] = y
        tr["coast"] = 0
    for i, (x, y) in enumerate(dets):
        if i not in used:
            tracks.append(
                {
                    "x": x,
                    "y": y,
                    "vx": 0.0,
                    "vy": 0.9,
                    "coast": 0,
                    "hit": False,
                    "last_y": y,
                }
            )
    return [t for t in tracks if t["coast"] <= COAST]


def fold_gate(tracks, n):
    for tr in tracks:
        prev = tr.get("last_y", tr["y"])
        y = tr["y"]
        if (not tr["hit"]) and prev < LINE_Y <= y:
            tr["hit"] = True
            n += 1
        tr["last_y"] = y
    return n
