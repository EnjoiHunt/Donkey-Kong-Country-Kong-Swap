"""Build new DKC sprite frames from rasters (8x8 tiles only)."""
import numpy as np
from common import raster
def shifted(rom, off, dx, dy):
    a = raster(rom, off); out = np.zeros_like(a)
    H, W = a.shape
    ys, xs = np.nonzero(a)
    ny, nx = ys + dy, xs + dx
    ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
    out[ny[ok], nx[ok]] = a[ys[ok], xs[ok]]
    return out
def encode(a):
    ys, xs = np.nonzero(a)
    if len(xs) == 0:
        return bytes([0, 1, 0, 0, 0, 1, 0, 0, 0x80, 0x80]) + bytes(32)
    x0, y0 = xs.min(), ys.min()
    tiles = []
    for ty in range(y0, ys.max() + 1, 8):
        for tx in range(x0, xs.max() + 1, 8):
            blk = a[ty:ty + 8, tx:tx + 8]
            if blk.any():
                b = bytearray(32)
                for y in range(blk.shape[0]):
                    for x in range(blk.shape[1]):
                        v = int(blk[y, x]); s = 7 - x
                        for bit, o in ((0, 0), (1, 1), (2, 16), (3, 17)):
                            if v >> bit & 1: b[y * 2 + o] |= 1 << s
                tiles.append((tx, ty, bytes(b)))
    assert len(tiles) <= 32, len(tiles)
    n = len(tiles)
    hdr = bytes([0, n, 0, 0, 0, n, 0, 0])
    pos = b''.join(bytes([tx & 255, ty & 255]) for tx, ty, _ in tiles)
    return hdr + pos + b''.join(t for _, _, t in tiles)
def top_point(a):
    ys, xs = np.nonzero(a)
    t = ys.min(); band = xs[ys <= t + 4]
    return int(t), int(np.median(band))
def seat_point(a):
    ys, xs = np.nonzero(a)
    b = ys.max(); band = xs[ys >= b - 8]
    return int(b), int(band.min())
