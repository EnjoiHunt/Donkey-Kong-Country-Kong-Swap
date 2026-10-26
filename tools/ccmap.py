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
import cranky_rig as CRIG

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


def _fam_shift(ref):
    return ref

def _flip(a): return np.roll(a[:, ::-1], 1, axis=1)          # mirror about x = 128
ANCHOR = {}                                                  # id(frame) -> riding hip point
def _cr_rider(tnt, wk):
    t = _flip(cr(tnt)); w = cr(wk)
    legs = w.copy(); legs[:116] = 0
    legs[~np.isin(legs, [1, 2, 3, 4, 5, 6, 7, 0xB, 0xC, 0xD])] = 0
    legs[:, 136:] = 0
    ys, xs = np.nonzero(t); tb = ys.max()
    comp = shift(legs, 4, tb - np.nonzero(legs)[0].min() - 4)
    comp[t > 0] = t[t > 0]
    ANCHOR[id(comp)] = (int(xs.min()) + 8, int(tb) - 2)
    return comp
CR_RIDE = [_cr_rider('ThrowTNT1', 'Walk1'), _cr_rider('ThrowTNT6', 'Walk1')]   # leaning forward, holding on
CR_CART = [_flip(cr('ThrowTNT1'))]
CLEAN = [ST[15], ST[16]]                       # arms up, no eye-pop
SW, RA = CRIG.SWING, CRIG.RAISED                 # cane swing / cane raised (from WindPhonograph1)
CR_GROUPS = {
    'Idle': WP, 'Walk': W, 'Run': W, 'HoldWalk': CLEAN, 'HoldIdle': [ST[15]],
    'Jump': [RA[0]], 'Bounce': [RA[0], RA[1]], 'Land': st(20, 21), 'Turn': [W[0]],
    'GroundSlap': SW, 'BeatChest': RA + CLEAN, 'SitDown': st(20, 24), 'Hurt': F[:4],
    'Failure': F, 'Pickup': st(20, 23), 'Unknown4Pose': [ST[21]], 'ThrowPose': st(16, 18),
    'EnterCrawlSpace': st(22, 24), 'Crawling': st(21, 24), 'TooCloseToEdge': st(16, 19),
    'Unknown2Pose': [WP[0]], 'Unknown3Pose': [WP[0]], 'Unknown1_Pose': [WP[0]],
    'Roll': SW, 'Swimming': CR_SWIM, 'Duck': st(22, 24), 'UnusedVictory': RA + CLEAN,
    'SwingOnRope': [ST[15]], 'HangOnVerticalRope': [ST[15]], 'TurnOnVerticalRope': [ST[15]],
    'ClimbUpSingleVerticalRope': CLEAN, 'DonkeyTakesLead': RA + CLEAN, 'DiddyTakesLead': RA + CLEAN,
    'Victory': RA + CLEAN, 'HeyWatchThis': SW[:3], 'PrankDiddy': WP, 'FingerBitten': F,
    'RideAnimalBuddy': CR_RIDE, 'HangOntoWinky': CR_RIDE, 'HangOntoStabbingEnguarde': CR_RIDE,
    'RideSteelKeg': W, 'AngledInMinecart': CR_CART,
}
# ---------------------------------------------------------------- Candy
P = CP.POSES
STAND = [cy('Stand1'), cy('Stand2'), cy('Stand3'), cy('Stand2')]
KISS = rng('BlowKiss', 1, 14, cy)
SWOON = rng('Swoon', 1, 11, cy)
def pp(prefix, n): return [P[f'{prefix}{k}'] for k in range(n)]
from candy_rig import ground as _ground
CRAWL = [_ground(rotate_whole(P[f'walk{k}'], -90, (128, 92), (128, 92))) for k in range(8)]   # walk cycle turned 90 degrees forward
import candy_rig as _CR
RIDE = [_CR.rotate_whole(_CR.pose(thighL=45, shinL=-10 + 4 * k, thighR=92, shinR=-12 + 5 * k, armR=45 - 5 * k,
                                  foreR=75 - 5 * k, no_back_leg=True), -12 - 3 * k, (128, 92), (128, 92)) for k in range(2)]
