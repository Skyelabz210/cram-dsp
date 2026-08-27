"""NODE-DRE — the glyph machine (integer-exact, evidence-preserving).

This module is the legitimate version of what the researcher's concept
illustrations depict: glyph extraction from a codex page, an internal-
structure code per glyph "searched circularly outward from the center",
matching that code across a page (and across pages), a luminance ordering
over the extracted glyphs, and a test of whether that ordering traces a
coherent path. Every value emitted is an exact integer function of the
input integers (A1); nothing is inpainted, synthesized, or enhanced.

What it does NOT do, by design: it does not generate imagery, does not
assert meanings for glyphs, and does not manufacture a "luminous path" —
it measures whether one exists and reports the number either way.

Pipeline (all exact):
  int_luma        (77R + 150G + 29B) >> 8, weights sum to 256
  otsu_threshold  integer Otsu via cross-multiplied variance comparison
  ink components  run-based two-pass connected components (8-connectivity),
                  union-find with path compression — exact partition
  glyph cells     component bounding boxes filtered by area window after
                  k-step 8-neighbour binary dilation (shift-OR only)
  ring signature  ink-fraction (milli) per concentric ring about the ink
                  centroid; radii by exact integer sqrt (table search),
                  scale-normalized to a fixed ring count
  matching        L1 distance between ring signatures — exact integers,
                  ranked; ties reported as ties
  luminance order cells ranked by interior median luma (exact lower median)
  path test       L1 tour length of the luminance ordering vs seeded
                  Fisher-Yates permutations (deterministic LCG) — the rank
                  is the exact permutation p-value numerator

A2/A8: no residue decode paths are involved here; no Sqr usage. The one
sanctioned emission seam for milli-unit reporting is floor division by a
stated denominator, printed as milli.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Luma + threshold
# ---------------------------------------------------------------------------

LUMA_R, LUMA_G, LUMA_B = 77, 150, 29  # sum = 256


def int_luma(rgb):
    """Exact integer luma: (77R + 150G + 29B) >> 8. uint8 in, int64 out."""
    r = rgb[:, :, 0].astype(np.int64)
    g = rgb[:, :, 1].astype(np.int64)
    b = rgb[:, :, 2].astype(np.int64)
    return (LUMA_R * r + LUMA_G * g + LUMA_B * b) >> 8


def exact_median(values) -> int:
    """Lower median by full sort — exact integer."""
    s = np.sort(np.asarray(values), axis=None)
    return int(s[(s.size - 1) // 2])


def otsu_threshold(luma) -> int:
    """Integer Otsu. Between-class separation w0*w1*(mu0-mu1)^2 is compared
    across thresholds as the exact rational (w1*sum0 - w0*sum1)^2 / (w0*w1)
    using cross-multiplication — no division is ever evaluated.

    Returns the first luma value of the bright class, so the dark class is
    exactly `luma < threshold` (the convention `ink_mask` uses)."""
    hist = np.bincount(np.asarray(luma).ravel().astype(np.int64), minlength=256)
    total = int(hist.sum())
    total_sum = int((np.arange(256, dtype=np.int64) * hist).sum())
    best_t, best_num, best_den = 0, -1, 1
    w0 = 0
    sum0 = 0
    for t in range(256):
        w0 += int(hist[t])
        if w0 == 0:
            continue
        w1 = total - w0
        if w1 == 0:
            break
        sum0 += t * int(hist[t])
        diff = w1 * sum0 - w0 * (total_sum - sum0)
        num = diff * diff
        den = w0 * w1
        if num * best_den > best_num * den:
            best_t, best_num, best_den = t, num, den
    return best_t + 1


def ink_mask(luma, threshold: int):
    """Boolean ink mask: strictly darker than the threshold."""
    return np.asarray(luma) < threshold


# ---------------------------------------------------------------------------
# Connected components (run-based, 8-connectivity, exact)
# ---------------------------------------------------------------------------

def _find(parent, x: int) -> int:
    root = x
    while parent[root] != root:
        root = parent[root]
    while parent[x] != root:
        parent[x], x = root, parent[x]
    return root


def _union(parent, a: int, b: int):
    ra, rb = _find(parent, a), _find(parent, b)
    if ra != rb:
        if ra < rb:
            parent[rb] = ra
        else:
            parent[ra] = rb


def label_components(mask, conn: int = 8):
    """Two-pass run-based labeling. Returns (labels int64 array, n_components).
    Background label 0; components labeled 1..n in first-pixel order.
    conn=8 (default) or conn=4; hole counting uses 4-conn background as the
    topological dual of 8-conn foreground."""
    mask = np.asarray(mask)
    h, w = mask.shape
    labels = np.zeros((h, w), dtype=np.int64)
    parent = [0]
    prev_runs = []  # (c0, c1_exclusive, provisional_label)
    for r in range(h):
        row = mask[r].astype(np.int8)
        d = np.diff(np.concatenate((np.zeros(1, np.int8), row,
                                    np.zeros(1, np.int8))))
        starts = np.flatnonzero(d == 1)
        ends = np.flatnonzero(d == -1)
        runs = []
        for s, e in zip(starts.tolist(), ends.tolist()):
            lab = 0
            for ps, pe, pl in prev_runs:
                # 8-conn: [s-1, e] meets [ps, pe-1]; 4-conn: strict overlap
                if (s <= pe and ps <= e) if conn == 8 else (s < pe and ps < e):
                    if lab == 0:
                        lab = _find(parent, pl)
                    else:
                        _union(parent, lab, pl)
            if lab == 0:
                lab = len(parent)
                parent.append(lab)
            runs.append((s, e, lab))
            labels[r, s:e] = lab
        prev_runs = runs
    # resolve to canonical roots, then compact to 1..n
    roots = np.asarray([_find(parent, i) for i in range(len(parent))],
                       dtype=np.int64)
    remap = np.zeros(len(parent), dtype=np.int64)
    nxt = 0
    seen = {}
    for i in range(1, len(parent)):
        rt = int(roots[i])
        if rt not in seen:
            nxt += 1
            seen[rt] = nxt
        remap[i] = seen[rt]
    return remap[labels], nxt


def dilate(mask, steps: int = 1):
    """8-neighbour binary dilation by shift-OR, `steps` times. Exact."""
    m = np.asarray(mask).copy()
    for _ in range(steps):
        n = m.copy()
        n[1:, :] |= m[:-1, :]
        n[:-1, :] |= m[1:, :]
        n[:, 1:] |= m[:, :-1]
        n[:, :-1] |= m[:, 1:]
        n[1:, 1:] |= m[:-1, :-1]
        n[1:, :-1] |= m[:-1, 1:]
        n[:-1, 1:] |= m[1:, :-1]
        n[:-1, :-1] |= m[1:, 1:]
        m = n
    return m


def component_boxes(labels, n: int):
    """Per-component (y0, y1, x0, x1, area) — half-open boxes, exact."""
    ys, xs = np.nonzero(labels)
    ls = labels[ys, xs]
    y0 = np.full(n + 1, np.iinfo(np.int64).max, dtype=np.int64)
    y1 = np.zeros(n + 1, dtype=np.int64)
    x0 = np.full(n + 1, np.iinfo(np.int64).max, dtype=np.int64)
    x1 = np.zeros(n + 1, dtype=np.int64)
    np.minimum.at(y0, ls, ys)
    np.maximum.at(y1, ls, ys)
    np.minimum.at(x0, ls, xs)
    np.maximum.at(x1, ls, xs)
    area = np.bincount(ls, minlength=n + 1)
    out = []
    for i in range(1, n + 1):
        out.append((int(y0[i]), int(y1[i]) + 1, int(x0[i]), int(x1[i]) + 1,
                    int(area[i])))
    return out


def glyph_cells(mask, min_area: int, max_area: int, merge_steps: int = 2):
    """Candidate glyph cells: dilate the ink mask so strokes of one glyph
    join, label, keep boxes whose *dilated* area sits in the window.
    Returns boxes in reading order (top-to-bottom, then left-to-right by
    box top-left, row-banded by box height median)."""
    merged = dilate(mask, merge_steps)
    labels, n = label_components(merged)
    boxes = [b for b in component_boxes(labels, n)
             if min_area <= b[4] <= max_area]
    boxes.sort(key=lambda b: (b[0], b[2]))
    return boxes


# ---------------------------------------------------------------------------
# Ring signature — the glyph's internal code, read circularly outward
# ---------------------------------------------------------------------------

def ink_centroid(cell_mask):
    """Integer centroid of ink pixels (floor division). Falls back to the
    geometric center of the cell when the cell holds no ink."""
    ys, xs = np.nonzero(np.asarray(cell_mask))
    if ys.size == 0:
        h, w = np.asarray(cell_mask).shape
        return (h - 1) // 2, (w - 1) // 2
    return int(ys.sum()) // ys.size, int(xs.sum()) // xs.size


def _isqrt_grid(d2):
    """Exact integer sqrt of a squared-distance grid via table search.
    Table bound from math.isqrt — exact integer square root, not float."""
    from math import isqrt
    m = int(d2.max())
    squares = np.arange(isqrt(m) + 2, dtype=np.int64) ** 2
    return np.searchsorted(squares, d2, side="right").astype(np.int64) - 1


def _scaled_offsets(cell_mask):
    """Offsets from the EXACT rational ink centroid, scaled by the ink
    count n so no division ever happens: dy_s = n·y − ΣY, dx_s = n·x − ΣX.
    Mirroring negates dx_s exactly and rot90 permutes (dy_s, dx_s) exactly,
    so codes built on these offsets are exactly invariant — a floor-divided
    centroid is not (the rounding breaks the symmetry on asymmetric ink)."""
    cm = np.asarray(cell_mask)
    h, w = cm.shape
    ys, xs = np.nonzero(cm)
    if ys.size == 0:
        n, sy, sx = 1, (h - 1) // 2, (w - 1) // 2
    else:
        n, sy, sx = ys.size, int(ys.sum()), int(xs.sum())
    yy = n * np.arange(h, dtype=np.int64)[:, None] - sy
    xx = n * np.arange(w, dtype=np.int64)[None, :] - sx
    return yy, xx


def ring_signature(cell_mask, n_rings: int = 12):
    """Milli ink-fraction per concentric ring around the ink centroid,
    scale-normalized to n_rings. Exact integers; empty rings report -1 so
    absence is distinguishable from zero ink."""
    cm = np.asarray(cell_mask)
    h, w = cm.shape
    yy, xx = _scaled_offsets(cm)
    d2 = yy * yy + xx * xx
    r = _isqrt_grid(d2)
    rmax = int(r.max())
    if rmax == 0:
        ring = np.zeros((h, w), dtype=np.int64)
    else:
        ring = np.minimum(r * n_rings // (rmax + 1), n_rings - 1)
    sig = np.zeros(n_rings, dtype=np.int64)
    for k in range(n_rings):
        sel = ring == k
        npx = int(sel.sum())
        if npx == 0:
            sig[k] = -1
        else:
            sig[k] = (1000 * int(cm[sel].sum())) // npx
    return sig


def signature_distance(a, b) -> int:
    """Exact L1 distance between ring signatures (same length)."""
    return int(np.abs(np.asarray(a) - np.asarray(b)).sum())


def match_signatures(query_sig, candidates):
    """Rank candidate signatures by exact L1 distance to the query.
    Returns list of (distance, index) sorted ascending, ties kept in
    index order — ties are reported, never broken arbitrarily."""
    scored = [(signature_distance(query_sig, c), i)
              for i, c in enumerate(candidates)]
    scored.sort()
    return scored


# ---------------------------------------------------------------------------
# Luminance ordering + path test
# ---------------------------------------------------------------------------

def cell_brightness(luma, box) -> int:
    """Exact lower-median luma of the cell interior."""
    y0, y1, x0, x1, _ = box
    return exact_median(np.asarray(luma)[y0:y1, x0:x1])


def luminance_order(luma, boxes):
    """Boxes ranked brightest-first by interior median; exact ties broken
    by reading order (the tie itself is preserved in the returned keys)."""
    keyed = [(-cell_brightness(luma, b), i) for i, b in enumerate(boxes)]
    keyed.sort()
    return [(int(-k), i) for k, i in keyed]


def box_center(box):
    y0, y1, x0, x1, _ = box
    return ((y0 + y1) // 2, (x0 + x1) // 2)


def path_length_l1(points) -> int:
    """Exact L1 tour length over the point sequence."""
    total = 0
    for (y0, x0), (y1, x1) in zip(points, points[1:]):
        total += abs(y1 - y0) + abs(x1 - x0)
    return total


class LCG:
    """Deterministic 64-bit LCG (Knuth MMIX constants) — seeded integer
    stream for permutation nulls. Not for cryptography; for reproducible
    null distributions only."""
    A = 6364136223846793005
    C = 1442695040888963407
    M = 1 << 64

    def __init__(self, seed: int):
        self.state = seed % self.M

    def next_below(self, n: int) -> int:
        self.state = (self.A * self.state + self.C) % self.M
        return (self.state >> 16) % n


def permutation_path_test(points, ordered_indices, n_perm: int = 999,
                          seed: int = 20260827):
    """Is the luminance-ordered tour shorter than chance?

    Exact integers end to end: observed L1 tour length under the given
    ordering vs n_perm seeded Fisher-Yates shuffles of the same points.
    Returns (observed, n_shorter_or_equal, n_perm) where the p-value is
    (n_shorter_or_equal + 1) / (n_perm + 1) — emitted as the exact pair,
    never as a float."""
    seq = [points[i] for i in ordered_indices]
    observed = path_length_l1(seq)
    rng = LCG(seed)
    idx = list(range(len(points)))
    n_le = 0
    for _ in range(n_perm):
        for j in range(len(idx) - 1, 0, -1):
            k = rng.next_below(j + 1)
            idx[j], idx[k] = idx[k], idx[j]
        if path_length_l1([points[i] for i in idx]) <= observed:
            n_le += 1
    return observed, n_le, n_perm


# ---------------------------------------------------------------------------
# Page-level driver
# ---------------------------------------------------------------------------

def analyze_page(rgb, min_area: int = 120, max_area: int = 12000,
                 merge_steps: int = 2, n_rings: int = 12):
    """Full machine pass over one RGB page. Returns a dict of exact values:
    threshold, ink coverage (milli), glyph boxes, per-glyph ring signatures
    and brightness, luminance ordering, and the permutation path test."""
    y = int_luma(rgb)
    thr = otsu_threshold(y)
    mask = ink_mask(y, thr)
    total = mask.size
    boxes = glyph_cells(mask, min_area, max_area, merge_steps)
    sigs = []
    for b in boxes:
        y0, y1, x0, x1, _ = b
        sigs.append(ring_signature(mask[y0:y1, x0:x1], n_rings))
    order = luminance_order(y, boxes)
    centers = [box_center(b) for b in boxes]
    if len(boxes) >= 3:
        path = permutation_path_test(centers, [i for _, i in order])
    else:
        path = (0, 0, 0)
    return {
        "threshold": thr,
        "ink_milli": (1000 * int(mask.sum())) // total,
        "boxes": boxes,
        "signatures": sigs,
        "luminance_order": order,
        "centers": centers,
        "path_test": path,
    }


# ---------------------------------------------------------------------------
# Discovery primitives — topology, tonal bands, bulk code matching
# ---------------------------------------------------------------------------

def count_holes(comp_mask) -> int:
    """Exact hole count of one component: 4-connected background components
    that do not touch the crop border (topological dual of 8-conn ink).
    A hollow dot (drawn ring / stitching hole) has >= 1; a solid dot has 0."""
    cm = np.asarray(comp_mask)
    inv = ~cm
    labels, n = label_components(inv, conn=4)
    if n == 0:
        return 0
    border = np.concatenate((labels[0, :], labels[-1, :],
                             labels[:, 0], labels[:, -1]))
    border_ids = set(int(v) for v in np.unique(border) if v != 0)
    return n - len(border_ids)


def dot_shape_milli(box):
    """(aspect, fill) in milli for a component box: aspect = 1000*h//w,
    fill = 1000*area//(h*w). Roundish solid dots fill high; rings lower."""
    y0, y1, x0, x1, area = box
    h, w = y1 - y0, x1 - x0
    return (1000 * h) // w, (1000 * area) // (h * w)


