"""Count the bananas in every DKC1 level (main path + bonus rooms) from the ROM.

Bananas come from two places:
  * banana formations (lines / arcs of single bananas), per level ID
    DATA_B8B41D[entrance] -> level, DATA_B8C0E1[level] -> 4-byte entries,
    each entry's shape (DATA_B8C0DF table) starts with its banana count;
  * banana-bunch sprites (sprite $15, worth 10) in the per-entrance sprite list
    DATA_BD8000[entrance] -> 8-byte entries (type, x, y, spawn script)."""
import re, sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))



def w(R, o): return R[o] | R[o + 1] << 8


def entrances():
    """name -> id, from the disassembly's entrance list (or data/entrances.json)"""
    import config as CFG
    return json.load(open(CFG.data('entrances.json')))   # entrance names from the DKC1 disassembly


def formation_count(R, lvl):
    base = 0x38C0E1
    p = base + w(R, base + lvl * 2)
    shapes = 0x380000 | w(R, 0x38C0DF)
    total = 0
    while True:
        w0 = w(R, p)
        if w0 == 0:
            break
        sh = w0 & 0x3FE
        addr = shapes + w(R, shapes + sh)
        total += R[addr]
        p += 4
    return total


def script_sprite(R, ptr, depth=0):
    """follow a sprite spawn script and return the sprite ID it sets"""
    o = 0x350000 | ptr
    sid = None
    for _ in range(64):
        op = w(R, o)
        if op < 0x8000:
            if op == 0x0D45:
                sid = w(R, o + 2)
            o += 4
            continue
        code = op >> 8
        if code == 0x80:
            break
        if code == 0x82:
            s = script_sprite(R, w(R, o + 2), depth + 1) if depth < 8 else None
            if s is not None:
                sid = s
            o += 4
            continue
        n = {0x81: 1, 0x88: 1, 0x8D: 1, 0x8E: 1, 0x8F: 2, 0x90: 2, 0x91: 1, 0x92: 2, 0x94: 3,
             0x95: 1, 0x96: 1, 0x97: 1}.get(code, 0)
        o += 2 + 2 * n
    return sid


def bunches(R, ent):
    p = 0x3D0000 | w(R, 0x3D8000 + ent * 2)
    n = 0
    for _ in range(400):
        t = w(R, p)
        if t == 0:
            break
        if script_sprite(R, w(R, p + 6)) == 0x15:
            n += 1
        p += 8
    return n


SKIP = ('Exit', 'Checkpoint', 'KongsBananaHoard', 'DKsHouse', 'Warp')


def level_totals(R):
    E = entrances()
    mains = {n[:-5]: i for n, i in E.items() if n.endswith('_Main')}
    mains['ReptileRumble'] = E['ReptileRumble_Main1']
    out = {}
    for lv, main_id in sorted(mains.items(), key=lambda kv: kv[1]):
        ents = [i for n, i in E.items() if n.startswith(lv + '_') and not any(s in n for s in SKIP)]
        lvls = sorted({R[0x38B41D + e] for e in ents})
        sprite_lists = {}
        for e in ents:
            sprite_lists.setdefault(w(R, 0x3D8000 + e * 2), e)
        f = sum(formation_count(R, l) for l in lvls)
        b = sum(bunches(R, e) for e in sprite_lists.values())
        out[lv] = dict(entrance=main_id, levels=lvls, formations=f, bunches=b, total=f + 10 * b,
                       entrances=sorted(ents))
    return out


if __name__ == '__main__':
    R = open(sys.argv[1], 'rb').read()
    for k, v in level_totals(R).items():
        print(f"{k:22s} ent {v['entrance']:#04x} lv {v['levels']} singles {v['formations']:4d} bunches {v['bunches']:2d} total {v['total']}")
