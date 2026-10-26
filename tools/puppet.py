"""Cut-out puppet for building new sprite poses from an existing indexed raster.

A part is a boolean mask over the source raster plus a pivot.  A pose places each
part with a rotation about its pivot (forward = towards +x, in degrees) and an
offset.  Parts are drawn in order, so later parts cover earlier ones.
"""
import math
import numpy as np


def rot_part(src, mask, pivot, ang, dst_pivot, out):
    """Draw src[mask] rotated by ang degrees (positive = foot swings towards +x
    for a part hanging below its pivot) so that pivot lands on dst_pivot."""
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    px, py = pivot
    # forward transform of the part's bounding box -> destination bbox
    cx = [xs.min() - px, xs.max() + 1 - px]
    cy = [ys.min() - py, ys.max() + 1 - py]
    pts = [(x * ca + y * sa, -x * sa + y * ca) for x in cx for y in cy]
    dx0 = int(math.floor(min(p[0] for p in pts))) - 1
    dx1 = int(math.ceil(max(p[0] for p in pts))) + 1
    dy0 = int(math.floor(min(p[1] for p in pts))) - 1
    dy1 = int(math.ceil(max(p[1] for p in pts))) + 1
    qx, qy = dst_pivot
    H, W = out.shape
    for dy in range(dy0, dy1 + 1):
        for dx in range(dx0, dx1 + 1):
            # inverse rotation
            sx = dx * ca - dy * sa + px
            sy = dx * sa + dy * ca + py
            ix, iy = int(math.floor(sx + 0.5)), int(math.floor(sy + 0.5))
            if 0 <= iy < src.shape[0] and 0 <= ix < src.shape[1] and mask[iy, ix] and src[iy, ix]:
                ox, oy = qx + dx, qy + dy
                if 0 <= ox < W and 0 <= oy < H:
                    out[oy, ox] = src[iy, ix]


def place(src, mask, dxy, out):
    ys, xs = np.nonzero(mask & (src > 0))
    H, W = out.shape
    for y, x in zip(ys, xs):
        ox, oy = x + dxy[0], y + dxy[1]
        if 0 <= ox < W and 0 <= oy < H:
            out[oy, ox] = src[y, x]


def limb(src, out, thigh, shin, hip, knee, a_thigh, a_shin, hip_dst):
    """Two-segment limb: thigh rotates about hip, shin follows with its own
    absolute angle about the knee (angles are absolute, not relative)."""
    rot_part(src, thigh, hip, a_thigh, hip_dst, out)
    a = math.radians(a_thigh)
    kx, ky = knee[0] - hip[0], knee[1] - hip[1]
    nkx = kx * math.cos(a) + ky * math.sin(a)
    nky = -kx * math.sin(a) + ky * math.cos(a)
    kd = (int(round(hip_dst[0] + nkx)), int(round(hip_dst[1] + nky)))
    rot_part(src, shin, knee, a_shin, kd, out)
    return kd


def outline_fix(a, outline_idx):
    """Fill single-pixel holes inside a part with neighbours (cheap cleanup
    after rotation)."""
    b = a.copy()
    H, W = a.shape
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if a[y, x] == 0:
                n = [a[y - 1, x], a[y + 1, x], a[y, x - 1], a[y, x + 1]]
                nz = [v for v in n if v]
                if len(nz) >= 3:
                    b[y, x] = max(set(nz), key=nz.count)
    return b
