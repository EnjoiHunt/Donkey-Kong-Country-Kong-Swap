"""DKC1 Kong Swap v0.2: keep DK & Diddy, add Kiddy & Dixie, switch with L/R on the map.

Layout (8 MB ExHiROM):
  0x000000-0x3FFFFF  original DKC1 (banks $C0-$FF / $80-$BF), untouched except hooks
  0x400000-0x7FFFFF  banks $40-$7D. Upper halves mirror banks $00-$3F upper halves
                     (so bank $00 vectors/header and any $00-$3F code reads still work);
                     lower halves ($xx:0000-7FFF) hold the new data:
     $40:0000  alternate pose table      $40:3000  alternate Kong palettes
     $40:3100  map Kiddy palette          $40:4000  hook code (asar)
     $41-$5F:0000-7FFF  Kiddy/Dixie frames
"""
import sys, json, subprocess, statistics
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

import hashlib
EXPECT = {'DKC1_ROM': ('fa8cacf5bbfc39ee6bbaa557adf89133d60d42f6cf9e1db30d5a36a469f74d15', 'Donkey Kong Country (USA) v1.0'),
          'DKC2_ROM': ('35421a9af9dd011b40b91f792192af9f99c93201d8d394026bdfb42cbf2d8633', "Donkey Kong Country 2 - Diddy's Kong Quest (USA) (En,Fr)"),
          'DKC3_ROM': ('2277a2d8dddb01fe5cb0ae9a0fa225d42b3a11adccaeafa18e3c339b3794a32b', "Donkey Kong Country 3 - Dixie Kong's Double Trouble! (USA) (En,Fr)")}
for _k, (_h, _name) in EXPECT.items():
    _p = getattr(CFG, _k)
    if not os.path.exists(_p):
        sys.exit(f'Missing {_k}: put your headerless {_name} ROM at {_p} (or set the {_k} environment variable).')
    _got = hashlib.sha256(open(_p, 'rb').read()).hexdigest()
    if _got != _h:
        sys.exit(f'{_k} ({_p}) is not a clean headerless {_name}.\n  expected SHA-256 {_h}\n  got      {_got}')
import kongmap as K
import numpy as np
from common import ptr
from kongmap import R1, R2, R3, parse, raster, bbox, NAMES, dk1_groups
from palprobe import pal_at

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(CFG.BUILD, 'dkc1_kong_swap.sfc')
SIZE = 0x800000
rom = bytearray(R1) + bytearray(SIZE - len(R1))

# --- ExHiROM mirroring of banks $00-$3F upper halves -------------------------
for b in range(0x40):
    rom[0x400000 + b * 0x10000 + 0x8000:0x400000 + b * 0x10000 + 0x10000] = R1[b * 0x10000 + 0x8000:b * 0x10000 + 0x10000]
for hdr in (0x00FFC0, 0x40FFC0):
    rom[hdr + 0x15] = 0x35          # map mode: ExHiROM, FastROM
    rom[hdr + 0x17] = 0x0D          # ROM size: 8 Mbit*... (8 MB rounds up to 8 MB class)

def lo_half(bank):
    return 0x400000 + (bank - 0x40) * 0x10000

# --- alternate pose table ----------------------------------------------------
POSE = 0x3BCC9C
POSE_LEN = 0x3BF790 - POSE
assert POSE_LEN < 0x3000
alt = bytearray(R1[POSE:POSE + POSE_LEN])
T0 = lo_half(0x40)

# --- place frames --------------------------------------------------------------
free = [[lo_half(b), lo_half(b) + 0x8000] for b in range(0x41, 0x7C)]
placed = {}
def put(data):
    for ext in free:
        if ext[1] - ext[0] >= len(data):
            o = ext[0]; rom[o:o + len(data)] = data; ext[0] += len(data); return o
    raise SystemExit('out of space')
def snes(o):  # file offset in $40-$7D region -> 24-bit address
    return 0x400000 + (o - 0x400000)

assign = dict(K.assign)

# overworld map sprite: Kiddy's DKC3 map frames
d3 = json.load(open(CFG.data('dkc3_all.json')))['ents']
g1 = dk1_groups()
MAP_WALK = [d3[i] for i in range(2444, 2452)]     # DKC3 world-map Kiddy, side view
MAP_VICT = [d3[i] for i in range(2524, 2531)]
dk_map_feet = statistics.median(bbox(raster(R1, NAMES[i][1]))[3] for i in g1['MapDonkeyKong_Walk'])
ki_map_feet = statistics.median(bbox(raster(R3, o))[3] for o in MAP_WALK)
MAP_SHIFT = int(round(dk_map_feet - ki_map_feet))
for grp, src in (('MapDonkeyKong_Walk', MAP_WALK), ('MapDonkeyKong_Victory', MAP_VICT)):
    idxs = g1[grp]
    for n, i in enumerate(idxs):
        assign[i] = ('R3map', src[K.phase(len(idxs), len(src), n)])

