"""Frame mapping for Cranky (replaces DK) and Candy (replaces Diddy).

Produces ASSIGN_C / ASSIGN_Y: DKC1 frame index -> index raster (256x256, frame
coordinates) and MAP_C / MAP_Y: pose-table offset -> raster for the world map."""
import sys, os, json, math, statistics
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from common import R1, NAMES, dk1_groups, raster, bbox
import candy_poses as CP
from candy_rig import shift, rotate_whole
from puppet import rot_part

g1 = dk1_groups()
import config as CFG
FR = dict(json.load(open(CFG.data('cc_frames.json'))))
def cr(name): return raster(R1, FR['CrankyKong_' + name])
def cy(name): return raster(R1, FR['CandyKong_' + name])
def rng(prefix, a, b, f): return [f(f'{prefix}{i}') for i in range(a, b + 1)]

def feet_row(a):
    """lowest row that is more than 3 pixels wide (ignores Cranky's cane tip)"""
    ys = np.nonzero(a.any(axis=1))[0]
    for y in range(ys.max(), ys.min(), -1):
        if np.count_nonzero(a[y]) > 3:
            return y
    return ys.max()

def feet_x(a):
    y = feet_row(a); xs = np.nonzero(a[max(0, y - 6):y + 1].any(axis=0))[0]
    return (xs.min() + xs.max()) / 2

# ---------------------------------------------------------------- Cranky
W = rng('Walk', 1, 16, cr)
ST = {i: cr(f'Startled{i}') for i in range(1, 25)}
F = rng('Fall', 1, 7, cr)
WP = rng('WindPhonograph', 1, 12, cr)
def st(a, b): return [ST[i] for i in range(a, b + 1)]
CR_SWIM = [rotate_whole(W[i], -65, (126, 112), (126, 108)) for i in (0, 4, 8, 12)]

CR_GROUPS = {
    'Idle': WP, 'Walk': W, 'Run': W, 'HoldWalk': st(9, 12), 'HoldIdle': [ST[10]],
    'Jump': st(8, 11), 'Bounce': st(8, 11), 'Land': st(20, 21), 'Turn': [W[0]],
    'GroundSlap': st(1, 7), 'BeatChest': st(8, 15), 'SitDown': st(20, 24), 'Hurt': F[:4],
    'Failure': F, 'Pickup': st(20, 23), 'Unknown4Pose': [ST[21]], 'ThrowPose': st(13, 18),
    'EnterCrawlSpace': st(22, 24), 'Crawling': st(21, 24), 'TooCloseToEdge': st(15, 19),
    'Unknown2Pose': [WP[0]], 'Unknown3Pose': [WP[0]], 'Unknown1_Pose': [WP[0]],
    'Roll': st(1, 7), 'Swimming': CR_SWIM, 'Duck': st(22, 24), 'UnusedVictory': st(8, 15),
    'SwingOnRope': [ST[10]], 'HangOnVerticalRope': [ST[10]], 'TurnOnVerticalRope': [ST[10]],
    'ClimbUpSingleVerticalRope': st(9, 11), 'DonkeyTakesLead': st(8, 12), 'DiddyTakesLead': st(8, 12),
    'Victory': st(8, 15), 'HeyWatchThis': st(1, 3), 'PrankDiddy': WP, 'FingerBitten': F,
    'RideAnimalBuddy': [ST[21]], 'HangOntoWinky': [ST[10]], 'HangOntoStabbingEnguarde': [ST[10]],
    'RideSteelKeg': W, 'AngledInMinecart': [ST[21]],
}
# ---------------------------------------------------------------- Candy
P = CP.POSES
STAND = [cy('Stand1'), cy('Stand2'), cy('Stand3'), cy('Stand2')]
KISS = rng('BlowKiss', 1, 14, cy)
SWOON = rng('Swoon', 1, 11, cy)
def pp(prefix, n): return [P[f'{prefix}{k}'] for k in range(n)]
CY_GROUPS = {
    'IdleSway': STAND, 'Walk': pp('walk', 8), 'Run': pp('run', 8), 'Jump': [P['jump0'], P['jump1']],
    'Fall': [P['fall0'], P['fall1']], 'Land': [P['crouch']], 'Roll': KISS, 'Hurt': SWOON,
    'TooCloseToEdge': SWOON[:6], 'Bounce': [P['jump0'], P['jump1']], 'Victory': KISS,
    'Failure': SWOON, 'Swimming': pp('swim', 4), 'Pickup': [P['crouch']], 'HoldWalk': pp('carrywalk', 8),
    'Throw': [P['throw']], 'ScratchHead': STAND, 'Duck': [P['duck']], 'Crawling': pp('crawl', 4),
    'EnterCrawlSpace': [P['duck']], 'HangOnVerticalRope': [P['hang0']], 'TurnOnVerticalRope': [P['hang1']],
    'ClimbUpSingleVerticalRope': [P['hang0'], P['hang1']], 'RideSteelKeg': pp('run', 8),
    'SwingOnRope': [P['hang0'], P['hang1']], 'DiddyTakesLead': KISS, 'DonkeyTakesLead': [P['jump0']],
    'RideAnimalBuddy': [P['sit']], 'Unknown1Pose': [P['sit']], 'HangOntoWinky': [P['hang0']],
    'HangOntoStabbingEnguarde': [P['hang0']], 'AngledInMinecart': [P['sit']], 'IdleInMinecart': [P['sit']],
}
TOP_ALIGN = {'SwingOnRope', 'HangOnVerticalRope', 'TurnOnVerticalRope', 'ClimbUpSingleVerticalRope',
             'HangOntoWinky', 'HangOntoStabbingEnguarde'}
