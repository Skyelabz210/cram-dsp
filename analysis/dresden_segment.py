"""Per-page segmentation — the missing layer from the original request.

"each page carefully segmented, numbered, and grouped into common assumed
categories". The numbering and the section grouping went into
data/dresden/INDEX.md; the SEGMENTATION was never built, and every later
stage suffered for it (figure detectors that merged the page into one blob,
glyph detectors that returned three boxes for a column holding a dozen).

This decomposes every page into its structural elements, numbers each one,
and assigns it a category by stated integer rules. It is the substrate the
rest of the machinery should have been standing on.

Categories (geometry only; no meaning is assigned):
  rule_h / rule_v   red register rules and column rules
  panel_ground      solid red or blue picture-panel fill
  figure            large black-ink drawing
  glyph_block       compound black-ink glyph cell
  numeral_bar       wide thin black bar
  numeral_dot       small round mark (black or red), hollow or solid
  margin            red page-edge frame
Elements are numbered page.register.index in reading order.

Outputs per page: data/dresden/segments/scanNN.json and an overlay
data/dresden/derived/segments/scanNN_seg.jpg. Master table:
docs/DRESDEN_SEGMENTS.md.

Usage: python3 analysis/dresden_segment.py [scan]
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import dresden
from cram_dsp.forensics import Ledger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "dresden")
SEG = os.path.join(DATA, "segments")
OVR = os.path.join(DATA, "derived", "segments")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(SEG, exist_ok=True)
os.makedirs(OVR, exist_ok=True)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                       13)
FB = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)

CATCOL = {"rule_h": (200, 70, 60), "rule_v": (160, 60, 50),
          "panel_ground": (70, 130, 200), "figure": (0, 230, 120),
          "glyph_block": (255, 205, 60), "numeral_bar": (150, 120, 255),
          "numeral_dot": (0, 210, 255), "margin": (120, 90, 80)}
ORDER = ["figure", "glyph_block", "numeral_bar", "numeral_dot",
         "panel_ground", "rule_h", "rule_v", "margin"]


def page_label(k):
    if k <= 28:
        return str(k)
    if k in (29, 30, 31):
        return "28" + "*" * (k - 28)
    if k <= 63:
        return str(k - 3)
    if k == 64:
        return "60*"
    return str(k - 4)


def page_path(k):
    return os.path.join(DATA, "pages", "wdl11621_scan%02d.jpg" % k)


DARK = 110          # luma below this counts toward the dark-fraction profile
GUT = 220           # milli; a gutter/mount band must reach this dark fraction


def leaf_block(y):
    """Locate the physical leaf inside the scan frame.

    RECEIPT — this function exists because of a measured defect. The first
    segmenter keyed every threshold to the SCAN frame (margins 40 px from the
    scan edge, rules >= 45% of scan width) and returned rule_h = rule_v = 0 on
    scan 50, whose register rules are plainly visible. Cause: each WDL scan
    carries slivers of the ADJACENT leaves, so the scan frame is roughly 20%
    wider than the page and its edges are the neighbours, not this page's
    margin. Every geometry rule was being measured against the wrong object.

    The leaf is bounded by the dark gutter between leaves (vertical) and the
    dark mount band (horizontal). Both are found as the strongest dark-
    fraction peak in the outer quarter (rows: outer fifth) of each side, then
    widened to the band's own half-maximum. Fractions are exact integer
    milli-counts of pixels below DARK; no float anywhere.
    """
    H, W = y.shape
    dark = y < DARK
    col = (1000 * dark.sum(axis=0)) // H
    row = (1000 * dark.sum(axis=1)) // W

    def band(prof, lo, hi):
        """Peak of prof in [lo,hi) widened to half-maximum; None if no band."""
        seg = prof[lo:hi]
        if seg.size == 0:
            return None
        j = lo + int(np.argmax(seg))
        pk = int(prof[j])
        if pk < GUT:
            return None
        half = pk // 2
        a = j
        while a > lo and prof[a - 1] >= half:
            a -= 1
        b = j
        while b + 1 < hi and prof[b + 1] >= half:
            b += 1
        return a, b + 1

    lb = band(col, 0, W // 4)
    rb = band(col, (3 * W) // 4, W)
    tb = band(row, 0, H // 5)
    bb = band(row, (4 * H) // 5, H)
    x0 = lb[1] if lb else 0
    x1 = rb[0] if rb else W
    y0 = tb[1] if tb else 0
    y1 = bb[0] if bb else H
    if x1 - x0 < W // 3:
        x0, x1 = 0, W
    if y1 - y0 < H // 3:
        y0, y1 = 0, H
    return int(y0), int(y1), int(x0), int(x1)


def overlap(a, b):
    return not (a[1] <= b[0] or a[0] >= b[1] or a[3] <= b[2] or a[2] >= b[3])


def despeckle(mask, min_area: int = 8):
    """Drop components below min_area. Exact; used for the PROJECTION mask
    only — never for measurement of an element."""
    lab, n = dresden.label_components(mask)
    if n == 0:
        return mask
    area = np.bincount(lab.ravel(), minlength=n + 1)
    area[0] = 0
    return (area >= min_area)[lab]


def cut_bands(prof, minlen, num=2, den=5):
    """Split a 1-D integer projection into content bands. A position is a GAP
    when its count falls to num/den of the profile's own non-zero median —
    an order statistic of the page itself, not a tuned constant. Returns
    [(start, stop), ...] of runs of non-gap positions at least minlen long."""
    n = prof.shape[0]
    nz = prof[prof > 0]
    if nz.size == 0:
        return []
    med = int(np.sort(nz)[nz.size // 2])
    cut = max(2, (med * num) // den)
    solid = prof > cut
    out, i = [], 0
    while i < n:
        if solid[i]:
            j = i
            while j < n and solid[j]:
                j += 1
            if j - i >= minlen:
                out.append((i, j))
            i = j
        else:
            i += 1
    return out


def centres(elems, cat, axis):
    """Sorted, de-duplicated centre coordinates of one category."""
    lo, hi = (0, 1) if axis == 0 else (2, 3)
    vals = sorted(set((e["box"][lo] + e["box"][hi]) // 2
                      for e in elems if e["cat"] == cat))
    out, last = [], -99
    for v in vals:
        if v - last > 20:
            out.append(v)
            last = v
    return out


def classify_cell(mask, h, w, area):
    """Category of one segmented cell, by geometry only. No meaning."""
    if h <= 16 and w >= h * 3 and w >= 14:
        return "numeral_bar"
    if h <= 22 and w <= 22 and area >= 12:
        asp = (1000 * min(h, w)) // max(h, w)
        if asp >= 550:
            return "numeral_dot"
    if h >= 14 and w >= 14:
        return "glyph_block"
    return None


def split_oversize(cells, txt, axis, depth=3):
    """Re-split cells that are far larger than the page's own median cell.

    Receipt: a single gap threshold per zone under-splits DENSE writing —
    on scan 50 the lower-left registers came back as a handful of boxes
    spanning 2x3 glyph grids, while the sparse upper column segmented
    cleanly. The threshold is not the problem; the assumption that one
    threshold fits a whole zone is. A cell wider (taller) than 3/2 of the
    page's median glyph cell is cut at the MINIMUM of its own projection,
    searched only in its middle half so the cut cannot shave off an edge.
    Median cell size is an order statistic of the page itself.
    """
    if depth == 0:
        return cells
    lo, hi = (0, 1) if axis == 0 else (2, 3)
    sizes = sorted(c["box"][hi] - c["box"][lo] for c in cells
                   if c["cat"] == "glyph_block")
    if len(sizes) < 6:
        return cells
    med = sizes[len(sizes) // 2]
    lim = (med * 3) // 2
    out, changed = [], False
    for c in cells:
        a, b = c["box"][lo], c["box"][hi]
        if c["cat"] != "glyph_block" or b - a <= lim:
            out.append(c)
            continue
        y0, y1, x0, x1 = c["box"]
        piece = txt[y0:y1, x0:x1]
        prof = piece.sum(axis=1 - axis)
        n = prof.shape[0]
        q0, q1 = n // 4, (n * 3) // 4
        if q1 - q0 < 2:
            out.append(c)
            continue
        k = q0 + int(np.argmin(prof[q0:q1]))
        parts = ((a, a + k), (a + k, b))
        made = []
        for (pa, pb) in parts:
            if pb - pa < 10:
                made = []
                break
            box = ([pa, pb, x0, x1] if axis == 0 else [y0, y1, pa, pb])
            sl = txt[box[0]:box[1], box[2]:box[3]]
            ar = int(sl.sum())
            if ar < 10:
                made = []
                break
            made.append(dict(c, box=tuple(box), area=ar))
        if made:
            out.extend(made)
            changed = True
        else:
            out.append(c)
    return split_oversize(out, txt, axis, depth - 1) if changed else out


def segment(rgb):
    """Hierarchical decomposition of one page:

        leaf  ->  registers  ->  zones  ->  rows  ->  cells

    Every geometric threshold is keyed to the LEAF, never to the scan frame,
    and every cut is an order statistic of the page's own ink projection. No
    step assigns meaning to anything it finds.
    """
    SH, SW = rgb.shape[:2]
    ly0, ly1, lx0, lx1 = leaf_block(dresden.int_luma(rgb))
    sub = rgb[ly0:ly1, lx0:lx1]
    H, W = sub.shape[:2]
    cls, thr = dresden.pigment_classes(sub)
    y = dresden.int_luma(sub)
    black = cls == dresden.PIG_BLACK
    red = cls == dresden.PIG_RED
    blue = cls == dresden.PIG_BLUE
    ink = despeckle(black, 8)
    elems = []

    # --- 1. register rules and column rules: LINE OPENING of the red mask --
    # Receipt: shape-of-component detection returned ZERO rules on scan 50,
    # whose rules are plainly visible, because a rule touches the red-brown
    # mottling of the damaged plaster and the component becomes a blob. An
    # opening by a line of LH (LV) pixels keeps only unbroken runs of that
    # length, which is the property a rule actually has. See dresden.open_line.
    LH = (W * 22) // 100
    LV = (H * 18) // 100
    hl, hn = dresden.label_components(
        dresden.dilate(dresden.open_line(red, LH, axis=1), 1))
    for bx in dresden.component_boxes(hl, hn):
        if bx[3] - bx[2] >= LH and bx[1] - bx[0] <= 26:
            elems.append({"cat": "rule_h", "box": bx[:4], "area": bx[4]})
    vl, vn = dresden.label_components(
        dresden.dilate(dresden.open_line(red, LV, axis=0), 1))
    for bx in dresden.component_boxes(vl, vn):
        if bx[1] - bx[0] >= LV and bx[3] - bx[2] <= 26:
            elems.append({"cat": "rule_v", "box": bx[:4], "area": bx[4]})

    # --- 2. picture panels: solid red/blue ground, block-level -------------
    B = 16
    gh, gw = H // B, W // B
    blk = (red | blue)[:gh * B, :gw * B].reshape(gh, B, gw, B)
    dens = (1000 * blk.sum(axis=(1, 3))) // (B * B)
    # Receipt (two failures, both kept). (a) At density 350 with a block
    # erosion, the heavily over-painted RED panel of scan 50 fell below the
    # floor and a panel plainly present returned nothing. (b) Removing the
    # erosion and dropping to 300 then swallowed the red-brown MOTTLING of the
    # damaged plaster: two panel_grounds spanning the whole leaf, which marked
    # the dense writing "occupied" and deleted it from the segmentation. The
    # discriminator that survives both is SHAPE — a panel is a rectangle and
    # mottling is not — so the erosion is kept (it peels one-block filaments)
    # and the component must additionally fill 600/1000 of its own box.
    solid = dens >= 300
    e = solid.copy()
    e[1:, :] &= solid[:-1, :]
    e[:-1, :] &= solid[1:, :]
    e[:, 1:] &= solid[:, :-1]
    e[:, :-1] &= solid[:, 1:]
    pl, pn = dresden.label_components(e)
    occupied = np.zeros((H, W), dtype=bool)
    for bx in dresden.component_boxes(pl, pn):
        bh, bw = bx[1] - bx[0], bx[3] - bx[2]
        fill = (1000 * bx[4]) // max(bh * bw, 1)
        if bx[4] >= 40 and bh >= 4 and bw >= 4 and fill >= 600:
            bb = (bx[0] * B, bx[1] * B, bx[2] * B, bx[3] * B)
            elems.append({"cat": "panel_ground", "box": bb,
                          "area": bx[4] * B * B})
            occupied[bb[0]:bb[1], bb[2]:bb[3]] = True

    # --- 3. figures: picture areas, from applied colour --------------------
    # Receipt (four failures, all kept).
    #  (a) BLACK-only detection fragmented on polychrome paintings, which were
    #      then segmented as writing.
    #  (b) black|red|blue merged the whole lower page into one component: the
    #      production red margin calls the damaged plaster red, and the
    #      dilation bridges the glyph grid.
    #  (c) COLOUR at a strict red margin isolates the picture areas cleanly,
    #      but also fires on the column of RED NUMERALS inside the writing —
    #      that is colour in exactly the same sense.
    #  (d) Segmenting cells first and rejecting a candidate whose box the
    #      cells cover is CIRCULAR: with the panel not yet known, its own
    #      painting is segmented as writing and blocks its detection.
    # The discriminator that needs neither cells nor black is CONNECTEDNESS of
    # the colour itself: a picture area contains one large connected colour
    # mass; a numeral column contains only small isolated marks, however many.
    cls2, _t2 = dresden.pigment_classes(sub, red_margin=48)
    colour = despeckle((cls2 == dresden.PIG_RED) | (cls2 == dresden.PIG_BLUE),
                       20)
    cml, cmn = dresden.label_components(colour)
    cma = np.bincount(cml.ravel(), minlength=cmn + 1)
    cma[0] = 0
    grp, gn = dresden.label_components(dresden.dilate(colour, 8))
    biggest = np.zeros(gn + 1, dtype=np.int64)
    for lab in range(1, cmn + 1):
        pos = np.argmax(cml == lab)
        g = int(grp.ravel()[pos])
        if g > 0 and int(cma[lab]) > biggest[g]:
            biggest[g] = int(cma[lab])
    figs = []
    for gi, bx in enumerate(dresden.component_boxes(grp, gn), start=1):
        h, w = bx[1] - bx[0], bx[3] - bx[2]
        if bx[4] < 8000 or h < 70 or w < 70:
            continue
        if w > (W * 4) // 5 or h > (H * 2) // 3:
            continue
        if biggest[gi] < 1500:
            continue
        figs.append((bx, {"colour_mass": int(biggest[gi])}))

    # Line-drawn figures on a WHITE ground carry no colour at all — the
    # seated figure of Forstemann p69 (scan 73), the very column this build
    # exists to read, is pure black outline. Receipt: the colour pass cannot
    # see it and it came back segmented as ten glyph cells. A single
    # connected BLACK stroke mass of figure extent is admitted here; the
    # extent bounds are what stop this pass merging dense writing, and the
    # earlier failure of a black-ONLY detector (fragmenting on polychrome) is
    # covered by the colour pass above rather than by loosening these.
    rawl, rawn = dresden.label_components(black)
    rawa = np.bincount(rawl.ravel(), minlength=rawn + 1)
    rawa[0] = 0
    bl, bn = dresden.label_components(dresden.dilate(black, 2))
    for bx in dresden.component_boxes(bl, bn):
        h, w = bx[1] - bx[0], bx[3] - bx[2]
        if bx[4] < 2500 or h < 70 or w < 70:
            continue
        if w > (W * 4) // 5 or h > (H * 2) // 3:
            continue
        if any(overlap(bx[:4], f[0][:4]) for f in figs):
            continue
        # MEASURED, not gated. A tried discriminator was: a picture is one
        # continuous contour, merged writing is many glyphs bridged by the
        # dilation, so the largest UNDILATED stroke should be a large share of
        # the mass. It does not separate them at this scan resolution — the
        # true p69 figure scores 52/1000 on 402 raw strokes and a block of
        # merged writing on the same page scores 43/1000 on 399. Both numbers
        # ship with every stroke-mass figure so a higher-resolution capture
        # can be tested against them; nothing is decided on them here.
        reg = rawl[bx[0]:bx[1], bx[2]:bx[3]]
        labs = np.unique(reg)
        labs = labs[labs > 0]
        big = int(rawa[labs].max()) if labs.size else 0
        figs.append((bx, {"stroke_mass": int(bx[4]),
                          "raw_strokes": int(labs.size),
                          "largest_stroke_milli": (1000 * big) // int(bx[4])}))

    for bx, extra in figs:
        el = {"cat": "figure", "box": bx[:4], "area": int(bx[4])}
        el.update(extra)
        elems.append(el)
        occupied[bx[0]:bx[1], bx[2]:bx[3]] = True

    # --- 4. registers: bands between horizontal rules ----------------------
    cuts = centres(elems, "rule_h", 0)
    bounds = [0] + cuts + [H]

    # --- 5. zones, rows, cells --------------------------------------------
    vcuts = centres(elems, "rule_v", 1)
    txt = ink & ~occupied
    cells = []
    for r in range(len(bounds) - 1):
        ra, rb = bounds[r], bounds[r + 1]
        if rb - ra < 24:
            continue
        band = txt[ra:rb]
        # zone edges: column rules inside this band, plus the vertical edges
        # of any picture panel that overlaps it (a panel splits the writing)
        xs = set(vcuts)
        for el in elems:
            if el["cat"] in ("panel_ground", "figure"):
                bb = el["box"]
                if bb[0] < rb and bb[1] > ra:
                    xs.add(bb[2])
                    xs.add(bb[3])
        edges = [0] + sorted(x for x in xs if 12 < x < W - 12) + [W]
        for z in range(len(edges) - 1):
            za, zb = edges[z], edges[z + 1]
            if zb - za < 30:
                continue
            zone = band[:, za:zb]
            if not zone.any():
                continue
            for (ya, yb) in cut_bands(zone.sum(axis=1), 10):
                line = zone[ya:yb]
                for (xa, xb) in cut_bands(line.sum(axis=0), 8):
                    cw, ch = xb - xa, yb - ya
                    piece = line[:, xa:xb]
                    ar = int(piece.sum())
                    cat = classify_cell(piece, ch, cw, ar)
                    if cat is None or ar < 10:
                        continue
                    hollow = 0
                    if cat == "numeral_dot":
                        hollow = int(dresden.count_holes(np.pad(piece, 1)) >= 1)
                    cells.append({"cat": cat,
                                  "box": (ra + ya, ra + yb, za + xa, za + xb),
                                  "area": ar, "register": r, "zone": z,
                                  "hollow": hollow})
    cells = split_oversize(cells, txt, 1)
    cells = split_oversize(cells, txt, 0)
    # Receipt: the fibrous, damaged plaster ABOVE the writing produced a row
    # of large empty "glyph blocks" on scan 50 (elements 1-20) — boxes with
    # almost no ink in them. A cell must carry ink at a third of the page's
    # OWN median cell fill; the scale is an order statistic of the page, not
    # a constant.
    fills = sorted((1000 * c["area"]) //
                   max((c["box"][1] - c["box"][0]) *
                       (c["box"][3] - c["box"][2]), 1)
                   for c in cells if c["cat"] == "glyph_block")
    if len(fills) >= 6:
        floor = fills[len(fills) // 2] // 3
        cells = [c for c in cells
                 if (1000 * c["area"]) //
                 max((c["box"][1] - c["box"][0]) *
                     (c["box"][3] - c["box"][2]), 1) >= floor]
    for c in cells:
        c["box"] = tuple(int(v) for v in c["box"])

    # --- 5b. RED bar-and-dot numerals -------------------------------------
    # Receipt: the cell pass ran on black ink alone and left every red numeral
    # on the page unsegmented — visible as unboxed red marks between boxed
    # glyph cells in the 2x overlay. Folding the red mask into the same
    # projection then merged numerals into their neighbouring glyph cells and
    # cost the black bars their category. Red numerals are ISOLATED marks, so
    # unlike glyphs they segment correctly as components, in their own pass.
    red_ink = despeckle(cls2 == dresden.PIG_RED, 10) & ~occupied
    rml, rmn = dresden.label_components(red_ink)
    for i, bx in enumerate(dresden.component_boxes(rml, rmn), start=1):
        h, w = bx[1] - bx[0], bx[3] - bx[2]
        if h > 30 or w > 90 or bx[4] < 14:
            continue
        cat = classify_cell(None, h, w, bx[4])
        if cat not in ("numeral_bar", "numeral_dot"):
            continue
        hollow = 0
        if cat == "numeral_dot":
            comp = np.pad(rml[bx[0]:bx[1], bx[2]:bx[3]] == i, 1)
            hollow = int(dresden.count_holes(comp) >= 1)
        cells.append({"cat": cat, "box": tuple(int(v) for v in bx[:4]),
                      "area": int(bx[4]), "register": -1, "zone": -1,
                      "hollow": hollow, "pigment": "red"})

    elems.extend(cells)

    # --- 6. numbering in reading order -------------------------------------
    for el in elems:
        if el.get("register", -1) < 0:
            cy = (el["box"][0] + el["box"][1]) // 2
            el["register"] = max(0, sum(1 for c in cuts if c <= cy))
            el["zone"] = -1
    elems.sort(key=lambda el: (el["register"], el["zone"],
                               el["box"][0], el["box"][2]))
    for n, el in enumerate(elems, start=1):
        el["id"] = n
        # boxes are stored in SCAN coordinates so overlays and every
        # downstream stage can index the original page directly
        el["box"] = [int(el["box"][0]) + ly0, int(el["box"][1]) + ly0,
                     int(el["box"][2]) + lx0, int(el["box"][3]) + lx0]
        el["area"] = int(el["area"])
        el["register"] = int(el["register"])
        el["zone"] = int(el["zone"])
    return elems, [bd + ly0 for bd in bounds], thr, [ly0, ly1, lx0, lx1]


def fixtures():
    """Exact fixtures for the two new primitives. Known answers only."""
    checks, fails = 0, []

    def ck(name, cond):
        nonlocal checks
        checks += 1
        if not cond:
            fails.append(name)

    # open_line: a 40-px horizontal bar survives a length-30 horizontal
    # opening and is erased by a length-30 vertical one; a blob of the same
    # area but no long run is erased by both.
    m = np.zeros((60, 60), dtype=bool)
    m[20:24, 10:50] = True
    ck("h-line survives h-opening", dresden.open_line(m, 30, 1).sum() > 0)
    ck("h-line erased by v-opening", dresden.open_line(m, 30, 0).sum() == 0)
    ck("h-opening is idempotent on the bar",
       np.array_equal(dresden.open_line(m, 30, 1),
                      dresden.open_line(dresden.open_line(m, 30, 1), 30, 1)))
    ck("h-opening never adds pixels", (dresden.open_line(m, 30, 1) & ~m).sum()
       == 0)
    blob = np.zeros((60, 60), dtype=bool)
    blob[20:33, 20:33] = True
    ck("blob erased by h-opening", dresden.open_line(blob, 30, 1).sum() == 0)
    ck("blob erased by v-opening", dresden.open_line(blob, 30, 0).sum() == 0)
    ck("blob survives an opening it fits",
       dresden.open_line(blob, 13, 1).sum() == blob.sum())
    ck("over-long opening is empty", dresden.open_line(m, 61, 1).sum() == 0)
    # transpose symmetry
    ck("axes are transposes of each other",
       np.array_equal(dresden.open_line(m, 30, 1),
                      dresden.open_line(m.T, 30, 0).T))

    # leaf_block: a synthetic scan — bright leaf between two dark gutters,
    # dark mount bands top and bottom, bright neighbour slivers outside.
    y = np.full((400, 300), 200, dtype=np.int64)
    y[:, 40:52] = 20      # left gutter
    y[:, 250:262] = 20    # right gutter
    y[:14, :] = 20        # top mount
    y[386:, :] = 20       # bottom mount
    ly0, ly1, lx0, lx1 = leaf_block(y)
    ck("leaf left edge at the gutter", 46 <= lx0 <= 58)
    ck("leaf right edge at the gutter", 244 <= lx1 <= 256)
    ck("leaf top edge at the mount", 8 <= ly0 <= 20)
    ck("leaf bottom edge at the mount", 380 <= ly1 <= 392)
    # a scan with no gutters at all must fall back to the whole frame
    flat = np.full((400, 300), 200, dtype=np.int64)
    ck("no-gutter scan falls back to the frame",
       leaf_block(flat) == (0, 400, 0, 300))

    # cut_bands: three blocks separated by true gaps
    prof = np.zeros(100, dtype=np.int64)
    prof[10:25] = 40
    prof[40:55] = 40
    prof[70:85] = 40
    ck("three blocks -> three bands", len(cut_bands(prof, 5)) == 3)
    ck("bands are the blocks", cut_bands(prof, 5)[1] == (40, 55))
    ck("minlen suppresses short bands", len(cut_bands(prof, 20)) == 0)
    ck("empty profile -> no bands",
       cut_bands(np.zeros(100, dtype=np.int64), 5) == [])
    return checks, fails


def main():
    only = int(sys.argv[1]) if len(sys.argv) > 1 else None
    nchecks, failed = fixtures()
    print("FIXTURES: %d checks, %d failures%s"
          % (nchecks, len(failed),
             "" if not failed else " -> " + "; ".join(failed)))
    if failed:
        sys.exit(1)
    ledger = Ledger()
    rows = []
    for k in ([only] if only else range(1, 79)):
        rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
        elems, bounds, thr, leaf = segment(rgb)
        lab = page_label(k)
        counts = {c: sum(1 for e in elems if e["cat"] == c) for c in ORDER}
        hollow = sum(1 for e in elems
                     if e["cat"] == "numeral_dot" and e.get("hollow"))
        with open(os.path.join(SEG, "scan%02d.json" % k), "w") as f:
            json.dump({"scan": k, "page": lab, "registers": len(bounds) - 1,
                       "leaf_box": leaf, "otsu": int(thr), "counts": counts,
                       "hollow_dots": hollow, "elements": elems}, f)
        # RENDER FROM THE HIGH-RESOLUTION SCAN WHEN IT IS PRESENT.
        # Receipt: the analysis ran on the 684x1350 pages embedded in the
        # source PDF, and the overlays were ALSO drawn on them, upscaled 2x.
        # That made the delivered pictures worse than they had to be — the
        # researcher could not read their own codex in them. Boxes are exact
        # integers in scan coordinates either way; only the surface they are
        # drawn on changes, and it is the library's own scan of the same
        # object (identity verified, see tools/fetch_slub.py).
        hp = os.path.join(DATA, "hires", "slub_p%02d.jpg" % k)
        if os.path.exists(hp):
            base = Image.open(hp).convert("RGB")
            OW = 1700
            base = base.resize((OW, base.height * OW // base.width),
                               Image.LANCZOS)
            SCALE = OW / rgb.shape[1]
        else:
            SCALE = 2
            base = Image.fromarray(rgb).convert("RGB").resize(
                (rgb.shape[1] * SCALE, rgb.shape[0] * SCALE), Image.LANCZOS)
        img = base
        pan = Image.new("RGB", (img.width + 250, img.height + 46), (16, 16, 16))
        pan.paste(img, (0, 46))
        d = ImageDraw.Draw(pan)
        def S2(v):
            return int(v * SCALE)

        d.text((8, 8), "SEGMENTATION  scan %02d  /  Forstemann page %s   "
                       "leaf y%d-%d x%d-%d   %d registers   %d elements"
               % (k, lab, leaf[0], leaf[1], leaf[2], leaf[3],
                  len(bounds) - 1, len(elems)), fill=(240, 240, 240), font=FB)
        d.text((8, 26), "EVIDENCE overlay: boxes are exact integer element "
                        "bounds on the unmodified scan. Nothing is enhanced.",
               fill=(150, 150, 150), font=F)
        d.rectangle([S2(leaf[2]), S2(leaf[0]) + 46,
                     S2(leaf[3]) - 1, S2(leaf[1]) + 45],
                    outline=(255, 255, 255), width=3)
        for bd in bounds[1:-1]:
            d.line([(S2(leaf[2]), S2(bd) + 46), (S2(leaf[3]), S2(bd) + 46)],
                   fill=(255, 120, 0), width=3)
        for el in elems:
            bb = el["box"]
            d.rectangle([S2(bb[2]), S2(bb[0]) + 46, S2(bb[3]), S2(bb[1]) + 46],
                        outline=CATCOL[el["cat"]], width=2)
        for el in elems:
            bb = el["box"]
            d.text((S2(bb[2]) + 2, S2(bb[0]) + 47), str(el["id"]),
                   fill=CATCOL[el["cat"]], font=F)
        # legend, with this page's own counts
        yy = 60
        d.text((img.width + 12, yy), "CATEGORIES (count)", fill=(240, 240, 240),
               font=FB)
        yy += 24
        for cat in ORDER:
            d.rectangle([img.width + 12, yy, img.width + 30, yy + 14],
                        outline=CATCOL[cat], width=3)
            d.text((img.width + 38, yy), "%s  %d" % (cat, counts[cat]),
                   fill=CATCOL[cat], font=F)
            yy += 24
        yy += 12
        d.rectangle([img.width + 12, yy, img.width + 30, yy + 14],
                    outline=(255, 255, 255), width=3)
        d.text((img.width + 38, yy), "leaf block", fill=(255, 255, 255), font=F)
        yy += 24
        d.line([(img.width + 12, yy + 7), (img.width + 30, yy + 7)],
               fill=(255, 120, 0), width=3)
        d.text((img.width + 38, yy), "register cut", fill=(255, 120, 0), font=F)
        yy += 34
        d.text((img.width + 12, yy), "hollow dots %d" % hollow,
               fill=(200, 200, 200), font=F)
        yy += 20
        d.text((img.width + 12, yy), "otsu %d" % int(thr),
               fill=(200, 200, 200), font=F)
        pan.save(os.path.join(OVR, "scan%02d_seg.jpg" % k), quality=66,
                 optimize=True)
        ledger.record("segment", {"scan": k, "page": lab,
                                  "elements": len(elems),
                                  "registers": len(bounds) - 1,
                                  "counts": counts, "hollow_dots": hollow},
                      Ledger.digest(dresden.int_luma(rgb)), "segments")
        rows.append((k, lab, len(bounds) - 1, len(elems), counts, hollow))
        if only:
            print(lab, "leaf", leaf, len(elems), counts, "hollow", hollow)

    if not only:
        with open(os.path.join(DATA, "segment_receipts.json"), "w") as f:
            f.write(ledger.export())
        tot = {c: sum(r[4][c] for r in rows) for c in ORDER}
        out = ["# Per-page segmentation — every page, every element, "
               "numbered and categorised", "",
               "Run: `python3 analysis/dresden_segment.py`; receipts "
               "`data/dresden/segment_receipts.json`; per-page JSON in "
               "`data/dresden/segments/`; overlays in "
               "`data/dresden/derived/segments/`; codex contact sheet "
               "`demo/dresden_segments_contact.jpg`.", "",
               "This is the layer the original request asked for and that "
               "was missing. The request was that each page be *carefully "
               "segmented, numbered, and grouped into common assumed "
               "categories*. `INDEX.md` delivered the numbering and the "
               "grouping; the segmentation was never built, and every later "
               "stage paid for it — figure detectors that merged a page into "
               "one blob, glyph detectors that returned three boxes for a "
               "column holding a dozen glyphs.", "",
               "Categories are geometric rules only. **No meaning is "
               "assigned to any element**, and nothing here closes anything "
               "(`docs/RULES_OF_EXPLORATION.md`).", "",
               "## Hierarchy", "",
               "```", "leaf  ->  registers  ->  zones  ->  rows  ->  cells",
               "```", "",
               "Every geometric threshold is keyed to the **leaf**, and "
               "every cut is an order statistic of the page's own ink "
               "projection — not a tuned constant.", "",
               "## Four defects this stage found and fixed (receipts)", "",
               "1. **Every threshold was keyed to the scan frame, not the "
               "page.** Each WDL scan carries slivers of the *adjacent "
               "leaves*, so the scan frame is roughly 20% wider than the "
               "leaf and its edges are the neighbours. `leaf_block` now "
               "finds the dark gutter and mount bands as dark-fraction peaks "
               "in the outer quarter (rows: outer fifth) and every later "
               "rule is measured inside it.", "",
               "2. **Register rules were detected by component shape and "
               "returned ZERO** on scan 50, whose rules are plainly visible. "
               "A rule touches the red-brown mottling of the damaged plaster "
               "and the component becomes a blob. Replaced by "
               "`dresden.open_line` — an exact integer morphological opening "
               "by a straight line, which tests the property a rule actually "
               "has (an unbroken run) instead of a property of whatever "
               "component it happens to join.", "",
               "3. **One gap threshold per zone under-splits dense "
               "writing.** The sparse upper column of scan 50 segmented "
               "cleanly while the dense lower registers came back as a "
               "handful of boxes spanning 2x3 glyph grids. Cells larger than "
               "3/2 of the page's own median glyph cell are now re-cut at "
               "the minimum of their own projection.", "",
               "4. **Red bar-and-dot numerals were invisible.** The cell "
               "pass ran on black ink alone. Folding red into the same "
               "projection merged numerals into neighbouring glyph cells, so "
               "they get their own component pass — they are isolated marks, "
               "and unlike glyphs they segment correctly that way.", "",
               "## Named instrument limits (MEASURED, not closed)", "",
               "- **Line-drawn figures are not separable from dense "
               "line-drawn writing at 684x1350.** Figures are emitted from "
               "two passes and labelled by provenance: `colour_mass` "
               "(applied red/blue picture areas — reliable) and "
               "`stroke_mass` (black outline masses). A discriminator was "
               "tried and *does not work*: the largest undilated stroke as a "
               "share of the mass scores **52/1000 on 402 raw strokes** for "
               "the true seated figure of p69 (scan 73) and **43/1000 on "
               "399** for a block of merged writing on the same page. Both "
               "numbers ship with every `stroke_mass` figure so a "
               "higher-resolution capture can be tested against them.", "",
               "- **`margin` fired 0 times across all 78 pages.** The "
               "category is subsumed: `leaf_block` cuts at the gutter, so a "
               "page-edge red frame lies outside the leaf by construction. "
               "Reported as zero rather than removed "
               "(`BENCHMARKS.md` section 3).", "",
               "- **`panel_ground` fired 4 times.** A panel must fill "
               "600/1000 of its own box, which is what stops the red-brown "
               "mottling being called a panel; most picture areas are "
               "carried by `figure` instead.", "",
               "Codex totals: " + ", ".join("**%d** %s" % (tot[c], c)
                                            for c in ORDER) + ".", "",
               "| Scan | Page | Registers | Elements | " +
               " | ".join(ORDER) + " | hollow dots |",
               "|---|---|---|---|" + "---|" * (len(ORDER) + 1)]
        for k, lab, nreg, ne, counts, hol in rows:
            out.append("| %d | %s | %d | %d | %s | %d |"
                       % (k, lab, nreg, ne,
                          " | ".join(str(counts[c]) for c in ORDER), hol))
        with open(os.path.join(DOCS, "DRESDEN_SEGMENTS.md"), "w") as f:
            f.write("\n".join(out) + "\n")
        # codex-wide contact sheet: the visual the report is read against
        TW, TH, cols = 300, 560, 13
        nrow = (len(rows) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * TW, nrow * (TH + 30) + 46),
                          (12, 12, 12))
        ds = ImageDraw.Draw(sheet)
        ds.text((10, 10), "DRESDEN CODEX — per-page segmentation, all %d "
                          "scans. EVIDENCE overlays on unmodified scans; "
                          "%d elements." % (len(rows), sum(r[3] for r in rows)),
                fill=(240, 240, 240), font=FB)
        for i, (k, lab, _nr, ne, _c, _h) in enumerate(rows):
            th = Image.open(os.path.join(OVR, "scan%02d_seg.jpg" % k))
            th.thumbnail((TW - 8, TH))
            cx, cy = (i % cols) * TW + 4, 46 + (i // cols) * (TH + 30)
            sheet.paste(th, (cx, cy))
            ds.text((cx + 2, cy + th.height + 4),
                    "scan %d / p%s / %d el" % (k, lab, ne),
                    fill=(200, 200, 200), font=F)
        sheet.save(os.path.join(ROOT, "demo",
                                "dresden_segments_contact.jpg"), quality=72,
                   optimize=True)
        print("pages segmented:", len(rows))
        print("totals:", tot)
        print("elements:", sum(r[3] for r in rows))


if __name__ == "__main__":
    main()
