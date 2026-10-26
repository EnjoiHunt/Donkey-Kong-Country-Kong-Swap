import sys, json
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

from dkcsprite import plausible
rom = open(CFG.DKC2_ROM, 'rb').read()
B = 0x390000
r16 = lambda o: rom[o] | rom[o+1] << 8
def frames_of(anim):
    cur = r16(B + anim*4); out = []; seen = set(); unk = None
    for _ in range(200):
        if cur in seen or cur >= 0xfff8: break
        seen.add(cur); op = rom[B+cur]
        if 0 < op < 0x80: out.append(r16(B+cur+1)); cur += 3
        elif op in (0x81, 0x83, 0x84): cur += 3
        elif op == 0x8a: cur += 10
        elif op == 0x8b: cur += 8
        else: unk = op; break
    return out, unk
def gfx_ok(g):
    a, b, c, d = rom[0x3c8000+g:0x3c8004+g]
    return d == 0 and c >= 0xC0 and plausible(rom, (c << 16 | b << 8 | a) & 0x3fffff)
if __name__ == '__main__':
    result = {}
    for who, base in (('diddy', 0), ('dixie', 0xa3)):
        gs = []; stops = {}
        for k in range(0xa3):
            fr, unk = frames_of(base + k)
            stops[unk] = stops.get(unk, 0) + 1
            for g in fr:
                if gfx_ok(g) and g not in gs: gs.append(g)
        result[who] = gs
        print(who, len(gs), 'stop ops', stops)
    both = set(result['diddy']) & set(result['dixie'])
    print('shared', len(both))
    json.dump(result, open(CFG.data('dkc2_kong_gfx.json'), 'w'))