RIDE_HIP = (128, 92)          # where her hips are in RIDE frames
CY_GROUPS = {
    'IdleSway': STAND, 'Walk': pp('walk', 8), 'Run': pp('run', 8), 'Jump': [P['jump0'], P['jump1']],
    'Fall': [P['fall0'], P['fall1']], 'Land': [KISS[7]], 'Roll': KISS, 'Hurt': SWOON,
    'TooCloseToEdge': SWOON[:6], 'Bounce': [P['jump0'], P['jump1']], 'Victory': KISS,
    'Failure': SWOON, 'Swimming': pp('swim', 4), 'Pickup': KISS[6:9], 'HoldWalk': pp('carrywalk', 8),
    'Throw': [P['throw']], 'ScratchHead': STAND, 'Duck': [KISS[i] for i in (0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 13)], 'Crawling': CRAWL,
    'EnterCrawlSpace': CRAWL[:2], 'HangOnVerticalRope': [P['hang0']], 'TurnOnVerticalRope': [P['hang1']],
    'ClimbUpSingleVerticalRope': [P['hang0'], P['hang1']], 'RideSteelKeg': pp('run', 8),
    'SwingOnRope': [P['hang0'], P['hang1']], 'DiddyTakesLead': KISS, 'DonkeyTakesLead': [P['jump0']],
    'RideAnimalBuddy': RIDE, 'Unknown1Pose': RIDE, 'HangOntoWinky': RIDE,
    'HangOntoStabbingEnguarde': RIDE, 'AngledInMinecart': [RIDE[0]], 'IdleInMinecart': [RIDE[0]],
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

def small_box(a, scale, x0, y0):
    """downscale with a fixed origin (x0, y0) so frames stay registered"""
    ys, xs = np.nonzero(a)
    x1, y1 = xs.max() + 1, ys.max() + 1
    w, h = int((x1 - x0) * scale) + 1, int((y1 - y0) * scale) + 1
    out = np.zeros_like(a)
    for y in range(h):
        for x in range(w):
            sx0, sx1 = x0 + int(x / scale), x0 + int((x + 1) / scale)
            sy0, sy1 = y0 + int(y / scale), y0 + int((y + 1) / scale)
            blk = a[sy0:max(sy1, sy0 + 1), sx0:max(sx1, sx0 + 1)]
            if blk.size == 0: continue
            v = blk[blk.shape[0] // 2, blk.shape[1] // 2]
            if v == 0 and np.count_nonzero(blk) * 2 > blk.size:
                nz = blk[blk > 0]; v = np.bincount(nz).argmax()
            out[y0 + y, x0 + x] = v
    return out

FAMILY = {}          # id(raster) -> reference raster of its animation family
def family(frames, ref):
    for f in frames: FAMILY[id(f)] = ref
family(W + CR_SWIM, W[0]); family(WP + SW + RA, WP[0]); family(list(ST.values()), ST[20]); family(F, F[0])
family(STAND + KISS + SWOON + list(P.values()) + CRAWL + RIDE, STAND[0])

def build(groups, prefix, ref_feet_y, ref_feet_x, cart_lift=0, scale=None, hip_groups=None):
    out = {}
    cache = {}
    def sc(r):
        if scale is None: return r
        if id(r) in PRESCALED: return PRESCALED[id(r)]
        if id(r) not in cache: cache[id(r)] = small_box(r, scale, 64, 24)
        return cache[id(r)]
    for grp, srcs in groups.items():
        idxs = g1.get(prefix + grp)
        if not idxs:
            continue
        for n, i in enumerate(idxs):
            s0 = srcs[phase(len(idxs), len(srcs), n)]; s = sc(s0)
            o = raster(R1, NAMES[i][1])
            if hip_groups and grp in hip_groups:
                ob, ox = seat_point(o)
                k = scale or 1
                ax, ay = ANCHOR.get(id(s0), RIDE_HIP)
                hx = 64 + (ax - 64) * k if scale else ax
                hy = 24 + (ay - 24) * k if scale else ay
                a = shift(s, int(round(ox + 5 - hx)), int(round(ob - 2 - hy)))
            elif grp in TOP_ALIGN:
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
                r = sc(FAMILY.get(id(s0), s0))     # one offset per animation family: no bobbing or sliding
                a = shift(s, int(round(ref_feet_x - feet_x(r))), int(ref_feet_y - feet_row(r)))
            out[i] = a
    return out

dk_y = statistics.median(feet_row(raster(R1, NAMES[i][1])) for i in g1['DonkeyKong_Walk'] + g1['DonkeyKong_Idle'])
dk_x = statistics.median(feet_x(raster(R1, NAMES[i][1])) for i in g1['DonkeyKong_Walk'] + g1['DonkeyKong_Idle'])
dd_y = statistics.median(feet_row(raster(R1, NAMES[i][1])) for i in g1['Diddy_Walk'] + g1['Diddy_IdleSway'])
dd_x = statistics.median(feet_x(raster(R1, NAMES[i][1])) for i in g1['Diddy_Walk'] + g1['Diddy_IdleSway'])
ASSIGN_C = build(CR_GROUPS, 'DonkeyKong_', dk_y, dk_x, 6,
                 hip_groups={'RideAnimalBuddy', 'HangOntoWinky', 'HangOntoStabbingEnguarde'})
import candy_eyes
PRESCALED = dict(zip(map(id, KISS), candy_eyes.fix([small_box(k, 2 / 3, 64, 24) for k in KISS])))   # open eyes
ASSIGN_Y = build(CY_GROUPS, 'Diddy_', dd_y, dd_x, 10, scale=2 / 3,
                 hip_groups={'RideAnimalBuddy', 'Unknown1Pose', 'HangOntoWinky', 'HangOntoStabbingEnguarde'})   # Candy at 2/3 size

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
    # scale every frame inside one shared box so the body keeps its place (no bounce)
    stack = np.zeros_like(srcs[0])
    for s in srcs: stack |= (s > 0)
    ys, xs = np.nonzero(stack); y0, x0 = ys.min(), xs.min()
    sm = []
    for s in srcs:
        c = np.zeros_like(s); c[y0:, x0:] = s[y0:, x0:]
        big = np.zeros_like(s); big[:] = 0
        sm.append(small_box(s, scale, x0, y0))
    ref = small_box(srcs[0], scale, x0, y0)
    dx, dy = int(round(rx - feet_x(ref))), int(ry - feet_row(ref))
    for n, p in enumerate(poses):
        out[p] = shift(sm[phase(len(poses), len(sm), n)], dx, dy)
    return out

def poses_of(idxs): return [0x8C + 4 * i for i in idxs]
dk_map_walk = poses_of(g1['MapDonkeyKong_Walk']); dk_map_vict = poses_of(g1['MapDonkeyKong_Victory'])
dd_map_walk = [0x1054 + 4 * k for k in range(8)]; dd_map_vict = [0x1074 + 4 * k for k in range(11)]
dk_t = [0x12AC + 4 * k for k in range(9)]; dd_t = [0x12D0 + 4 * k for k in range(8)]
MAP_C, MAP_Y = {}, {}
CS, YS = 0.5, 0.34
MAP_C.update(map_set(dk_map_walk, W[::2], dk_map_walk, CS))
MAP_C.update(map_set(dk_map_vict, RA + CLEAN, dk_map_walk, CS))
MAP_C.update(map_set(dk_t, W[::2], dk_t, CS))
MAP_Y.update(map_set(dd_map_walk, pp('walk', 8), dd_map_walk, YS))
MAP_Y.update(map_set(dd_map_vict, KISS[::2], dd_map_walk, YS))
MAP_Y.update(map_set(dd_t, pp('walk', 8), dd_t, YS))