# map Diddy -> Dixie's DKC3 map frames (pose-table offsets, outside the Kong index range)
DIX_WALK = [d3[i] for i in range(2484, 2492)]     # DKC3 world-map Dixie, side view
DIX_VICT = [d3[i] for i in range(2549, 2554)]
def pose_off(e): return e
dd_map_walk = [0x1054 + 4 * k for k in range(8)]
dd_map_vict = [0x1074 + 4 * k for k in range(11)]
def ptr_at(pose):
    a, b, c, d = R1[POSE + pose:POSE + pose + 4]; return (c << 16 | b << 8 | a) & 0x3FFFFF
dd_map_feet = statistics.median(bbox(raster(R1, ptr_at(p)))[3] for p in dd_map_walk)
dx_map_feet = statistics.median(bbox(raster(R3, o))[3] for o in DIX_WALK)
DIX_MAP_SHIFT = int(round(dd_map_feet - dx_map_feet))
pose_assign = {}
for poses, src in ((dd_map_walk, DIX_WALK), (dd_map_vict, DIX_VICT)):
    for n, p in enumerate(poses):
        pose_assign[p] = ('R3mapD', src[K.phase(len(poses), len(src), n)])
# island overview: tiny Kong frames
TK = MAP_WALK                                      # island uses the same side-view frames
TD = DIX_WALK
dk_t = [0x12AC + 4 * k for k in range(9)]; dd_t = [0x12D0 + 4 * k for k in range(8)]
TK_SHIFT = int(round(statistics.median(bbox(raster(R1, ptr_at(p)))[3] for p in dk_t) - statistics.median(bbox(raster(R3, o))[3] for o in TK)))
TD_SHIFT = int(round(statistics.median(bbox(raster(R1, ptr_at(p)))[3] for p in dd_t) - statistics.median(bbox(raster(R3, o))[3] for o in TD)))
for poses, src, tag in ((dk_t, TK, 'R3tinyK'), (dd_t, TD, 'R3tinyD')):
    for n, p in enumerate(poses):
        pose_assign[p] = (tag, src[K.phase(len(poses), len(src), n)])

# animal riding + mine carts: composed Kiddy/Dixie frames aligned to each original pose
import math as _m
from compose import shifted as _sh, encode as _enc, top_point as _top, seat_point as _seat
from common import kiddy_groups as _kgf
from anim2 import frames_of as _fo, gfx_ok as _gok
_kg = _kgf()
_dix_sit = ptr(R2, 0x3C8000 + [x for x in _fo(0x4C + 0xA3)[0] if _gok(x)][0])
def _ang(a):
    ys, xs = np.nonzero(a > 0); x = xs - xs.mean(); y = ys - ys.mean()
    w, v = np.linalg.eigh(np.cov(np.vstack([x, y]))); vx, vy = v[:, 1]
    if vy > 0: vx, vy = -vx, -vy
    return _m.degrees(_m.atan2(vx, -vy))
_tob = [(_ang(raster(R3, o)), o) for o in _kg['RideToboggan']]
def _ride(orig, srom, soff):
    o = raster(R1, orig); s_ = raster(srom, soff)
    ob, ox = _seat(o); sb, sx = _seat(s_)
    return _enc(_sh(srom, soff, ox - sx, ob - sb))
def _cart(orig, srom, soff):
    o = raster(R1, orig); s_ = raster(srom, soff)
    ot, ox = _top(o); st, sx = _top(s_)
    a = _sh(srom, soff, ox - sx, ot - st)
    ys, _ = np.nonzero(o); a[ys.max() + 1:] = 0
    return _enc(a)
def _pick_tob(off):
    t = _ang(raster(R1, off))
    if t < -30: t = max(-16, t + 90)
    return min(_tob, key=lambda p: abs(p[0] - t))[1]
RAW = {}
def _raw(i, data):
    RAW[i] = data; assign[i] = ('RAW', i)
_sit = _kg['SitOnAnimalBuddy']
for grp in ('DonkeyKong_RideAnimalBuddy', 'DonkeyKong_HangOntoWinky', 'DonkeyKong_HangOntoStabbingEnguarde'):
    for n, i in enumerate(g1[grp]):
        _raw(i, _ride(NAMES[i][1], R3, _sit[n % len(_sit)]))
