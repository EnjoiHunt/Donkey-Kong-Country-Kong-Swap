"""Global numbering of every banana (singles in formations + bunch sprites) for
per-banana persistence (4.3)."""
import bananas as B
w = B.w


def shape_cols(R, addr):
    n = R[addr]
    x = (w(R, addr + 1) << 1) & 0x7F
    p66 = w(R, 0x38B7AF - 2 + x); p64 = p66
    y = 2; cols = []
    A = w(R, addr + y); y += 2; c = 1
    while True:
        nc = A & 1; A = (A >> 1) | (c << 15); c = nc
        if A == 0:
            A = w(R, addr + y); y += 2; c = 1; continue
        nc = p64 & 1; p64 = (p64 >> 1) | (c << 15); c = nc
        if c == 0: continue
        cols.append(p64); p64 = p66; n -= 1; c = 0
        if n == 0: break
    return cols


def level_words(R, lvl):
    base = 0x38C0E1; p = base + w(R, base + lvl * 2); shapes = 0x380000 | w(R, 0x38C0DF); out = []
    while w(R, p):
        out += shape_cols(R, shapes + w(R, shapes + (w(R, p) & 0x3FE))); p += 4
    return out


def list_ptr(R, ent): return w(R, 0x3D8000 + ent * 2)


def bunch_entries(R, ptr):
    p = 0x3D0000 | ptr; out = []; i = 0
    for _ in range(400):
        if w(R, p) == 0: break
        if B.script_sprite(R, w(R, p + 6)) == 0x15: out.append(i)
        p += 8; i += 1
    return out, i


def build(R):
    E = B.entrances()
    lv = {k: v for k, v in B.level_totals(R).items() if k not in ('UnusedRoom', 'AnimalTokenTest')}
    order = sorted(lv, key=lambda k: lv[k]['entrance'])
    k = 0
    lid_base = {}      # level id -> (k_start, words, kbase per word)
    for name in order:
        for lid in lv[name]['levels']:
            if lid in lid_base: continue
            words = level_words(R, lid)
            kb = []
            for v in words:
                kb.append(k); k += bin(v).count('1')
            lid_base[lid] = (kb[0] if kb else k, words, kb)
    list_k = {}        # list ptr -> {entry index: k}
    for name in order:
        for e in lv[name]['entrances']:
            ptr = list_ptr(R, e)
            if ptr in list_k: continue
            ents, n = bunch_entries(R, ptr)
            d = {}
            for i in ents: d[i] = k; k += 1
            list_k[ptr] = (d, n)
    levels = []
    for name in order:
        ranges = set(); total = 0
        for lid in lv[name]['levels']:
            s, words, kb = lid_base[lid]; cnt = sum(bin(v).count('1') for v in words)
            if cnt: ranges.add((s, cnt))
        for e in lv[name]['entrances']:
            d, n = list_k[list_ptr(R, e)]
            for i, kk in d.items(): ranges.add((kk, 1))
        ranges = sorted(ranges)
        merged = []
        for s, c in ranges:
            if merged and merged[-1][0] + merged[-1][1] == s: merged[-1][1] += c
            else: merged.append([s, c])
        singles = sum(c for s, c in ranges)
        total = sum(c for s, c in ranges if True)
        bunches = sum(1 for e in set(lv[name]['entrances']) for _ in [0])
        levels.append(dict(name=name, entrance=lv[name]['entrance'], entrances=lv[name]['entrances'], ranges=merged))
    return dict(K=k, lid=lid_base, lists=list_k, levels=levels, order=order)


if __name__ == '__main__':
    import sys
    R = open(sys.argv[1], 'rb').read()
    L = build(R)
    print('K', L['K'], 'level ids', len(L['lid']), 'words', sum(len(v[1]) for v in L['lid'].values()), 'lists', len(L['lists']))
    for lv in L['levels']:
        print(lv['name'], lv['ranges'])
