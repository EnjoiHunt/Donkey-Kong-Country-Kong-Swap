"""Funky Kong frames: DKC2 art (his Funky's Flights II poses) plus a drawn surfboard."""
import os, sys, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
from common import R2, ptr, raster
from anim2 import frames_of, gfx_ok
from candy_rig import shift, rotate_whole, ground
from puppet import rot_part, place, outline_fix

PAL_OFF = 0x3D7528          # DKC2 Funky palette (alt palette $23)


def _fr(a): return [raster(R2, ptr(R2, 0x3C8000 + x)) for x in dict.fromkeys(x for x in frames_of(a)[0] if gfx_ok(x))]


DYN = _fr(0x1CA)            # balancing pose, arms out, bandana flying (13)
STAND = _fr(0x1CC)          # facing the camera (3)
TALK = _fr(0x1CD)           # (6)
NOD = _fr(0x1CE)            # (5)


def scale(a, s, ox=128, oy=131):
    """nearest-neighbour scale about (ox, oy) (feet)"""
    out = np.zeros_like(a)
    ys, xs = np.nonzero(a)
    H, W = a.shape
    for y in range(int(oy - (oy - ys.min()) * s) - 1, int(oy + (ys.max() - oy) * s) + 2):
        for x in range(int(ox - (ox - xs.min()) * s) - 1, int(ox + (xs.max() - ox) * s) + 2):
            sy, sx = int(round(oy + (y - oy) / s)), int(round(ox + (x - ox) / s))
            if 0 <= sy < H and 0 <= sx < W and 0 <= y < H and 0 <= x < W:
                out[y, x] = a[sy, sx]
    return out


def board(length=46, x0=0, y0=0):
    """side view of a surfboard, nose to the right (+x). Funky palette indices:
    1 black, 10/11/12 magentas, 15 white, 14 grey."""
    h = 5
    out = {}
    for i in range(length):
        t = i / (length - 1)
        thick = max(2, int(round(h * math.sin(math.pi * min(1, t * 1.15)) ** 0.5)))
        lift = int(round(4 * max(0, t - 0.8) / 0.2) ** 1) if t > 0.8 else 0
        top = -thick // 2 - lift
        for j in range(top, top + thick + 1):
            out[(x0 + i, y0 + j)] = 12
        out[(x0 + i, y0 + top - 1)] = 1
        out[(x0 + i, y0 + top + thick + 1)] = 1
        out[(x0 + i, y0 + top + thick)] = 10
        if 0.1 < t < 0.85:
            out[(x0 + i, y0 + top + 1)] = 15 if 0.25 < t < 0.75 else 11
    for j in range(-6, 6):                    # rounded tail / nose caps
        for (x, y), v in list(out.items()):
            pass
    xs = [x for x, y in out]; ys = [y for x, y in out]
    for y in range(min(ys), max(ys) + 1):     # outline the ends
        row = [x for (x, yy) in out if yy == y]
        if row:
            out[(min(row) - 1, y)] = 1; out[(max(row) + 1, y)] = 1
    return out


def on_board(a, dx_board=0, feet=None):
    """put frame a on a board under its feet"""
    a = a.copy()
    rows = [y for y in range(a.shape[0]) if np.count_nonzero(a[y]) >= 4]
    fb = max(rows)
    ys, xs = np.nonzero(a[:fb + 1])
    a[fb + 1:] = 0
    band = xs[ys >= fb - 3]
    cx = int((band.min() + band.max()) / 2)
    B = board()
    bx = min(x for x, y in B); bw = max(x for x, y in B) - bx
    midx = bx + bw // 2
    by = min(y for x, y in B if x == midx)     # top of the deck in the middle
    ox, oy = cx - bw // 2 - bx + dx_board, fb - 1 - by
    out = a.copy()
    for (x, y), v in B.items():
        X, Y = x + ox, y + oy
        if 0 <= X < out.shape[1] and 0 <= Y < out.shape[0] and out[Y, X] == 0:
            out[Y, X] = v
    return out


SC = 0.8                                    # a little smaller so frame + board fit 32 tiles
DYN_S = [scale(a, SC) for a in DYN]
SURF = [ground(on_board(a)) for a in DYN_S]
AIR = SURF                                   # he takes the board along when he jumps
STAND_S = [scale(a, SC) for a in STAND]
TALK_S = [scale(a, SC) for a in TALK]
NOD_S = [scale(a, SC) for a in NOD]


def walk(k, n=8):
    """knuckle walk from the front-facing stance: hands lift in turn, body bobs"""
    a = STAND_S[0]
    H, W = a.shape
    yy, xx = np.mgrid[0:H, 0:W]
    ys, xs = np.nonzero(a)
    cx = (xs.min() + xs.max()) / 2; fb = ys.max()
    lowband = yy >= fb - 14
    left = (a > 0) & lowband & (xx < cx - 5)
    right = (a > 0) & lowband & (xx > cx + 5)
    body = (a > 0) & ~left & ~right
    t = 2 * math.pi * k / n
    ll = int(round(3 * max(0, math.sin(t)))); rl = int(round(3 * max(0, -math.sin(t))))
    bob = int(round(abs(math.sin(t))))
    out = np.zeros_like(a)
    place(a, body, (0, -bob), out)
    place(a, left, (int(round(2 * math.sin(t))), -ll), out)
    place(a, right, (int(round(2 * math.sin(t))), -rl), out)
    return out


WALK = [walk(k) for k in range(8)]
HURT = [rotate_whole(STAND_S[0], a, (128, 110), (128, 110)) for a in (-15, -30, 15)]
FAIL = [rotate_whole(STAND_S[0], a, (128, 115), (128, 118)) for a in (-20, -45, -70, -90)]
SWIM = [rotate_whole(DYN_S[k], -55, (128, 110), (128, 112)) for k in (0, 3, 6, 9)]
DUCK = [ground(scale(STAND_S[0], 1.0)[0:0].reshape(0, 0) if False else STAND_S[0])]
