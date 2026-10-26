"""Shared mapping logic: which Kiddy/Dixie frame replaces each DK/Diddy frame."""
import sys, json, re, statistics
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

from common import R1, R2, R3, ptr, NAMES, dk1_groups, kiddy_groups, raster, bbox
from dkcsprite import parse, plausible
from anim2 import frames_of, gfx_ok
TABLE = 0x3BCD28
g1 = dk1_groups()
kg = kiddy_groups()

# ---------------- animation mapping ----------------
DK_TO_KIDDY = {
    'Idle': 'LookAroundIdle', 'Walk': 'Walk', 'Jump': 'Jump', 'Land': 'Land', 'Turn': 'Turn',
    'GroundSlap': 'Tantrum', 'BeatChest': 'Victory', 'SitDown': 'SitDown', 'Hurt': 'Hurt',
    'Pickup': 'Pickup', 'Unknown4Pose': 'Pickup', 'HoldWalk': 'HoldWalk', 'ThrowPose': ('Throw', 0, 13),
    'Run': 'Run', 'EnterCrawlSpace': 'Duck', 'Crawling': 'Duck', 'TooCloseToEdge': 'LookAroundIdle',
    'Unknown2Pose': 'LookAroundIdle', 'Bounce': 'Jump', 'Roll': 'Roll', 'Swimming': 'Swim',
    'Unknown3Pose': 'LookAroundIdle', 'RideAnimalBuddy': 'SitOnAnimalBuddy',
    'RideSteelKeg': 'RideSteelKeg', 'HangOntoStabbingEnguarde': 'HangFromSquawks',
    'HangOntoWinky': 'HangFromSquawks', 'Duck': 'Duck', 'UnusedVictory': 'Victory',
    'SwingOnRope': 'IdleOnVerticalRope', 'HoldIdle': 'HoldWalk', 'AngledInMinecart': 'RideToboggan',
    'HangOnVerticalRope': 'HangOnVerticalRope', 'TurnOnVerticalRope': 'TurnOnVerticalRope',
    'ClimbUpSingleVerticalRope': 'ClimbUpSingleVerticalRope', 'Unknown1_Pose': 'LookAroundIdle',
    'DonkeyTakesLead': 'KiddyTakesLead', 'DiddyTakesLead': 'DixieTakesLead', 'Failure': 'Tantrum',
    'Victory': 'Victory', 'HeyWatchThis': 'Victory', 'PrankDiddy': 'PullPajamas',
    'FingerBitten': 'Tantrum',
}
# DKC1 Diddy group -> (DKC2 Diddy animation id, optional frame slice). Dixie anim = id + 0xA3.
DIDDY_TO_DIXIE = {
    'IdleSway': (0x01,), 'Walk': (0x3c,), 'Run': (0x3d,), 'Jump': (0x2a,), 'Fall': (0x3e,),
    'Land': (0x08,), 'Roll': (0x19,), 'Hurt': (0x28,), 'TooCloseToEdge': (0x41,),
    'Bounce': (0x4b,), 'Victory': (0x38,), 'Failure': (0x42, 0, 2), 'Swimming': (0x43,),
    'Pickup': (0x45,), 'HoldWalk': (0x54,), 'Throw': (0x14,), 'ScratchHead': (0x01,),
    'RideAnimalBuddy': (0x58,), 'Unknown1Pose': (0x58,), 'HangOntoWinky': (0x58,),
    'Duck': (0x0e,), 'Crawling': (0x13, 0, 5), 'EnterCrawlSpace': (0x0e,),
    'HangOntoStabbingEnguarde': (0x5d,), 'HangOnVerticalRope': (0x30,),
    'TurnOnVerticalRope': (0x32,), 'ClimbUpSingleVerticalRope': (0x31,), 'RideSteelKeg': (0x01,),
    'SwingOnRope': (0x2b,), 'AngledInMinecart': (0x0e,), 'IdleInMinecart': (0x0e,),
    'DiddyTakesLead': (0x2c,), 'DonkeyTakesLead': (0x2d,),
}

def dixie_frames(spec):
    k = spec[0]
    fr = list(dict.fromkeys(x for x in frames_of(k + 0xA3)[0] if gfx_ok(x)))
    if len(spec) == 3:
        fr = fr[spec[1]:spec[2]]
    return [ptr(R2, 0x3C8000 + x) for x in fr]

def phase(n, m, i):
    return min(m - 1, i * m // n)

assign = {}   # dkc1 frame index -> (source rom name, offset)
for grp, idxs in g1.items():
    if grp.startswith('DonkeyKong_'):
        tgt = DK_TO_KIDDY.get(grp[len('DonkeyKong_'):])
        if not tgt:
            continue
        if isinstance(tgt, tuple):
            src = kg[tgt[0]][tgt[1]:tgt[2]]
        else:
            src = kg[tgt]
        for n, i in enumerate(idxs):
            assign[i] = ('R3', src[phase(len(idxs), len(src), n)])
    elif grp.startswith('Diddy_'):
        spec = DIDDY_TO_DIXIE.get(grp[len('Diddy_'):])
        if not spec:
            continue
        src = dixie_frames(spec)
        for n, i in enumerate(idxs):
            assign[i] = ('R2', src[phase(len(idxs), len(src), n)])
kept = [i for i in range(965) if i not in assign]
print('replaced', len(assign), 'kept', len(kept), sorted({re.sub(r'\d+$', '', NAMES[i][2]) for i in kept}))

# ---------------- feet alignment ----------------
def bottoms(rom_, offs):
    return statistics.median(bbox(raster(rom_, o))[3] for o in offs)
dk_feet = bottoms(R1, [NAMES[i][1] for g in ('DonkeyKong_Idle', 'DonkeyKong_Walk', 'DonkeyKong_Run') for i in g1[g]])
ki_feet = bottoms(R3, kg['LookAroundIdle'] + kg['Walk'] + kg['Run'])
dd_feet = bottoms(R1, [NAMES[i][1] for g in ('Diddy_IdleSway', 'Diddy_Walk', 'Diddy_Run') for i in g1[g]])
dx_feet = bottoms(R2, dixie_frames((0x01,)) + dixie_frames((0x3c,)) + dixie_frames((0x3d,)))
SHIFT = {'R3': int(round(dk_feet - ki_feet)), 'R2': int(round(dd_feet - dx_feet))}
print('feet', dk_feet, ki_feet, dd_feet, dx_feet, 'shift', SHIFT)

SRC = {'R2': R2, 'R3': R3}
def frame_bytes(tag, off):
    s = SRC[tag]
    f = parse(s, off)
    b = bytearray(s[off:off + f['size']])
    dy = SHIFT[tag]
    for k in range(len(f['pos'])):
        y = b[9 + k * 2] + dy
        assert 0 <= y <= 255
        b[9 + k * 2] = y
    # sanity: must fit DKC1's 32-char Kong VRAM slot
    span = max(f['d1n'], f['d2s'] + f['d2n'] if f['d2n'] else 0)
    assert span <= 32, (tag, hex(off), span)
    return bytes(b)


import numpy as _np
_M = _np.load(CFG.data('inactive_M.npy'))
def read_pal(src, off):
    return [src[off + i * 2] | src[off + i * 2 + 1] << 8 for i in range(15)]
def inactive(p):
    out = []
    for v in p:
        r, g, b = v & 31, (v >> 5) & 31, (v >> 10) & 31
        r, g, b = [max(0, min(31, int(round(x)))) for x in _np.array([r, g, b, 1.0]) @ _M]
        out.append(r | g << 5 | b << 10)
    return out
