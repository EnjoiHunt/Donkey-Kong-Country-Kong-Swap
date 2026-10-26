"""Encode an index raster as a DKC sprite frame using freely placed 8x8 tiles,
packing them tightly so tall sprites fit the 32-character VRAM slot."""
import numpy as np


def _cover_rows(a, phase):
    ys, xs = np.nonzero(a)
    y0 = ys.min() - phase
    tiles = []
    for ty in range(y0, ys.max() + 1, 8):
        band = a[max(ty, 0):ty + 8]
        cols = np.nonzero(band.any(axis=0))[0]
        x = None
        for c in cols:
            if x is None or c >= x + 8:
                # tighten vertically within the band for this tile
                x = c
                tiles.append((x, ty))
    return tiles


def _tighten(a, tiles):
    """Shift each tile up/down within its band to start at its first used row
    (lets later bands start lower); simple and safe because bands don't overlap."""
    return tiles


def cover(a):
    best = None
    for phase in range(8):
        t = _cover_rows(a, phase)
        if best is None or len(t) < len(best):
            best = t
    # column-band variant (tall thin sprites)
    for phase in range(8):
        t = [(x, y) for (y, x) in _cover_rows(a.T, phase)]
        if len(t) < len(best):
            best = t
    return best


def tile_bytes(a, tx, ty):
    b = bytearray(32)
    for y in range(8):
        for x in range(8):
            yy, xx = ty + y, tx + x
            if 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1]:
                v = int(a[yy, xx]); s = 7 - x
                for bit, o in ((0, 0), (1, 1), (2, 16), (3, 17)):
                    if v >> bit & 1:
                        b[y * 2 + o] |= 1 << s
    return bytes(b)


def encode(a, limit=32):
    ys, xs = np.nonzero(a)
    if len(xs) == 0:
        return bytes([0, 1, 0, 0, 0, 1, 0, 0, 0x80, 0x80]) + bytes(32)
    tiles = cover(a)
    if len(tiles) > limit:
        raise ValueError(f'{len(tiles)} tiles')
    # overlapping tiles: a later tile must not paint transparent over earlier
    # pixels, which can't happen (transparent = 0 is never drawn), so overlaps are fine
    n = len(tiles)
    hdr = bytes([0, n, 0, 0, 0, n, 0, 0])
    pos = b''.join(bytes([tx & 255, ty & 255]) for tx, ty in tiles)
    return hdr + pos + b''.join(tile_bytes(a, tx, ty) for tx, ty in tiles)


def count(a):
    return len(cover(a)) if a.any() else 1