for grp in ('Diddy_RideAnimalBuddy', 'Diddy_Unknown1Pose', 'Diddy_HangOntoWinky', 'Diddy_HangOntoStabbingEnguarde'):
    for i in g1[grp]:
        _raw(i, _ride(NAMES[i][1], R2, _dix_sit))
for i in g1['DonkeyKong_AngledInMinecart']:
    _raw(i, _cart(NAMES[i][1], R3, _pick_tob(NAMES[i][1])))
for i in g1['Diddy_AngledInMinecart'] + g1['Diddy_IdleInMinecart']:
    _raw(i, _cart(NAMES[i][1], R2, _dix_sit))
EMPTY_FRAME = bytes([0, 1, 0, 0, 0, 1, 0, 0, 0x80, 0x80]) + bytes(32)   # one blank 8x8 tile

# extra-life HUD balloon: DK's art, recoloured to look right under Kiddy's palette
_dkp = K.read_pal(R1, 0x3C849A); _kp = K.read_pal(R3, 0x3D34CF)
def _rgb(v): return ((v & 31) << 3, ((v >> 5) & 31) << 3, ((v >> 10) & 31) << 3)
def _d2(a, b): return sum((x - y) ** 2 for x, y in zip(a, b))
BAL_MAP = [0] + [1 + min(range(15), key=lambda j: _d2(_rgb(_dkp[i - 1]), _rgb(_kp[j]))) for i in range(1, 16)]
def recolor(off):
    f = parse(R1, off); b = bytearray(R1[off:off + f['size']]); p = f['data'] - off
    for t in range(f['d1n'] + f['d2n']):
        tb = b[p + t * 32:p + t * 32 + 32]; out = bytearray(32)
        for y in range(8):
            for x in range(8):
                sh = 7 - x
                v = ((tb[y*2] >> sh) & 1) | (((tb[y*2+1] >> sh) & 1) << 1) | (((tb[16+y*2] >> sh) & 1) << 2) | (((tb[16+y*2+1] >> sh) & 1) << 3)
                v = BAL_MAP[v]
                for bit, o in ((0, 0), (1, 1), (2, 16), (3, 17)):
                    if v >> bit & 1: out[y*2+o] |= 1 << sh
        b[p + t * 32:p + t * 32 + 32] = out
    return bytes(b)
for i in g1['HUDBalloon_Idle']:
    assign[i] = ('REMAP', NAMES[i][1])

def fbytes(tag, off):
    if tag == 'REMAP':
        return recolor(off)
    if tag == 'EMPTY':
        return EMPTY_FRAME
    if tag == 'RAW':
        return RAW[off]
    if tag in ('R3tinyK', 'R3tinyD'):
        s, dy = R3, (TK_SHIFT if tag == 'R3tinyK' else TD_SHIFT)
    elif tag == 'R3map':
        s, dy = R3, MAP_SHIFT
    elif tag == 'R3mapD':
        s, dy = R3, DIX_MAP_SHIFT
    else:
        s, dy = K.SRC[tag], K.SHIFT[tag]
    f = parse(s, off)
    b = bytearray(s[off:off + f['size']])
    for k in range(len(f['pos'])):
        b[9 + k * 2] = max(0, min(255, b[9 + k * 2] + dy))
    assert max(f['d1n'], (f['d2s'] + f['d2n']) if f['d2n'] else 0) <= 32
    return bytes(b)

for t in sorted(set(assign.values()) | set(pose_assign.values()), key=lambda t: (-len(fbytes(*t)), str(t))):
    placed[t] = put(fbytes(*t))
for i, t in assign.items():
    a = snes(placed[t])
    e = (0x3BCD28 + i * 4) - POSE
    alt[e:e + 4] = bytes([a & 255, (a >> 8) & 255, a >> 16, 0])
for p, t in pose_assign.items():
    a = snes(placed[t])
    alt[p:p + 4] = bytes([a & 255, (a >> 8) & 255, a >> 16, 0])
rom[T0:T0 + len(alt)] = alt

# --- per-Kong tables (2.0): Kiddy-only at $7D:0000, Dixie-only at $7D:3000 ----------
def big_pose(p):   # mirrors PoseSide in kong_swap.asm
    return p < 0x950 or 0x12AC <= p < 0x12D0
