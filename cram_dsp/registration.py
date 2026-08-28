"""Exact geometric registration — can this icon be laid onto that feature?

Built for the icon->character correspondence experiment. The question is not
"do these look alike" but "can this icon's contour, at a natural scale and
orientation, be registered onto a specific region of the character". That
demands exact geometry, so nothing here is approximate and nothing is float.

Rotation without float: a Pythagorean triple (a, b, c) with a^2 + b^2 = c^2
gives an EXACT rational rotation, cos = a/c and sin = b/c. The map is
    x' = (a*x - b*y) / c ,  y' = (b*x + a*y) / c
evaluated with integer arithmetic and sampled nearest-neighbour, so a
rotated mask is an exact function of the input mask. Fourteen triples plus
sign flips and quarter turns cover the circle in roughly 2-8 degree steps.

Uniform scale is an exact rational p/q, likewise nearest-neighbour.

Every metric below is an integer or an integer milli-ratio:
  squared Euclidean distance transform (squared distances ARE integers)
  chamfer, hausdorff, boundary overlap, mask IoU
  skeleton agreement (Zhang-Suen thinning, integer)
  topology: components, holes, endpoints, branch points
"""

import numpy as np

# (a, b, c) with a^2 + b^2 = c^2; angle = atan2(b, a), listed by angle.
TRIPLES = [
    (1, 0, 1),        # 0 degrees
    (84, 13, 85),     # ~8.80
    (60, 11, 61),     # ~10.39
    (40, 9, 41),      # ~12.68
    (63, 16, 65),     # ~14.25
    (24, 7, 25),      # ~16.26
    (12, 5, 13),      # ~22.62
    (77, 36, 85),     # ~25.06
    (80, 39, 89),     # ~25.99
    (15, 8, 17),      # ~28.07
    (56, 33, 65),     # ~30.51
    (45, 28, 53),     # ~31.89
    (4, 3, 5),        # ~36.87
    (55, 48, 73),     # ~41.11
    (72, 65, 97),     # ~42.08
    (21, 20, 29),     # ~43.60
]

BIG = np.int64(1) << 40


