import sys
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

import numpy as np
from collections import Counter
from common import R2, R3, raster, ptr, kiddy_groups
from palprobe import pal_at
KP = pal_at(R3, 0x3d34cf); DP = pal_at(R2, 0x3d6574)
def _src(which):
    if which == 'k':
        return raster(R3, kiddy_groups()['LookAroundIdle'][0])
    from anim2 import frames_of, gfx_ok
    g = [x for x in frames_of(0x01 + 0xA3)[0] if gfx_ok(x)][0]
    return raster(R2, ptr(R2, 0x3C8000 + g))
def region(path, x0, y0, w, h, pal, drop_blue):
    a = _src(path); ys, xs = np.nonzero(a); a = a[ys.min():, xs.min():]
    sub = a[y0:y0 + h, x0:x0 + w].copy()
    if drop_blue:
        for i in range(1, 16):
            r, g, b = pal[i]
            if b > r + 20: sub[sub == i] = 0
    return sub
def shrink(sub, pal, n=16):
    h, w = sub.shape; out = np.zeros((n, n), int)
    lum = {i: sum(pal[i]) for i in range(1, 16)}
    for ty in range(n):
        for tx in range(n):
            ys = range(int(ty * h / n), max(int(ty * h / n) + 1, int((ty + 1) * h / n)))
            xs = range(int(tx * w / n), max(int(tx * w / n) + 1, int((tx + 1) * w / n)))
            c = Counter(int(sub[y, x]) for y in ys for x in xs)
            if c.get(0, 0) * 2 > sum(c.values()): continue
            c.pop(0, None)
            best = max(c.items(), key=lambda kv: (kv[1], -lum[kv[0]]))[0]
            out[ty, tx] = best
    return out
def to_rgb(idx, pal):
    rgb = np.zeros(idx.shape + (3,), int)
    for i in range(1, 16): rgb[idx == i] = pal[i]
    return rgb, idx > 0
def kiddy(x0=22, y0=0, w=20, h=20):
    return to_rgb(shrink(region('k', x0, y0, w, h, KP, True), KP), KP)
def dixie(x0=8, y0=0, w=21, h=21):
    return to_rgb(shrink(region('d', x0, y0, w, h, DP, False), DP), DP)

def fit(idx, n=16, ox=0, oy=0):
    out = np.zeros((16, 16), int); h, w = idx.shape
    out[oy:oy + h, ox:ox + w] = idx[:16 - oy, :16 - ox]
    return out
def kiddy2(x0, y0, w, h, n, ox, oy):
    s = shrink(region('k', x0, y0, w, h, KP, True), KP, n)
    return to_rgb(fit(s, 16, ox, oy), KP)
def dixie2(x0, y0, w, h, n, ox, oy):
    s = shrink(region('d', x0, y0, w, h, DP, False), DP, n)
    return to_rgb(fit(s, 16, ox, oy), DP)
