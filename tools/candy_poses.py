"""All generated Candy poses (name -> raster)."""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import candy_rig as C

def lean(a, ang):
    """tilt the whole figure about her feet (negative = leaning forward, she faces +x)"""
    return C.ground(C.rotate_whole(a, ang, (128, 118), (128, 118)))


def walk(k, n=8):
    """5.3: a hip-swinging walk, one hand on her hip, the other arm swinging"""
    t = 2 * math.pi * k / n; s, c = math.sin(t), math.cos(t)
    th = 22 * s
    tl, sl = th, th - 35 * max(0, c) - 4
    tr, sr = -th, -th - 35 * max(0, -c) - 4
    a = C.pose(thighL=tl, shinL=sl, thighR=tr, shinR=sr, armR=-18 * s + 4, foreR=-18 * s + 20, hip_merge=0.6)
    return C.shift(lean(a, -3), 0, -int(round(1.5 * abs(c))))


# 5.3: run cycle keyed like a side-view sprint: (thigh, shin) for one leg, the other half a cycle later
RUN_LEG = [(25, 5), (15, -10), (0, -15), (-20, -30), (-30, -60), (-10, -105), (35, -55), (42, 0)]


def run(k, n=8):
    tl, sl = RUN_LEG[k % 8]; tr, sr = RUN_LEG[(k + 4) % 8]
    arm = 38 * math.cos(2 * math.pi * k / 8 - 0.6)      # both arms pump, against the legs
    a = C.pose(thighL=tl, shinL=sl, thighR=tr, shinR=sr, armR=-arm + 5, foreR=-arm + 75,
               armL=arm + 5, foreL=arm + 75, hip_merge=0.8)
    bob = 2 if k % 4 in (1, 2) else 0                    # lower while her weight is on a leg
    return C.shift(lean(a, -12), 0, bob - 2)

POSES = {}
for k in range(8): POSES[f'walk{k}'] = walk(k)
for k in range(8): POSES[f'run{k}'] = run(k)
# jump: front knee up, arm raised
# 5.3 jump: front knee driven up, back leg tucked, one arm reaching up; fall: legs reaching down, arms out
POSES['jump0'] = lean(C.pose(thighL=-10, shinL=-55, thighR=65, shinR=-15, armR=155, foreR=170, armL=60, foreL=110,
                             body_dy=-6, arm_behind=True, hip_merge=0.7), -6)
POSES['jump1'] = lean(C.pose(thighL=-5, shinL=-45, thighR=75, shinR=-5, armR=165, foreR=175, armL=70, foreL=120,
                             body_dy=-6, arm_behind=True, hip_merge=0.7), -6)
POSES['fall0'] = C.pose(thighL=-15, shinL=-20, thighR=35, shinR=5, armR=120, foreR=140, armL=-110, foreL=-130,
                        arm_behind=True, hip_merge=0.5)
POSES['fall1'] = C.pose(thighL=-20, shinL=-5, thighR=25, shinR=15, armR=105, foreR=120, armL=-100, foreL=-115,
                        arm_behind=True, hip_merge=0.5)
# crouch / land / duck
POSES['crouch'] = C.ground(C.pose(thighL=-60, shinL=10, thighR=65, shinR=-15, armR=20, body_dy=12))
POSES['duck'] = C.ground(C.pose(thighL=-85, shinL=5, thighR=80, shinR=-5, armR=30, foreR=60, body_dy=18))
# hang (rope): both arms up
POSES['hang0'] = C.pose(thighL=-8, shinL=-4, thighR=10, shinR=4, armR=170, foreR=176, armL=-170, foreL=-176, arm_behind=True)
POSES['hang1'] = C.pose(thighL=10, shinL=4, thighR=-6, shinR=-4, armR=176, foreR=178, armL=-166, foreL=-172, arm_behind=True)
# carry overhead
POSES['carry'] = C.pose(thighL=-6, shinL=-6, thighR=8, shinR=4, armR=160, foreR=200, armL=-160, foreL=-200, arm_behind=True)
POSES['throw'] = C.pose(thighL=-12, shinL=-12, thighR=14, shinR=6, armR=95, foreR=85, body_dx=2)
# seated (ride / cart)
POSES['sit'] = C.ground(C.pose(thighL=86, shinL=5, thighR=80, shinR=0, armR=60, foreR=90, body_dy=14))
# swim: body horizontal, legs kicking
for k in range(4):
    s = math.sin(2 * math.pi * k / 4)
    a = C.pose(thighL=10 * s, shinL=15 * s, thighR=-10 * s, shinR=-15 * s, armR=165 - 25 * s, foreR=170, armL=-165 + 25 * s, foreL=-170, arm_behind=True)
    POSES[f'swim{k}'] = C.rotate_whole(a, -75, (128, 95), (128, 100))

# carrying walk: arms up, walking legs
for k in range(8):
    t = 2 * math.pi * k / 8; s = math.sin(t)
    tl, tr = 20 * s, -20 * s
    POSES[f'carrywalk{k}'] = C.shift(C.ground(C.pose(thighL=tl, shinL=tl - 26 * max(0, math.cos(t)), thighR=tr,
                                             shinR=tr - 26 * max(0, -math.cos(t)), armR=160, foreR=200,
                                             armL=-160, foreL=-200, arm_behind=True, hip_merge=0.6)),
                                     0, -int(round(1.5 * abs(math.cos(t)))))
# crawl: low crouch, reaching arm
for k in range(4):
    s = math.sin(2 * math.pi * k / 4)
    POSES[f'crawl{k}'] = C.ground(C.pose(thighL=-85 + 10 * s, shinL=5, thighR=80 - 10 * s, shinR=-5,
                                         armR=60 + 25 * s, foreR=80 + 20 * s, body_dy=18))