SEAT_ALIGN = {'RideAnimalBuddy', 'Unknown1Pose'}
CART_ALIGN = {'AngledInMinecart', 'IdleInMinecart'}

def phase(n, m, i): return min(m - 1, i * m // n)

def top_point(a):
    ys, xs = np.nonzero(a); t = ys.min(); band = xs[ys <= t + 4]
    return int(t), int(np.median(band))
def seat_point(a):
    ys, xs = np.nonzero(a); b = ys.max(); band = xs[ys >= b - 8]
    return int(b), int(band.min())

def build(groups, prefix, ref_feet_y, ref_feet_x, cart_lift=0):
    out = {}
    for grp, srcs in groups.items():
        idxs = g1.get(prefix + grp)
        if not idxs:
            continue
        for n, i in enumerate(idxs):
            s = srcs[phase(len(idxs), len(srcs), n)]
            o = raster(R1, NAMES[i][1])
            if grp in TOP_ALIGN:
                ot, ox = top_point(o); stt, sx = top_point(s)
                a = shift(s, ox - sx, ot - stt)
            elif grp in SEAT_ALIGN:
                ob, ox = seat_point(o); sb, sx = seat_point(s)
                a = shift(s, ox - sx, ob - sb)
            elif grp in CART_ALIGN:
                ot, ox = top_point(o); stt, sx = top_point(s)
                a = shift(s, ox - sx, ot - stt - cart_lift)
                ys = np.nonzero(o)[0]; a[ys.max() + 1:] = 0
            else:
                a = shift(s, int(round(ref_feet_x - feet_x(s))), int(ref_feet_y - feet_row(s)))
            out[i] = a
    return out

dk_y = statistics.median(feet_row(raster(R1, NAMES[i][1])) for i in g1['DonkeyKong_Walk'] + g1['DonkeyKong_Idle'])
dk_x = statistics.median(feet_x(raster(R1, NAMES[i][1])) for i in g1['DonkeyKong_Walk'] + g1['DonkeyKong_Idle'])
dd_y = statistics.median(feet_row(raster(R1, NAMES[i][1])) for i in g1['Diddy_Walk'] + g1['Diddy_IdleSway'])
dd_x = statistics.median(feet_x(raster(R1, NAMES[i][1])) for i in g1['Diddy_Walk'] + g1['Diddy_IdleSway'])
ASSIGN_C = build(CR_GROUPS, 'DonkeyKong_', dk_y, dk_x, 6)
ASSIGN_Y = build(CY_GROUPS, 'Diddy_', dd_y, dd_x, 14)

# ---------------------------------------------------------------- world map (small)
def small(a, scale):
    ys, xs = np.nonzero(a)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    w, h = max(1, round((x1 - x0) * scale)), max(1, round((y1 - y0) * scale))
    out = np.zeros_like(a)
    for y in range(h):
        for x in range(w):
            # sample the centre of each source cell, prefer non-transparent
            sx0, sx1 = x0 + int(x / scale), x0 + int((x + 1) / scale)
            sy0, sy1 = y0 + int(y / scale), y0 + int((y + 1) / scale)
            blk = a[sy0:max(sy1, sy0 + 1), sx0:max(sx1, sx0 + 1)]
            v = blk[blk.shape[0] // 2, blk.shape[1] // 2]
            if v == 0 and np.count_nonzero(blk) * 2 > blk.size:
                nz = blk[blk > 0]; v = np.bincount(nz).argmax()
            out[y0 + y, x0 + x] = v
    return out

def ptr_at(pose):
    P0 = 0x3BCC9C
    a, b, c = R1[P0 + pose:P0 + pose + 3]
    return (c << 16 | b << 8 | a) & 0x3FFFFF

def map_set(poses, srcs, ref_poses, scale):
    ref = [raster(R1, ptr_at(p)) for p in ref_poses]
    ry = statistics.median(feet_row(r) for r in ref); rx = statistics.median(feet_x(r) for r in ref)
    out = {}
    sm = [small(s, scale) for s in srcs]
    for n, p in enumerate(poses):
        s = sm[phase(len(poses), len(sm), n)]
        out[p] = shift(s, int(round(rx - feet_x(s))), int(ry - feet_row(s)))
    return out

def poses_of(idxs): return [0x8C + 4 * i for i in idxs]
dk_map_walk = poses_of(g1['MapDonkeyKong_Walk']); dk_map_vict = poses_of(g1['MapDonkeyKong_Victory'])
dd_map_walk = [0x1054 + 4 * k for k in range(8)]; dd_map_vict = [0x1074 + 4 * k for k in range(11)]
dk_t = [0x12AC + 4 * k for k in range(9)]; dd_t = [0x12D0 + 4 * k for k in range(8)]
MAP_C, MAP_Y = {}, {}
CS, YS = 0.5, 0.34
MAP_C.update(map_set(dk_map_walk, W[::2], dk_map_walk, CS))
MAP_C.update(map_set(dk_map_vict, st(8, 15), dk_map_walk, CS))
MAP_C.update(map_set(dk_t, W[::2], dk_t, CS))
MAP_Y.update(map_set(dd_map_walk, pp('walk', 8), dd_map_walk, YS))
MAP_Y.update(map_set(dd_map_vict, KISS[::2], dd_map_walk, YS))
MAP_Y.update(map_set(dd_t, pp('walk', 8), dd_t, YS))
