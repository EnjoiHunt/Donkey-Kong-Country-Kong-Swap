"""5.2: Cranky without his cane. The cane is a long, 1-2 pixel wide run of greys (colours 7-10)
that doesn't touch his white beard; erase it and patch the hole from the pixels around it."""
import numpy as np

GREY = (7, 8, 9, 10)
BEARD = (13, 14, 15)


def _components(mask):
    H, W = mask.shape
    lab = np.zeros(mask.shape, int); n = 0; comps = []
    for y, x in zip(*np.nonzero(mask)):
        if lab[y, x]: continue
        n += 1; st = [(y, x)]; lab[y, x] = n; pts = []
        while st:
            cy, cx = st.pop(); pts.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = cy + dy, cx + dx
                    if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n; st.append((yy, xx))
        comps.append(pts)
    return comps


def cane_mask(a):
    G = np.isin(a, GREY)
    B = np.isin(a, BEARD)
    Bn = np.zeros_like(B)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            Bn |= np.roll(np.roll(B, dy, 0), dx, 1)
    out = np.zeros_like(G)
    for pts in _components(G):
        ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
        ext = max(max(ys) - min(ys), max(xs) - min(xs)) + 1
        if ext < 8 or len(pts) > 3 * ext: continue
        near = sum(Bn[p] for p in pts) / len(pts)
        if near > 0.25: continue
        for p in pts: out[p] = True
    # and the short grey bits joined to it (the handle in his hand, the tip)
    for _ in range(2):
        near = np.zeros_like(out)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                near |= np.roll(np.roll(out, dy, 0), dx, 1)
        for pts in _components(G & ~out):
            if len(pts) <= 12 and any(near[p] for p in pts) and sum(Bn[p] for p in pts) <= len(pts) // 3:
                for p in pts: out[p] = True
    # a stub of handle sticking out of his hand: small grey bit mostly bordered by empty pixels
    if out.any():
        E = a == 0
        for pts in _components(G & ~out):
            if not 4 <= len(pts) <= 12 or sum(Bn[p] for p in pts): continue
            ys = [p[0] for p in pts]
            if max(ys) - min(ys) < 2: continue
            open_ = sum(1 for (y, x) in pts if (x > 0 and E[y, x - 1]) or (x + 1 < a.shape[1] and E[y, x + 1]))
            if open_ * 2 >= len(pts):
                for p in pts: out[p] = True
    return out


def remove_cane(a):
    m = cane_mask(a)
    if not m.any(): return a
    b = a.copy(); b[m] = 0
    todo = m.copy()
    for _ in range(3):
        nb = b.copy()
        for y, x in zip(*np.nonzero(todo)):
            vals = [b[y + dy, x + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1))
                    if 0 <= y + dy < b.shape[0] and 0 <= x + dx < b.shape[1] and b[y + dy, x + dx] and not todo[y + dy, x + dx]]
            if len(vals) >= 3:
                nb[y, x] = max(set(vals), key=vals.count); todo[y, x] = False
        b = nb
    # drop the little bits the cane leaves floating (its tip), anything not joined to Cranky
    comps = _components(b > 0)
    if comps:
        big = max(len(c) for c in comps)
        for c in comps:
            if len(c) < 12 and len(c) < big:
                for q in c: b[q] = 0
    return b