def classify_dots(mask, min_area: int = 20, max_area: int = 900,
                  aspect_lo: int = 500, aspect_hi: int = 2000):
    """Codex dot census on the RAW ink mask (no dilation): small, roughly
    round components split by exact topology into hollow (>=1 hole) and
    solid (0 holes). Returns (hollow_boxes, solid_boxes)."""
    labels, n = label_components(np.asarray(mask))
    hollow, solid = [], []
    for i, b in enumerate(component_boxes(labels, n), start=1):
        y0, y1, x0, x1, area = b
        if not (min_area <= area <= max_area):
            continue
        aspect, _fill = dot_shape_milli(b)
        if not (aspect_lo <= aspect <= aspect_hi):
            continue
        comp = labels[y0:y1, x0:x1] == i
        # pad by 1 so the outside is a single border-touching background comp
        comp = np.pad(comp, 1)
        if count_holes(comp) >= 1:
            hollow.append(b)
        else:
            solid.append(b)
    return hollow, solid


def luma_bands(luma, n_bands: int = 5):
    """Exact quantile band label per pixel (0 = darkest ... n_bands-1 =
    brightest): thresholds at exact order statistics of the page's own luma.
    The honest version of the illustrations' 'underlying structure layers'."""
    y = np.asarray(luma)
    s = np.sort(y, axis=None)
    cuts = [int(s[(i * s.size) // n_bands]) for i in range(1, n_bands)]
    band = np.zeros(y.shape, dtype=np.int64)
    for c in cuts:
        band += (y >= c).astype(np.int64)
    return band


def l1_matrix(A, B):
    """Exact all-pairs L1 distance between signature stacks A (n,k), B (m,k).
    Small enough inputs only — callers chunk."""
    A64 = np.asarray(A, dtype=np.int64)
    B64 = np.asarray(B, dtype=np.int64)
    return np.abs(A64[:, None, :] - B64[None, :, :]).sum(axis=2)


# ---------------------------------------------------------------------------
# Cross-generation localization — edge-orientation matching (exact)
#
# Lesson learned the hard way: median-centred luma SAD is NOT discriminative
# across scan generations (different colour grades make blank pages win as
# low-contrast fits — it produced a false negative on the researcher's p69
# column). Ink STRUCTURE survives re-photography; brightness does not. So
# the production localizer matches quantized gradient orientations, not
# intensities.
# ---------------------------------------------------------------------------

def orientation_planes(luma, mag_threshold: int = 18):
    """8 binary orientation planes from integer central-difference gradients.
    Octant binning uses only sign tests and |gx| vs |gy| comparisons — no
    trigonometry, no float. A pixel votes in exactly one plane when its
    L1 gradient magnitude reaches mag_threshold."""
    y = np.asarray(luma, dtype=np.int64)
    gx = np.zeros_like(y)
    gy = np.zeros_like(y)
    gx[:, 1:-1] = y[:, 2:] - y[:, :-2]
    gy[1:-1, :] = y[2:, :] - y[:-2, :]
    strong = (np.abs(gx) + np.abs(gy)) >= mag_threshold
    ax, ay = np.abs(gx), np.abs(gy)
    b = ((ay > ax).astype(np.int64) * 4
         + ((gx < 0) ^ (gy < 0)).astype(np.int64) * 2
         + (np.minimum(ax, ay) * 2 > np.maximum(ax, ay)).astype(np.int64))
    return np.stack([(strong & (b == k)).astype(np.int64) for k in range(8)])


def pool_planes(planes, block: int = 8):
    """Exact block-sum pooling of orientation planes (counts per cell)."""
    p = np.asarray(planes)
    c, h, w = p.shape
    hb, wb = (h // block) * block, (w // block) * block
    return p[:, :hb, :wb].reshape(
        c, hb // block, block, wb // block, block).sum(axis=(2, 4))


def cooccurrence_map(page_planes, tpl_planes):
    """Exact co-occurrence score at every offset: sum over planes of the
    dot product between the template and the aligned page window. int64
    einsum over a strided view — no float anywhere."""
    from numpy.lib.stride_tricks import sliding_window_view
    P = np.asarray(page_planes, dtype=np.int64)
    T = np.asarray(tpl_planes, dtype=np.int64)
    c, th, tw = T.shape
    if P.shape[1] < th or P.shape[2] < tw:
        return np.zeros((0, 0), dtype=np.int64)
    wins = sliding_window_view(P, (th, tw), axis=(1, 2))
    return np.einsum("cijhw,chw->ij", wins, T)


MIRROR_PLANE_PERM = (2, 3, 0, 1, 6, 7, 4, 5)  # gx -> -gx toggles the XOR bit


def mirror_planes(planes):
    """Orientation planes of the horizontally mirrored image: spatial flip
    plus the exact bin permutation induced by gx -> -gx."""
    p = np.asarray(planes)
    return p[list(MIRROR_PLANE_PERM)][:, :, ::-1]


def locate(page_luma, tpl_luma, block: int = 8, mag_threshold: int = 18):
    """Best placement of the template inside the page by pooled orientation
    co-occurrence. Returns (score, x, y, mirrored) with x/y in full-res
    pixels (top-left corner, quantized to the pooling block)."""
    pp = pool_planes(orientation_planes(page_luma, mag_threshold), block)
    tp = pool_planes(orientation_planes(tpl_luma, mag_threshold), block)
    best = (-1, 0, 0, 0)
    for mir in (0, 1):
        tq = mirror_planes(tp) if mir else tp
        sc = cooccurrence_map(pp, tq)
        if sc.size == 0:
            continue
        j = np.unravel_index(np.argmax(sc), sc.shape)
        cand = (int(sc[j]), int(j[1]) * block, int(j[0]) * block, mir)
        if cand[0] > best[0]:
            best = cand
    return best


# ---------------------------------------------------------------------------
# White-gradient machinery — the illustrations' actual pipeline, exact
# ---------------------------------------------------------------------------

def order_stat(luma, milli: int) -> int:
    """Exact order statistic: the luma value at rank milli/1000."""
    s = np.sort(np.asarray(luma), axis=None)
    idx = (milli * (s.size - 1)) // 1000
    return int(s[idx])


def highlight_freeze(luma, lo_milli: int = 500, hi_milli: int = 970):
    """Exact integer contrast freeze ('highlights & contrast frozen'):
    values at/below the lo order statistic -> 0, at/above the hi order
    statistic -> 255, linear integer scaling between. Every output value
    is floor((v-lo)*255/(hi-lo)) — a stated exact function of the input."""
    y = np.asarray(luma, dtype=np.int64)
    lo = order_stat(y, lo_milli)
    hi = order_stat(y, hi_milli)
    if hi <= lo:
        hi = lo + 1
    out = (y - lo) * 255 // (hi - lo)
    return np.clip(out, 0, 255), lo, hi


def white_nodes(luma, top_milli: int = 965, min_area: int = 12,
                max_area: int = 4000):
    """Bright-structure nodes: pixels at/above the top_milli order statistic,
    connected components, area-filtered. Returns (threshold, node list),
    each node (cy, cx, area, peak, median) — brightest-first by median,
    ties by peak then reading order. The honest 'white fiber/pigment'
    detector: an exact partition of the page's own brightest pixels."""
    y = np.asarray(luma, dtype=np.int64)
    thr = order_stat(y, top_milli)
    mask = y >= thr
    labels, n = label_components(mask)
    nodes = []
    boxes = component_boxes(labels, n)
    for i, b in enumerate(boxes, start=1):
        y0, y1, x0, x1, area = b
        if not (min_area <= area <= max_area):
            continue
        sel = labels[y0:y1, x0:x1] == i
        vals = y[y0:y1, x0:x1][sel]
        nodes.append(((y0 + y1) // 2, (x0 + x1) // 2, area,
                      int(vals.max()), exact_median(vals)))
    nodes.sort(key=lambda t: (-t[4], -t[3], t[0], t[1]))
    return thr, nodes


PIG_SUBSTRATE, PIG_BLACK, PIG_RED, PIG_BLUE = 0, 1, 2, 3


def pigment_classes(rgb, red_margin: int = 24, blue_margin: int = 12):
    """Exact pigment partition of an RGB scan — 4 classes by stated integer
    rules, no color science, no enhancement:

      RED   (frames, red numerals):  R - max(G,B) >= red_margin
      BLUE  (Maya blue/green washes): min(G,B) - R >= blue_margin
      BLACK (carbon ink): luma below the page's integer-Otsu threshold and
            not already red/blue
      SUBSTRATE: everything else

    Chroma rules are checked before the ink rule so dark reds stay red.
    Returns (class map int64, otsu threshold)."""
    a = np.asarray(rgb).astype(np.int64)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    y = int_luma(rgb)
    thr = otsu_threshold(y)
    red = (r - np.maximum(g, b)) >= red_margin
    blue = (np.minimum(g, b) - r) >= blue_margin
    black = (y < thr) & ~red & ~blue
    out = np.zeros(y.shape, dtype=np.int64)
    out[black] = PIG_BLACK
    out[red] = PIG_RED
    out[blue] = PIG_BLUE
    return out, thr


def pigment_fractions_milli(classes):
    """Exact per-class milli fractions of a pigment class map."""
    c = np.asarray(classes)
    total = c.size
    return [(1000 * int((c == k).sum())) // total for k in range(4)]


def octant_index(dy, dx):
    """Axis-centred angular octant (0..7) from integer offsets — the bins
    are centred on the axes and diagonals (boundaries near ±22.5°, rational
    slope 5/12), decided purely by |dx|, |dy| comparisons plus sign bits.
    Because the rule is symmetric in the absolute values, mirroring and
    right-angle rotation act as exact bin permutations with no boundary
    ambiguity: rot90 ⇒ o → (o+6) mod 8; mirror (x→−x) ⇒ o → (4−o) mod 8.
    Order: 0 E, 1 SE, 2 S, 3 SW, 4 W, 5 NW, 6 N, 7 NE (y down)."""
    dy = np.asarray(dy)
    dx = np.asarray(dx)
    ax, ay = np.abs(dx), np.abs(dy)
    horiz = ay * 12 <= ax * 5
    vert = ax * 12 <= ay * 5
    o = np.where(horiz, np.where(dx >= 0, 0, 4),
        np.where(vert, np.where(dy >= 0, 2, 6),
        np.where(dy >= 0, np.where(dx >= 0, 1, 3),
                 np.where(dx >= 0, 7, 5))))
    return o.astype(np.int64)


def sector_signature(cell_mask, n_rings: int = 6, n_sectors: int = 8):
    """Ring × angular-sector ink fractions (milli) about the ink centroid —
    the finer glyph code (the ring code is angularly blind and chains
    generic marks; this one separates forms). n_sectors must be 8 (octant
    geometry). Returns an (n_rings*8,) int64 vector; empty bins -1."""
    cm = np.asarray(cell_mask)
    h, w = cm.shape
    yy, xx = _scaled_offsets(cm)
    r = _isqrt_grid(yy * yy + xx * xx)
    rmax = int(r.max())
    ring = (np.minimum(r * n_rings // (rmax + 1), n_rings - 1)
            if rmax else np.zeros((h, w), dtype=np.int64))
    sect = octant_index(np.broadcast_to(yy, (h, w)),
                        np.broadcast_to(xx, (h, w)))
    sig = np.zeros(n_rings * 8, dtype=np.int64)
    flat = ring * 8 + sect
    npx = np.bincount(flat.ravel(), minlength=n_rings * 8)
    ink = np.bincount(flat.ravel()[cm.ravel()], minlength=n_rings * 8)
    for k in range(n_rings * 8):
        sig[k] = -1 if npx[k] == 0 else (1000 * int(ink[k])) // int(npx[k])
    return sig


def dihedral_variants(sig, n_rings: int = 6):
    """The 8 dihedral re-indexings of a sector signature (4 rotations × 2
    reflections), each an exact sector permutation. Returns (8, len) array."""
    s = np.asarray(sig).reshape(n_rings, 8)
    out = []
    for refl in (False, True):
        base = s[:, [(4 - k) % 8 for k in range(8)]] if refl else s
        for rot in range(4):
            out.append(np.roll(base, 2 * rot, axis=1).reshape(-1))
    return np.stack(out)


def dihedral_min_distance(a, b, n_rings: int = 6) -> int:
    """Exact min-L1 between sector signatures over the 8 dihedral poses of
    b — form matching invariant to 90° rotation and mirroring."""
    va = np.asarray(a, dtype=np.int64)
    return int(min(int(np.abs(va - v).sum())
                   for v in dihedral_variants(b, n_rings)))


def local_bright_field(luma, ink=None, block: int = 16):
    """Exact local brightness excess: luma minus the block-median SUBSTRATE
    (median of the block's non-ink pixels — in text-dense blocks a plain
    median is the ink level and would make all substrate read 'bright';
    a block with no substrate pixels borrows the page substrate median).
    Positive values = brighter than the local substrate — the field where
    white TRAILS live, independent of page lighting and text density."""
    y = np.asarray(luma, dtype=np.int64)
    if ink is None:
        ink = ink_mask(y, otsu_threshold(y))
    sub = ~np.asarray(ink)
    page_sub = exact_median(y[sub]) if bool(sub.any()) else exact_median(y)
    H, W = y.shape
    gh, gw = max(H // block, 1), max(W // block, 1)
    med = np.zeros((gh, gw), dtype=np.int64)
    for bi in range(gh):
        ys = bi * block
        ye = H if bi == gh - 1 else ys + block
        for bj in range(gw):
            xs = bj * block
            xe = W if bj == gw - 1 else xs + block
            vals = y[ys:ye, xs:xe][sub[ys:ye, xs:xe]]
            med[bi, bj] = exact_median(vals) if vals.size else page_sub
    bg = np.repeat(np.repeat(med, block, axis=0), block, axis=1)[:H, :W]
    if bg.shape[0] < H:
        bg = np.vstack([bg, np.repeat(bg[-1:, :], H - bg.shape[0], axis=0)])
    if bg.shape[1] < W:
        bg = np.hstack([bg, np.repeat(bg[:, -1:], W - bg.shape[1], axis=1)])
    return y - bg


def filament_components(luma, ink=None, base_diff: int = 14,
                        core_diff: int = 28, min_len: int = 60,
                        max_thickness: int = 24, merge_steps: int = 2):
    """White TRAILS — continuous locally-bright filaments, not blobs and
    not global-quantile slivers.

    The trail field is the local brightness excess (`local_bright_field`):
    a pixel is trail-band if it sits >= base_diff luma steps above its own
    block's median substrate (ink pixels excluded when an ink mask is
    given). Band pixels are bridged across `merge_steps` px gaps
    (shift-OR dilation) and labeled; a component is a TRAIL if it is long
    (>= min_len), thin relative to its length (mean thickness <=
    max_thickness AND length >= 3x thickness). It ASCENDS ('gradient to
    white') if any of its pixels reach core_diff above local substrate.

    Returns (labels, trails, band_mask) with each trail as
    (box, component_id, core_px, length, thickness)."""
    y = np.asarray(luma)
    diff = local_bright_field(y, ink=ink)
    band = diff >= base_diff
    if ink is not None:
        band &= ~np.asarray(ink)
    merged = dilate(band, merge_steps)
    labels, n = label_components(merged)
    trails = []
    for i, b in enumerate(component_boxes(labels, n), start=1):
        y0, y1, x0, x1, a = b
        length = max(y1 - y0, x1 - x0)
        if length < min_len:
            continue
        thickness = a // max(length, 1)
        if thickness > max_thickness or length < 3 * thickness:
            continue
        comp = labels[y0:y1, x0:x1] == i
        core = int((diff[y0:y1, x0:x1][comp] >= core_diff).sum())
        trails.append((b, i, core, length, thickness))
    return labels, trails, band


def trail_polyline(labels, comp_id: int, box, step: int = 6):
    """Ordered centreline of a filament: bin the component's pixels along
    its long axis in `step`-pixel slabs and take the exact integer centroid
    of each slab. Returns the polyline as (y, x) points in page coordinates,
    ordered along the axis — the trail's arc."""
    y0, y1, x0, x1, _ = box
    comp = np.asarray(labels)[y0:y1, x0:x1] == comp_id
    ys, xs = np.nonzero(comp)
    pts = []
    if (y1 - y0) >= (x1 - x0):
        for s in range(0, y1 - y0, step):
            sel = (ys >= s) & (ys < s + step)
            m = int(sel.sum())
            if m == 0:
                continue
            pts.append((y0 + int(ys[sel].sum()) // m,
                        x0 + int(xs[sel].sum()) // m))
    else:
        for s in range(0, x1 - x0, step):
            sel = (xs >= s) & (xs < s + step)
            m = int(sel.sum())
            if m == 0:
                continue
            pts.append((y0 + int(ys[sel].sum()) // m,
                        x0 + int(xs[sel].sum()) // m))
    return pts


def trail_glyph_sequence(polyline, boxes, reach: int = 40):
    """The glyphs a trail passes through, in trail order: for each glyph
    box, the earliest polyline point within L1 `reach` of the box centre;
    glyphs are returned ordered by that arc index (the illustrated 'key
    glyphs sequenced by the path'). Exact integers only."""
    seq = []
    for bi, b in enumerate(boxes):
        cy, cx = box_center(b)
        for ai, (py, px) in enumerate(polyline):
            if abs(py - cy) + abs(px - cx) <= reach:
                seq.append((ai, bi))
                break
    seq.sort()
    return [bi for _, bi in seq]


def white_path(nodes, limit: int = 12, min_sep: int = 0):
    """Brightest-first sequence over white nodes (the illustrated '1 =
    brightest' path). min_sep (L1 pixels) spatially de-duplicates: a node
    within min_sep of an already-chosen station is skipped, so the sequence
    walks distinct bright structures instead of crowding one bright patch.
    Greedy and exact — a stated rule, not a tuning knob. Returns the chosen
    centers in brightness order plus the exact L1 tour length."""
    seq = []
    for cy, cx, _, _, _ in nodes:
        if len(seq) >= limit:
            break
        if any(abs(cy - py) + abs(cx - px) < min_sep for py, px in seq):
            continue
        seq.append((cy, cx))
    return seq, path_length_l1(seq)