orig = R1[POSE:POSE + POSE_LEN]
altK, altD = bytearray(orig), bytearray(orig)
for p in range(0, POSE_LEN, 4):
    if alt[p:p + 4] != orig[p:p + 4]:
        dst = altK if big_pose(p) else altD
        dst[p:p + 4] = alt[p:p + 4]
rom[lo_half(0x7D):lo_half(0x7D) + POSE_LEN] = altK
rom[lo_half(0x7D) + 0x3000:lo_half(0x7D) + 0x3000 + POSE_LEN] = altD

# Kiddy's ground-pound slam frames (his DKC3 roll / somersault), pointer table at $40:3300
POUND = K.kiddy_groups()['Roll'] if hasattr(K, 'kiddy_groups') else None
from common import kiddy_groups as _kg
POUND = _kg()['Roll'][2:12] + [_kg()['SitOnEgg'][0]]   # 10 flip frames + butt-slam pose
PT = lo_half(0x40) + 0x3300
for n, off in enumerate(POUND):
    t = ('R3', off)
    if t not in placed:
        placed[t] = put(fbytes(*t))
    a = snes(placed[t])
    rom[PT + n * 4:PT + n * 4 + 4] = bytes([a & 255, (a >> 8) & 255, a >> 16, 0])
assert len(POUND) == 11

# Dixie's helicopter spin (DKC2 graphics $824-$850), pointer table at $40:3200
SPIN = [ptr(R2, 0x3C8000 + g) for g in json.load(open(CFG.data('spin_gids.json')))]
GT = lo_half(0x40) + 0x3200
for n, off in enumerate(SPIN):
    t = ('R2', off)
    if t not in placed:
        placed[t] = put(fbytes(*t))
    a = snes(placed[t])
    rom[GT + n * 4:GT + n * 4 + 4] = bytes([a & 255, (a >> 8) & 255, a >> 16, 0])

# --- palettes --------------------------------------------------------------------
P0 = lo_half(0x40) + 0x3000
rom[P0:P0 + 0xF0] = R1[0x3C8422:0x3C8512]
def write_pal(off, p):
    for i, v in enumerate(p):
        rom[off + i * 2] = v & 255; rom[off + i * 2 + 1] = v >> 8
kid = K.read_pal(R3, 0x3D34CF); dix = K.read_pal(R2, 0x3D6574)
for base, p in ((0x849A, kid), (0x8422, dix)):
    o = P0 + base - 0x8422
    write_pal(o, p); write_pal(o + 0x1E, K.inactive(p)); write_pal(o + 0x3C, p); write_pal(o + 0x5A, K.inactive(p))
mp = K.read_pal(R3, 0x3D4387)          # DKC3 shared overworld palette (Kiddy + Dixie) -> map sprite slot 1
write_pal(lo_half(0x40) + 0x3100, mp)

# ghost palettes for the absent partner on the world map (sprite palette 0): pale blue-grey
def ghost(p):
    out = []
    for v in p:
        r, g, bl = v & 31, (v >> 5) & 31, (v >> 10) & 31
        n = (0.30 * r + 0.59 * g + 0.11 * bl) / 31
        c = (min(31, round(9 + 17 * n)), min(31, round(12 + 17 * n)), min(31, round(17 + 14 * n)))
        out.append(c[0] | c[1] << 5 | c[2] << 10)
    return out
dkmap = [R1[0x39BFC5 + 2 * i] | R1[0x39BFC6 + 2 * i] << 8 for i in range(15)]
write_pal(lo_half(0x40) + 0x3500, ghost(dkmap))        # ghost of DK / Diddy
write_pal(lo_half(0x40) + 0x351E, ghost(mp))           # ghost of Kiddy / Dixie


# --- level-complete face icons (Kiddy / Dixie) -------------------------------------
import faces as FC
kr, km = FC.kiddy2(20, 0, 24, 22, 15, 0, 1); km[15, 0] = False
dr_, dm = FC.dixie2(4, 0, 26, 24, 15, 1, 0)
cols = [tuple(int(c) for c in kr[y, x]) for y in range(16) for x in range(16) if km[y, x]] + \
       [tuple(int(c) for c in dr_[y, x]) for y in range(16) for x in range(16) if dm[y, x]]
