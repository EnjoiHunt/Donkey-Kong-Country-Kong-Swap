"""DK animation -> Funky frames (5.0)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import funky as F
import ccmap as CM

S, D = F.STAND_S, F.DYN_S
FK_GROUPS = {
    'Idle': S + F.TALK_S[:2] + S, 'Walk': F.WALK, 'Run': F.SURF, 'HoldWalk': F.WALK, 'HoldIdle': [S[0]],
    'Jump': F.AIR[:6], 'Bounce': F.AIR[6:], 'Land': [S[0]], 'Turn': [S[0]],
    'GroundSlap': F.TALK_S, 'BeatChest': F.NOD_S + F.TALK_S, 'SitDown': [S[0]], 'Hurt': F.HURT, 'Failure': F.FAIL,
    'Pickup': [S[0]], 'Unknown4Pose': [S[0]], 'ThrowPose': D[:6],
    'EnterCrawlSpace': [S[0]], 'Crawling': F.WALK, 'TooCloseToEdge': D[::2],
    'Unknown2Pose': [S[0]], 'Unknown3Pose': [S[0]], 'Unknown1_Pose': [S[0]],
    'Roll': F.SURF, 'Swimming': F.SWIM, 'Duck': [S[0]], 'UnusedVictory': F.NOD_S,
    'SwingOnRope': [D[0]], 'HangOnVerticalRope': [D[0]], 'TurnOnVerticalRope': [D[0]],
    'ClimbUpSingleVerticalRope': D[:4], 'DonkeyTakesLead': F.TALK_S, 'DiddyTakesLead': F.TALK_S,
    'Victory': F.NOD_S + F.TALK_S, 'HeyWatchThis': F.TALK_S[:3], 'PrankDiddy': F.TALK_S, 'FingerBitten': F.HURT,
    'RideAnimalBuddy': [D[2], D[3]], 'HangOntoWinky': [D[0]], 'HangOntoStabbingEnguarde': [D[0]],
    'RideSteelKeg': F.SURF, 'AngledInMinecart': [D[2]],
}
ALL = [a for v in FK_GROUPS.values() for a in v]
CM.family(F.STAND_S + F.TALK_S + F.NOD_S + F.WALK + F.HURT + F.FAIL, F.STAND_S[0])
CM.family(F.SURF, F.SURF[0])
CM.family(F.DYN_S + F.SWIM, F.DYN_S[0])
ASSIGN_F = CM.build(FK_GROUPS, 'DonkeyKong_', CM.dk_y, CM.dk_x, 6,
                    hip_groups={'RideAnimalBuddy', 'HangOntoWinky', 'HangOntoStabbingEnguarde'})

MAP_F = {}
MAP_F.update(CM.map_set(CM.dk_map_walk, F.WALK[::2], CM.dk_map_walk, 0.5))
MAP_F.update(CM.map_set(CM.dk_map_vict, F.NOD_S + F.TALK_S, CM.dk_map_walk, 0.5))
MAP_F.update(CM.map_set(CM.dk_t, F.WALK[::2], CM.dk_t, 0.5))