def rdiv(n, d):
    """Round-half-away-from-zero integer division. Exact, no float."""
    if d < 0:
        n, d = -n, -d
    return (n + d // 2) // d if n >= 0 else -((-n + d // 2) // d)


def rotations(max_index: int = len(TRIPLES), quarter_turns=(0,),
              signs=(1, -1)):
    """Exact rotation set as (a, b, c) triples, including sign flips and
    optional quarter turns. Quarter turns compose exactly: (a,b) -> (-b,a)."""
    out = []
    for t in range(min(max_index, len(TRIPLES))):
        a, b, c = TRIPLES[t]
        for s in signs:
            aa, bb = a, s * b
            if b == 0 and s == -1:
                continue
            for q in quarter_turns:
                ca, cb = aa, bb
                for _ in range(q % 4):
                    ca, cb = -cb, ca
                out.append((ca, cb, c))
    seen, uniq = set(), []
    for r in out:
        if r not in seen:
            seen.add(r)
            uniq.append(r)
    return uniq


def transform_mask(mask, rot, num: int = 1, den: int = 1, mirror: int = 0,
                   out_shape=None):
    """Rotate + uniformly scale a boolean mask by exact rational maps,
    sampled nearest-neighbour. `rot` is (a, b, c); scale is num/den;
    `mirror` reflects x before rotating. Returns the transformed mask."""
    a, b, c = rot
    m = np.asarray(mask)
    h, w = m.shape
    # forward-map the four corners to size the output exactly
    cy_in, cx_in = (h - 1) // 2, (w - 1) // 2
    corners = [(0 - cy_in, 0 - cx_in), (0 - cy_in, w - 1 - cx_in),
               (h - 1 - cy_in, 0 - cx_in), (h - 1 - cy_in, w - 1 - cx_in)]
    fy, fx = [], []
    for dy, dx in corners:
        sx = -dx if mirror else dx
        fy.append(rdiv(num * (b * sx + a * dy), den * c))
        fx.append(rdiv(num * (a * sx - b * dy), den * c))
    oh = max(fy) - min(fy) + 1
    ow = max(fx) - min(fx) + 1
    if out_shape is not None:
        oh, ow = max(oh, out_shape[0]), max(ow, out_shape[1])
    cy_out, cx_out = (oh - 1) // 2, (ow - 1) // 2

    oy = np.arange(oh, dtype=np.int64)[:, None] - cy_out
    ox = np.arange(ow, dtype=np.int64)[None, :] - cx_out
    # inverse map: scale by den/num, rotate by -theta, un-mirror
    dy = (a * oy - b * ox) * den
    dx = (b * oy + a * ox) * den
    dd = c * num
    half = dd // 2
    sy = np.where(dy < 0, -((-dy + half) // dd), (dy + half) // dd)
    sx = np.where(dx < 0, -((-dx + half) // dd), (dx + half) // dd)
    if mirror:
        sx = -sx
    iy = sy + cy_in
    ix = sx + cx_in
    ok = (iy >= 0) & (iy < h) & (ix >= 0) & (ix < w)
    out = np.zeros((oh, ow), dtype=bool)
    out[ok] = m[iy[ok], ix[ok]]
    return out


def erode4(mask):
    """4-connected erosion, exact."""
    m = np.asarray(mask)
    e = m.copy()
    e[1:, :] &= m[:-1, :]
    e[:-1, :] &= m[1:, :]
    e[:, 1:] &= m[:, :-1]
    e[:, :-1] &= m[:, 1:]
    return e


def contour(mask):
    """Boundary pixels: in the mask, not in its 4-erosion."""
    m = np.asarray(mask)
    return m & ~erode4(m)


def contour_points(mask):
    ys, xs = np.nonzero(contour(mask))
    return np.stack([ys, xs], axis=1).astype(np.int64)


def sq_edt(mask, pad: int = 0):
    """EXACT squared Euclidean distance transform to the mask's set pixels.
    Squared distances are integers, so no float ever appears. Computed by
    vectorised running minimum over the source points."""
    m = np.asarray(mask)
    h, w = m.shape
    ys, xs = np.nonzero(m)
    out = np.full((h, w), BIG, dtype=np.int64)
    if ys.size == 0:
        return out
    yy = np.arange(h, dtype=np.int64)[:, None]
    xx = np.arange(w, dtype=np.int64)[None, :]
    for i in range(ys.size):
        dy = yy - ys[i]
        dx = xx - xs[i]
        np.minimum(out, dy * dy + dx * dx, out=out)
    return out


def isqrt_arr(a):
    """Exact integer square root of a non-negative integer array."""
    from math import isqrt
    flat = np.asarray(a).ravel()
    cap = int(flat[flat < BIG].max()) if np.any(flat < BIG) else 0
    table = np.arange(isqrt(cap) + 2, dtype=np.int64) ** 2
    r = np.searchsorted(table, np.minimum(flat, cap), side="right") - 1
    return r.reshape(np.asarray(a).shape)


# ---------------------------------------------------------------- metrics

def chamfer_milli(pts, edt, dy: int = 0, dx: int = 0):
    """Mean distance (milli px) from transformed points to the nearest
    target-contour pixel, using the exact squared EDT of the target."""
    h, w = edt.shape
    py = pts[:, 0] + dy
    px = pts[:, 1] + dx
    ok = (py >= 0) & (py < h) & (px >= 0) & (px < w)
    if not np.any(ok):
        return BIG, 0
    d2 = edt[py[ok], px[ok]]
    d = isqrt_arr(d2)
    inside = int(ok.sum())
    return (1000 * int(d.sum())) // inside, inside


def hausdorff(pts, edt, dy: int = 0, dx: int = 0):
    """Directed Hausdorff distance (px, exact integer sqrt of the max
    squared distance) from the points to the target contour."""
    h, w = edt.shape
    py = pts[:, 0] + dy
    px = pts[:, 1] + dx
    ok = (py >= 0) & (py < h) & (px >= 0) & (px < w)
    if not np.any(ok):
        return int(BIG)
    return int(isqrt_arr(np.asarray([[int(edt[py[ok], px[ok]].max())]]))[0][0])


def boundary_overlap_milli(pts, edt, tol: int = 1, dy: int = 0, dx: int = 0):
    """Fraction (milli) of transformed contour points lying within `tol`
    pixels of the target contour."""
    h, w = edt.shape
    py = pts[:, 0] + dy
    px = pts[:, 1] + dx
    ok = (py >= 0) & (py < h) & (px >= 0) & (px < w)
    if not np.any(ok):
        return 0
    near = int((edt[py[ok], px[ok]] <= tol * tol).sum())
    return (1000 * near) // int(ok.sum())


def iou_milli(a, b):
    """Exact mask IoU in milli over the overlap of two equal-shaped masks."""
    A, B = np.asarray(a), np.asarray(b)
    inter = int((A & B).sum())
    union = int((A | B).sum())
    return 0 if union == 0 else (1000 * inter) // union


# ------------------------------------------------------------- morphology

_ZS_A = None


def thin(mask, max_iter: int = 64):
    """Zhang-Suen thinning to a 1-px skeleton. Integer/boolean only."""
    m = np.asarray(mask).astype(np.uint8).copy()
    def nb(p):
        return [np.roll(np.roll(p, s[0], 0), s[1], 1) for s in
                ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1),
                 (-1, -1))]
    for _ in range(max_iter):
        changed = False
        for step in (0, 1):
            P = nb(m)
            B = sum(int_p.astype(np.int64) for int_p in P)
            A = np.zeros(m.shape, dtype=np.int64)
            for i in range(8):
                A += ((P[i] == 0) & (P[(i + 1) % 8] == 1)).astype(np.int64)
            if step == 0:
                cond = (P[0] * P[2] * P[4] == 0) & (P[2] * P[4] * P[6] == 0)
            else:
                cond = (P[0] * P[2] * P[6] == 0) & (P[0] * P[4] * P[6] == 0)
            rm = (m == 1) & (B >= 2) & (B <= 6) & (A == 1) & cond
            if np.any(rm):
                m[rm] = 0
                changed = True
        if not changed:
            break
    return m.astype(bool)


def skeleton_topology(mask):
    """(endpoints, branch points) of a thinned mask via crossing numbers."""
    s = thin(mask).astype(np.uint8)
    P = [np.roll(np.roll(s, d[0], 0), d[1], 1) for d in
         ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1),
          (-1, -1))]
    cn = np.zeros(s.shape, dtype=np.int64)
    for i in range(8):
        cn += np.abs(P[i].astype(np.int64) - P[(i + 1) % 8].astype(np.int64))
    cn = cn // 2
    on = s == 1
    return int((on & (cn == 1)).sum()), int((on & (cn >= 3)).sum())


def integral(a):
    """Exact 2-D prefix sums with a zero border."""
    return np.pad(np.cumsum(np.cumsum(np.asarray(a, dtype=np.int64), axis=0),
                            axis=1), ((1, 0), (1, 0)))


def window_sums(a, th: int, tw: int):
    """Exact sums over every th x tw window."""
    ii = integral(a)
    return ii[th:, tw:] - ii[:-th, tw:] - ii[th:, :-tw] + ii[:-th, :-tw]


def iou_map(icon_mask, target_mask, pad: int = None):
    """Exact IoU (milli) of the icon placed at every offset over the target.

    Why this and not chamfer-to-EDT: a codex character is a dense line
    drawing, so its contour pixels are everywhere and a one-directional
    chamfer saturates — every small icon sits within a pixel of *some*
    stroke, and random crops score perfectly. Area agreement does not
    saturate: it asks whether the icon's ink and the target's ink in the
    same window are the same set.

    intersection by sparse slice-adds over the icon's ON pixels; the
    target's ink count per window by integral image. All exact integers.
    Returns (iou_milli_map, offset_origin) where offset_origin is the pad
    applied, so offset (i, j) corresponds to placement (i - pad, j - pad).
    """
    ic = np.asarray(icon_mask)
    tg = np.asarray(target_mask)
    ih, iw = ic.shape
    if pad is None:
        pad = max(ih, iw)
    tp = np.pad(tg, pad)
    th, tw = tp.shape
    hs, ws = th - ih + 1, tw - iw + 1
    if hs <= 0 or ws <= 0:
        return np.zeros((0, 0), dtype=np.int64), pad
    ys, xs = np.nonzero(ic)
    area = int(ys.size)
    inter = np.zeros((hs, ws), dtype=np.int64)
    for i in range(area):
        inter += tp[int(ys[i]):int(ys[i]) + hs, int(xs[i]):int(xs[i]) + ws]
    tcount = window_sums(tp, ih, iw)
    union = area + tcount - inter
    return np.where(union > 0, (1000 * inter) // np.maximum(union, 1), 0), pad