def near(c, p): return sum((a - b) ** 2 for a, b in zip(c, p))
WHITE, BLACK = (248, 248, 248), (0, 0, 0)
rest = [c for c in cols if near(c, WHITE) > 900 and near(c, BLACK) > 900]
# k-means to 13 colours
import random
random.seed(3)
uniq = sorted(set(rest), key=lambda c: -rest.count(c))
cent = uniq[:13] + [uniq[0]] * max(0, 13 - len(uniq))
for _ in range(20):
    groups = [[] for _ in cent]
    for c in rest: groups[min(range(len(cent)), key=lambda i: near(c, cent[i]))].append(c)
    cent = [tuple(sum(v[k] for v in g) // len(g) for k in range(3)) if g else cent[i] for i, g in enumerate(groups)]
palette = [WHITE, BLACK] + cent                 # indices 1..15
def idx_of(c): return 1 + min(range(15), key=lambda i: near(c, palette[i]))
def tiles16(rgb, m):
    t = []
    for ty in (0, 1):
        row = []
        for tx in (0, 1):
            b = bytearray(32)
            for y in range(8):
                for x in range(8):
                    Y, X = ty * 8 + y, tx * 8 + x
                    v = idx_of(tuple(int(c) for c in rgb[Y, X])) if m[Y, X] else 0
                    s = 7 - x
                    for bit, off in ((0, 0), (1, 1), (2, 16), (3, 17)):
                        if v >> bit & 1: b[y * 2 + off] |= 1 << s
            row.append(bytes(b))
        t.append(row)
    return t
KT, DT = tiles16(kr, km), tiles16(dr_, dm)
FR = 0x7C0000
for f in range(8):
    base = FR + f * 0x400
    rom[base:base + 0x380] = R1[0x020000 + f * 0x380:0x020000 + (f + 1) * 0x380]
    rom[base + 0x380:base + 0x400] = bytes(0x80)
    for T, t0 in ((KT, 0x4C), (DT, 0x4E)):
        for ty in (0, 1):
            for tx in (0, 1):
                o = base + ((t0 + tx + ty * 16) - 0x40) * 32
                rom[o:o + 32] = T[ty][tx]
fp = lo_half(0x40) + 0x3400
for i, c in enumerate(cent):
    v = (c[0] >> 3) | ((c[1] >> 3) << 5) | ((c[2] >> 3) << 10)
    rom[fp + i * 2] = v & 255; rom[fp + i * 2 + 1] = v >> 8
from PIL import Image
prev = Image.new('RGB', (34, 16), (60, 70, 50))
for T, ox in ((KT, 0), (DT, 18)):
    for ty in (0, 1):
        for tx in (0, 1):
            from dkcsprite import decode_tile
            px = decode_tile(T[ty][tx])
            for y in range(8):
                for x in range(8):
                    if px[y][x]: prev.putpixel((ox + tx * 8 + x, ty * 8 + y), palette[px[y][x] - 1])
prev.resize((34 * 10, 160), Image.NEAREST).save(os.path.join(CFG.BUILD, 'face_tiles_preview.png'))

# --- assemble hooks --------------------------------------------------------------
open(OUT, 'wb').write(rom)
r = subprocess.run([CFG.ASAR, '--fix-checksum=off', os.path.join(CFG.SRC, 'kong_swap.asm'), OUT],
                   capture_output=True, text=True)
print(r.stdout, r.stderr)
assert r.returncode == 0
rom = bytearray(open(OUT, 'rb').read())
assert len(rom) == SIZE

# --- checksum (8 MB: 4 MB + 2 MB counted twice) ----------------------------------
for hdr in (0x00FFC0, 0x40FFC0):
    rom[hdr + 0x1C:hdr + 0x20] = b'\xff\xff\x00\x00'
s = sum(rom) & 0xFFFF
for hdr in (0x00FFC0, 0x40FFC0):
    rom[hdr + 0x1E] = s & 255; rom[hdr + 0x1F] = s >> 8
    rom[hdr + 0x1C] = (s ^ 0xFFFF) & 255; rom[hdr + 0x1D] = (s ^ 0xFFFF) >> 8
open(OUT, 'wb').write(rom)
used = sum(e[0] - (lo_half(0x41) + n * 0x10000) for n, e in enumerate(free))
print('frames', len(placed), 'bytes used', used, 'map shift', MAP_SHIFT, DIX_MAP_SHIFT)

# --- patch files --------------------------------------------------------------------
import patches as P
_src = open(CFG.DKC1_ROM, 'rb').read(); _dst = open(OUT, 'rb').read()
open(os.path.join(CFG.BUILD, 'dkc1_kong_swap.bps'), 'wb').write(P.make_bps(_src, _dst))
open(os.path.join(CFG.BUILD, 'dkc1_kong_swap.ips'), 'wb').write(P.make_ips(_src, _dst))
print('wrote', OUT, 'plus dkc1_kong_swap.bps and dkc1_kong_swap.ips in', CFG.BUILD)
