"""Cranky's cane arm cut from his DKC1 'WindPhonograph1' frame, so his cane
swing and jump poses don't need the eye-popping 'Startled' frames."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from puppet import rot_part, place, outline_fix
try:
    import config as CFG
    _FR = dict(json.load(open(CFG.data('cc_frames.json'))))
except Exception:
    _FR = dict(json.load(open(os.path.join(HERE, 'cc_frames.json'))))
from common import R1, raster

S = raster(R1, _FR['CrankyKong_WindPhonograph1'])
H, W = S.shape
yy, xx = np.mgrid[0:H, 0:W]
ARMCOL = np.isin(S, [3, 4, 5, 6, 0xB, 0xC, 0xD, 0xE])
ARM = (S > 0) & (xx <= 117) & (xx >= 106) & (yy >= 99) & (yy <= 110) & ARMCOL
ARM |= (S > 0) & (xx <= 107) & (yy >= 97) & (yy <= 107)               # hand and cane top
ARM |= (S > 0) & (xx <= 105) & (yy > 107) & ~((yy >= 120) & np.isin(S, [0xB, 0xC, 0xD, 0xE]) & (xx >= 101))
SHOULDER = (117, 105)
BODY = (S > 0) & ~ARM


ARMSEG = ARM & (xx >= 99) & (yy <= 107)          # forearm + hand
CANE = ARM & ~ARMSEG                                # the cane below the hand
HAND = (103, 103)


def pose(arm, cane_ang, behind=False):
    """Absolute angles (0 = hanging down, 90 = forward, 180 = up, -90 = back).
    In the source frame the arm points back (-90) and the cane hangs down (0)."""
    import math
    out = np.zeros_like(S)
    da, dc = arm - (-90), cane_ang - 0
    a = math.radians(da)
    hx, hy = HAND[0] - SHOULDER[0], HAND[1] - SHOULDER[1]
    nh = (int(round(SHOULDER[0] + hx * math.cos(a) + hy * math.sin(a))),
          int(round(SHOULDER[1] - hx * math.sin(a) + hy * math.cos(a))))
    def draw_arm():
        rot_part(S, CANE, HAND, dc, nh, out)
        rot_part(S, ARMSEG, SHOULDER, da, SHOULDER, out)
    if behind:
        draw_arm(); place(S, BODY, (0, 0), out)
    else:
        place(S, BODY, (0, 0), out); draw_arm()
    return outline_fix(out, 1)


KEYS = [(-150, -170), (180, 175), (145, 135), (115, 105), (95, 85), (75, 65)]
def _clean(o, min_px=4):
    """drop tiny stray islands left over from cutting the arm out"""
    from collections import deque
    seen = np.zeros(o.shape, bool); out = o.copy()
    for y, x in zip(*np.nonzero(o)):
        if seen[y, x]: continue
        comp = []; q = deque([(y, x)]); seen[y, x] = True
        while q:
            cy, cx = q.popleft(); comp.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < o.shape[0] and 0 <= nx < o.shape[1] and o[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; q.append((ny, nx))
        if len(comp) < min_px:
            for cy, cx in comp: out[cy, cx] = 0
    return out


SWING = [_clean(pose(a, c, behind=(a < -100 or a > 160))) for a, c in KEYS]
RAISED = [_clean(pose(-160, 170, True)), _clean(pose(-150, 160, True))]
