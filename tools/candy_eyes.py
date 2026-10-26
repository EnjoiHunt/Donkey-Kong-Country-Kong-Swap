"""Give Candy open eyes in every blow-kiss frame (after shrinking, her
half-closed eyelids read as black holes). Eyes are copied from the frames
that have them (3 for standing-ish, 13 for bent-over) by matching the head."""
import numpy as np

def _eye_at(a):
    ys, xs = np.nonzero(a == 15)
    return int(ys[0]), int(xs[0])

def _match(a, T, ty, tx, rad=10):
    h, w = T.shape
    best = None
    ys, xs = np.nonzero(a)
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            y0, x0 = ty + dy, tx + dx
            if y0 < 0 or x0 < 0: continue
            W_ = a[y0:y0 + h, x0:x0 + w]
            if W_.shape != T.shape: continue
            m = (T > 0) & (T != 15)
            score = np.count_nonzero((W_ == T) & m) - 0.5 * np.count_nonzero((W_ == 0) & m)
            if best is None or score > best[0]:
                best = (score, dy, dx)
    return best

def fix(frames, ref_idx=(2, 12)):
    out = list(frames)
    refs = []
    for r in ref_idx:
        y, x = _eye_at(frames[r])
        T = frames[r][y - 6:y + 5, x - 8:x + 6]
        refs.append((r, y, x, T))
    for i, a in enumerate(frames):
        if (a == 15).any():
            continue
        r, y, x, T = refs[0] if i < 7 else refs[1]
        sc, dy, dx = _match(a, T, y - 6 + 0, x - 8 + 0, 12)
        b = a.copy()
        ey, ex = y + dy, x + dx
        for xx, v in ((ex, 15), (ex + 2, 15), (ex + 3, 1)):
            if b[ey, xx]:
                b[ey, xx] = v
        out[i] = b
    return out
