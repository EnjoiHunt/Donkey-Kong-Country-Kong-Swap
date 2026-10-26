import sys, json, re
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

import numpy as np
from dkcsprite import parse, raster
R1 = open(CFG.DKC1_ROM, 'rb').read()
R2 = open(CFG.DKC2_ROM, 'rb').read()
R3 = open(CFG.DKC3_ROM, 'rb').read()
def ptr(rom, o):
    a, b, c, d = rom[o:o+4]; return (c << 16 | b << 8 | a) & 0x3fffff
DK1_TABLE = 0x3bcd28
NAMES = json.load(open(CFG.data('dkc1_frame_names.json')))  # [idx, off, name]
def dk1_groups():
    g = {}
    for i, off, n in NAMES:
        k = re.sub(r'\d+$', '', n.replace('GFX_', ''))
        g.setdefault(k, []).append(i)
    return g
KIDDY = [(m.group(1), int(m.group(2), 16)) for m in
         re.finditer(r'"Kiddy_(\w+)",\s*0x([0-9A-Fa-f]+)u', open(CFG.data('kiddy_frames.inc')).read())]
def kiddy_groups():
    g = {}
    for n, o in KIDDY:
        g.setdefault(re.sub(r'\d+$', '', n), []).append(o)
    return g
def bbox(img):
    ys, xs = np.nonzero(img)
    return (xs.min()-0x80, ys.min()-0x80, xs.max()-0x80, ys.max()-0x80) if len(xs) else None
