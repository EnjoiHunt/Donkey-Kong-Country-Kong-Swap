"""Decoder for the Donkey Kong Country sprite-frame format (DKC1/2/3).

Frame layout (all bytes):
  0 n2   number of 16x16 blocks
  1 n1a  number of 8x8 tiles, group A (row 0)
  2 idxa char index where group A starts (= 2*n2)
  3 n1b  number of 8x8 tiles, group B
  4 idxb char index where group B starts
  5 d1n  chars in first DMA (to char 0)
  6 d2s  second DMA dest char (0x10) or 0 if none
  7 d2n  chars in second DMA
  16x16 block i uses chars 2i, 2i+1, 2i+16, 2i+17.
  then (n2+n1a+n1b) x,y byte pairs, then (d1n+d2n)*32 bytes of 4bpp tiles.
"""
from PIL import Image


def hirom(addr):
    return addr & 0x3FFFFF


def decode_tile(b):
    px = []
    for y in range(8):
        p0, p1, p2, p3 = b[y*2], b[y*2+1], b[16+y*2], b[16+y*2+1]
        row = []
        for x in range(8):
            s = 7 - x
            row.append(((p0 >> s) & 1) | (((p1 >> s) & 1) << 1) |
                       (((p2 >> s) & 1) << 2) | (((p3 >> s) & 1) << 3))
        px.append(row)
    return px


def parse(rom, off):
    h = rom[off:off+8]
    n2, n1a, idxa, n1b, idxb, d1n, d2s, d2n = h
    d1s = 0
    npos = n2 + n1a + n1b
    pos = [(rom[off+8+i*2], rom[off+9+i*2]) for i in range(npos)]
    data = off + 8 + npos*2
    size = 8 + npos*2 + (d1n + d2n) * 32
    return dict(n2=n2, n1a=n1a, idxa=idxa, idxb=idxb, n1b=n1b, d1s=d1s, d1n=d1n,
                d2s=d2s, d2n=d2n, pos=pos, data=data, size=size)


def plausible(rom, off):
    if off + 8 > len(rom):
        return False
    n2, n1a, idxa, n1b, idxb, d1n, d2s, d2n = rom[off:off+8]
    if n2 + n1a + n1b == 0 or n2 + n1a + n1b > 64 or (n1a and idxa != 2*n2):
        return False
    if d2s not in (0x10, 0) or (d2s == 0 and d2n) or d1n > 0x40 or d2n > 0x20:
        return False
    return d1n + d2n == n2*4 + n1a + n1b


def render(rom, off, pal, scale=1):
    f = parse(rom, off)
    chars = {}
    p = f["data"]
    for i in range(f["d1n"]):
        chars[f["d1s"] + i] = rom[p:p+32]; p += 32
    for i in range(f["d2n"]):
        chars[f["d2s"] + i] = rom[p:p+32]; p += 32
    W = 256
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    px = img.load()

    def put(ch, ox, oy):
        if ch not in chars:
            return
        t = decode_tile(chars[ch])
        for y in range(8):
            for x in range(8):
                c = t[y][x]
                if c and 0 <= ox+x < W and 0 <= oy+y < W:
                    px[ox+x, oy+y] = pal[c] + (255,)

    k = 0
    for i in range(f["n2"]):
        x, y = f["pos"][k]; k += 1
        b = (i // 8) * 32 + (i % 8) * 2   # 16-char-wide virtual sheet
        put(b, x, y); put(b+1, x+8, y); put(b+16, x, y+8); put(b+17, x+8, y+8)
    for j in range(f["n1a"]):
        x, y = f["pos"][k]; k += 1
        put(f["idxa"] + j, x, y)
    for j in range(f["n1b"]):
        x, y = f["pos"][k]; k += 1
        put(f["idxb"] + j, x, y)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    if scale > 1:
        img = img.resize((img.width*scale, img.height*scale), Image.NEAREST)
    return img


def raster(rom, off, size=256):
    """Uncropped index raster in the frame's own coordinate space (origin 0x80,0x80 at centre)."""
    import numpy as np
    f = parse(rom, off)
    chars = {}
    p = f["data"]
    for i in range(f["d1n"]):
        chars[i] = rom[p:p+32]; p += 32
    for i in range(f["d2n"]):
        chars[f["d2s"] + i] = rom[p:p+32]; p += 32
    img = np.zeros((size, size), dtype=np.uint8)
    def put(ch, ox, oy):
        if ch not in chars: return
        t = decode_tile(chars[ch])
        for y in range(8):
            for x in range(8):
                if t[y][x] and 0 <= ox+x < size and 0 <= oy+y < size:
                    img[oy+y, ox+x] = t[y][x]
    k = 0
    for i in range(f["n2"]):
        x, y = f["pos"][k]; k += 1
        b = (i // 8) * 32 + (i % 8) * 2
        put(b, x, y); put(b+1, x+8, y); put(b+16, x, y+8); put(b+17, x+8, y+8)
    for j in range(f["n1a"]):
        x, y = f["pos"][k]; k += 1
        put(f["idxa"] + j, x, y)
    for j in range(f["n1b"]):
        x, y = f["pos"][k]; k += 1
        put(f["idxb"] + j, x, y)
    return img
