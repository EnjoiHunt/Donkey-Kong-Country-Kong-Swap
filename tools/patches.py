import zlib, sys

def varint(n):
    out = bytearray()
    while True:
        x = n & 0x7f; n >>= 7
        if n == 0: out.append(0x80 | x); return bytes(out)
        out.append(x); n -= 1

def sv(n):  # signed varint for relative offsets
    return varint((abs(n) << 1) | (1 if n < 0 else 0))

def make_bps(src, dst):
    p = bytearray(b'BPS1') + varint(len(src)) + varint(len(dst)) + varint(0)
    i = 0; srel = 0; trel = 0; lit = bytearray()
    def flush():
        nonlocal lit, p
        if lit:
            p += varint(((len(lit) - 1) << 2) | 1) + lit; lit = bytearray()
    while i < len(dst):
        # 1) same-offset source match
        j = i
        while j < len(dst) and j < len(src) and src[j] == dst[j]: j += 1
        if j - i >= 8:
            flush(); p += varint(((j - i - 1) << 2) | 0); i = j; continue
        # 2) mirrored source (ExHiROM upper halves): source offset i - 0x400000
        so = i - 0x400000
        if so >= 0:
            j = i
            while j < len(dst) and so + (j - i) < len(src) and src[so + j - i] == dst[j]: j += 1
            if j - i >= 16:
                flush(); p += varint(((j - i - 1) << 2) | 2) + sv(so - srel); srel = so + (j - i); i = j; continue
        # 3) run of a repeated byte -> TargetCopy from previous byte
        if i > 0 and dst[i] == dst[i - 1]:
            j = i
            while j < len(dst) and dst[j] == dst[i - 1]: j += 1
            if j - i >= 16:
                flush(); p += varint(((j - i - 1) << 2) | 3) + sv((i - 1) - trel); trel = (i - 1) + (j - i); i = j; continue
        lit.append(dst[i]); i += 1
    flush()
    p += zlib.crc32(src).to_bytes(4, 'little') + zlib.crc32(dst).to_bytes(4, 'little')
    p += zlib.crc32(p).to_bytes(4, 'little')
    return bytes(p)

def apply_bps(src, p):
    assert p[:4] == b'BPS1'; k = 4
    def rv():
        nonlocal k
        d = 0; s = 1
        while True:
            x = p[k]; k += 1; d += (x & 0x7f) * s
            if x & 0x80: return d
            s <<= 7; d += s
    ss, ts, ms = rv(), rv(), rv(); k += ms
    out = bytearray(); end = len(p) - 12; srel = 0; trel = 0
    while k < end:
        d = rv(); n = (d >> 2) + 1; a = d & 3
        if a == 0: out += src[len(out):len(out) + n]
        elif a == 1: out += p[k:k + n]; k += n
        else:
            d2 = rv(); off = (-1 if d2 & 1 else 1) * (d2 >> 1)
            if a == 2:
                srel += off; out += src[srel:srel + n]; srel += n
            else:
                trel += off
                for _ in range(n): out.append(out[trel]); trel += 1
    assert zlib.crc32(bytes(out)) == int.from_bytes(p[-8:-4], 'little')
    return bytes(out)

def make_ips(src, dst):
    out = bytearray(b'PATCH'); i = 0; n = len(dst)
    def get(a, x): return a[x] if x < len(a) else None
    while i < n:
        if get(src, i) == dst[i] and i != n - 1:
            i += 1; continue
        j = i
        while j < n and j - i < 0xFFFF and (get(src, j) != dst[j] or j == n - 1):
            j += 1
        if i == 0x454F46: i -= 1
        out += i.to_bytes(3, 'big') + (j - i).to_bytes(2, 'big') + dst[i:j]
        i = j
    return bytes(out + b'EOF')

def apply_ips(src, p):
    r = bytearray(src); k = 5
    while p[k:k + 3] != b'EOF':
        o = int.from_bytes(p[k:k + 3], 'big'); s = int.from_bytes(p[k + 3:k + 5], 'big'); k += 5
        if s == 0:
            rl = int.from_bytes(p[k:k + 2], 'big'); v = p[k + 2]; k += 3
            if len(r) < o + rl: r += bytes(o + rl - len(r))
            r[o:o + rl] = bytes([v]) * rl
        else:
            if len(r) < o + s: r += bytes(o + s - len(r))
            r[o:o + s] = p[k:k + s]; k += s
    return bytes(r)

if __name__ == '__main__':
    src = open(sys.argv[1], 'rb').read(); dst = open(sys.argv[2], 'rb').read(); base = sys.argv[3]
    b = make_bps(src, dst); open(base + '.bps', 'wb').write(b)
    i = make_ips(src, dst); open(base + '.ips', 'wb').write(i)
    print('bps', len(b), 'ok', apply_bps(src, b) == dst)
    print('ips', len(i), 'ok', apply_ips(src, i) == dst)
