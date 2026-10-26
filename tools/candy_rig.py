"""Candy Kong rig cut from her DKC1 'Stand1' frame (frame raster coordinates,
origin 128,128 = between the feet)."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from puppet import rot_part, place, limb, outline_fix

import json
from common import R1, raster
import config as CFG
S = raster(R1, dict(json.load(open(CFG.data('cc_frames.json'))))['CandyKong_Stand1'])
H, W = S.shape
yy, xx = np.mgrid[0:H, 0:W]
PINK = np.isin(S, [2, 3, 4, 5])          # leotard / bow
FUR = np.isin(S, [1, 6, 7, 8, 10, 11, 12, 13, 14])   # outline, fur, skin

# right (hanging) arm: fur/skin at the right edge
ARM_R = (S > 0) & FUR & (xx >= 136) & (yy >= 72) & (yy <= 104)
ARM_R |= (S > 0) & (xx >= 135) & (yy >= 97) & (yy <= 106) & FUR
ARM_R |= (S > 0) & (xx >= 138) & (yy >= 72) & (yy <= 106)
SHOULDER_R = (137, 74)
ELBOW_R = (138, 89)
UPPER_R, FORE_R = ARM_R & (yy < 89), ARM_R & (yy >= 89)

# legs: below the hips, not leotard
LEGS = (S > 0) & (yy >= 89) & ~((yy <= 96) & PINK) & ~ARM_R
LEG_L = LEGS & (xx <= 128)
LEG_R = LEGS & (xx >= 129)
KNEE_Y = 108
THIGH_L, SHIN_L = LEG_L & (yy < KNEE_Y), LEG_L & (yy >= KNEE_Y)
THIGH_R, SHIN_R = LEG_R & (yy < KNEE_Y), LEG_R & (yy >= KNEE_Y)
HIP_L, KNEE_L = (125, 91), (125, KNEE_Y)
HIP_R, KNEE_R = (132, 91), (132, KNEE_Y)

# left arm (hand on hip)
ARM_L = (S > 0) & (xx <= 121) & (yy >= 70) & (yy <= 88)
ARM_L |= (S > 0) & ~PINK & (xx <= 129) & (yy >= 82) & (yy <= 88)
SHOULDER_L = (122, 73)

BODY = (S > 0) & ~LEGS & ~ARM_R            # head, torso, left arm
TORSO_NOARM = BODY & ~ARM_L


def blank():
    return np.zeros_like(S)


def fill_hand_gap(out, dy=0):
    """When the hip arm is removed, paint leotard where the hand covered it."""
    for y in range(82, 89):
        row = [x for x in range(122, 131) if PINK[y, x] or TORSO_NOARM[y, x]]
        for x in range(122, 130):
            if out[y + dy, x] == 0 and S[y, x] and ARM_L[y, x]:
                out[y + dy, x] = 4 if x > 123 else 1


def pose(thighL=0, shinL=0, thighR=0, shinR=0, armR=0, foreR=None, armL=None, foreL=None,
         body_dy=0, body_dx=0, hip_arm=True, front='R', arm_behind=False, no_back_leg=False):
    """Angles in degrees, positive = towards +x (Candy faces +x).
    armL: None keeps the hand on her hip; a number gives her a straight arm
    (a copy of the right arm) at that angle."""
    out = blank()
    hipL = (HIP_L[0] + body_dx, HIP_L[1] + body_dy)
    hipR = (HIP_R[0] + body_dx, HIP_R[1] + body_dy)
    legs = [(THIGH_L, SHIN_L, HIP_L, KNEE_L, thighL, shinL, hipL),
            (THIGH_R, SHIN_R, HIP_R, KNEE_R, thighR, shinR, hipR)]
    if front == 'L':
        legs = legs[::-1]
    # back leg, torso, front leg (no back leg when straddling an animal: it's on the far side)
    if not no_back_leg:
        limb(S, out, *legs[0])
    if armL is not None:
        sh = (SHOULDER_L[0] + body_dx, SHOULDER_L[1] + body_dy)
        fl = armL if foreL is None else foreL
        limb(S, out, UPPER_R, FORE_R, SHOULDER_R, ELBOW_R, armL, fl, sh)
    sh = (SHOULDER_R[0] + body_dx, SHOULDER_R[1] + body_dy)
    if arm_behind:
        limb(S, out, UPPER_R, FORE_R, SHOULDER_R, ELBOW_R, armR, armR if foreR is None else foreR, sh)
    place(S, BODY if (hip_arm and armL is None) else TORSO_NOARM, (body_dx, body_dy), out)
    if not (hip_arm and armL is None):
        fill_hand_gap(out, 0)
    if no_back_leg:
        # straddling: her left leg (the one on the right of the sprite) is on the far side of the animal
        limb(S, out, *legs[0])
    else:
        limb(S, out, *legs[1])
    if not arm_behind:
        limb(S, out, UPPER_R, FORE_R, SHOULDER_R, ELBOW_R, armR, armR if foreR is None else foreR, sh)
    return outline_fix(out, 1)


def rotate_whole(a, ang, pivot=(128, 100), dst=(128, 100)):
    out = np.zeros_like(a)
    rot_part(a, a > 0, pivot, ang, dst, out)
    return outline_fix(out, 1)


def shift(a, dx, dy):
    out = np.zeros_like(a)
    place(a, a > 0, (dx, dy), out)
    return out


def ground(a, y=127):
    ys = np.nonzero(a)[0]
    return shift(a, 0, y - ys.max()) if len(ys) else a
