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
    """Exact integer sqrt of a squared-distance grid via table search."""
    m = int(d2.max())
    # squares table 0..r where r*r >= m
    r = 1
    while r * r < m + 1:
        r += 1
    squares = np.arange(r + 1, dtype=np.int64) ** 2
    return np.searchsorted(squares, d2, side="right").astype(np.int64) - 1


def ring_signature(cell_mask, n_rings: int = 12):
    """Milli ink-fraction per concentric ring around the ink centroid,
    scale-normalized to n_rings. Exact integers; empty rings report -1 so
    absence is distinguishable from zero ink."""
    cm = np.asarray(cell_mask)
    h, w = cm.shape
    cy, cx = ink_centroid(cm)
    yy = np.arange(h, dtype=np.int64)[:, None] - cy
    xx = np.arange(w, dtype=np.int64)[None, :] - cx
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
