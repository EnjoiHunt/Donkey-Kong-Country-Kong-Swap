"""All generated Candy poses (name -> raster)."""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import candy_rig as C

def walk(k, n=8, amp=22, arm=12):
    t = 2 * math.pi * k / n; s = math.sin(t)
    tl, tr = amp * s, -amp * s
    sl = tl - 28 * max(0, math.cos(t))
    sr = tr - 28 * max(0, -math.cos(t))
    return C.ground(C.pose(thighL=tl, shinL=sl, thighR=tr, shinR=sr, armR=-arm * s))

def run(k, n=8):
    t = 2 * math.pi * k / n; s = math.sin(t)
    tl, tr = 38 * s, -38 * s
    sl = tl - 50 * max(0, math.cos(t))
    sr = tr - 50 * max(0, -math.cos(t))
    a = C.pose(thighL=tl, shinL=sl, thighR=tr, shinR=sr, armR=-35 * s, foreR=-35 * s + 40)
    return C.ground(C.rotate_whole(a, 8, (128, 120), (128, 120)))

POSES = {}
for k in range(8): POSES[f'walk{k}'] = walk(k)
for k in range(8): POSES[f'run{k}'] = run(k)
# jump: front knee up, arm raised
POSES['jump0'] = C.pose(thighL=-15, shinL=-30, thighR=70, shinR=-20, armR=150, foreR=165, body_dy=-6, arm_behind=True)
POSES['jump1'] = C.pose(thighL=-25, shinL=-10, thighR=55, shinR=-5, armR=160, foreR=172, body_dy=-6, arm_behind=True)
POSES['fall0'] = C.pose(thighL=-20, shinL=-5, thighR=25, shinR=10, armR=125, foreR=150, armL=-125, foreL=-150, arm_behind=True)
POSES['fall1'] = C.pose(thighL=-25, shinL=-10, thighR=30, shinR=15, armR=135, foreR=160, armL=-135, foreL=-160, arm_behind=True)
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
    POSES[f'carrywalk{k}'] = C.ground(C.pose(thighL=tl, shinL=tl - 26 * max(0, math.cos(t)), thighR=tr,
                                             shinR=tr - 26 * max(0, -math.cos(t)), armR=160, foreR=200,
                                             armL=-160, foreL=-200, arm_behind=True))
# crawl: low crouch, reaching arm
for k in range(4):
    s = math.sin(2 * math.pi * k / 4)
    POSES[f'crawl{k}'] = C.ground(C.pose(thighL=-85 + 10 * s, shinL=5, thighR=80 - 10 * s, shinR=-5,
                                         armR=60 + 25 * s, foreR=80 + 20 * s, body_dy=18))
