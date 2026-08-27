"""Region report — point the machine at any spot in the codex.

`python3 analysis/dresden_region.py <page> [y0 y1 x0 x1]`
  <page>  Förstemann page label (e.g. 73); box defaults to the page's
          bottom-left quadrant if omitted. Coordinates in full-res pixels.

One command answers "look at page X, bottom left": the full lens stack on
the region (original, highlight freeze, shadow, pigment classes, white
path), plus the machine's findings inside it — glyph cells with dihedral
sector codes matched across the WHOLE codex (where else each form occurs),
blue-pigment components, white nodes, hollow/solid dots — written to
docs/regions/ with a panel in demo/. Exact integers throughout; receipts.
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import dresden
from cram_dsp.forensics import Ledger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "dresden")
DEMO = os.path.join(ROOT, "demo")
RDOC = os.path.join(ROOT, "docs", "regions")
os.makedirs(RDOC, exist_ok=True)


def scan_for_page(label: str) -> int:
    if label.endswith("*"):
        base = int(label.rstrip("*"))
        stars = len(label) - len(str(base))
        return 28 + stars if base == 28 else 64
    p = int(label)
    if p <= 28:
        return p
    if p <= 60:
        return p + 3
    return p + 4


def page_label(k: int) -> str:
    if 1 <= k <= 28:
        return str(k)
    if k in (29, 30, 31):
        return "28" + "*" * (k - 28)
    if 32 <= k <= 63:
        return str(k - 3)
    if k == 64:
        return "60*"
    return str(k - 4)


def page_path(k):
    return os.path.join(DATA, "pages", "wdl11621_scan%02d.jpg" % k)


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "73"
    k = scan_for_page(label)
    if len(sys.argv) >= 6:
        y0, y1, x0, x1 = (int(v) for v in sys.argv[2:6])
    else:
        y0, y1, x0, x1 = 675, 1350, 0, 342   # bottom-left quadrant

    rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
    y = dresden.int_luma(rgb)
    reg_rgb = rgb[y0:y1, x0:x1]
    reg_y = y[y0:y1, x0:x1]

    # lenses on the region
    fz, lo, hi = dresden.highlight_freeze(reg_y)
    sh, slo, shi = dresden.highlight_freeze(reg_y, 30, 500)
    cls, cthr = dresden.pigment_classes(reg_rgb)
    wthr, wnodes = dresden.white_nodes(reg_y)
    wseq, wtour = dresden.white_path(wnodes, min_sep=40)

    # cells inside the region, with codes
    res = dresden.analyze_page(rgb)
    mask = dresden.ink_mask(y, res["threshold"])
    inside = [(b, s) for b, s in zip(res["boxes"], res["signatures"])
              if b[0] >= y0 and b[1] <= y1 and b[2] >= x0 and b[3] <= x1]
    q_sect = [dresden.sector_signature(mask[b[0]:b[1], b[2]:b[3]])
              for b, _ in inside]

    # global stack for cross-codex matching
    g_cells, g_ring, g_sect = [], [], []
    for kk in range(1, 79):
        rr = np.asarray(Image.open(page_path(kk)).convert("RGB"))
        yy = dresden.int_luma(rr)
        rres = dresden.analyze_page(rr)
        mm = dresden.ink_mask(yy, rres["threshold"])
        for b, s in zip(rres["boxes"], rres["signatures"]):
            g_cells.append((kk, b))
            g_ring.append(s)
            g_sect.append(dresden.sector_signature(mm[b[0]:b[1], b[2]:b[3]]))
    GR = np.asarray(g_ring, dtype=np.int64)
    GV = np.stack([dresden.dihedral_variants(s) for s in g_sect])

    matches = []
    for (b, rs), ss in zip(inside, q_sect):
        dr = np.abs(GR - np.asarray(rs)).sum(axis=1)
        dsec = None
        for v in range(8):
            dv = np.abs(np.asarray(ss)[None, :] - GV[:, v, :]).sum(axis=1)
            dsec = dv if dsec is None else np.minimum(dsec, dv)
        d = dr + dsec
        order = np.argsort(d, kind="stable")
        top = []
        for gi in order:
            gk, gb = g_cells[int(gi)]
            if gk == k and gb == b:
                continue
            top.append((int(d[gi]), gk, gb))
            if len(top) == 3:
                break
        matches.append((b, top))

    # blue components + dots in the region
    blab, bn = dresden.label_components(cls == dresden.PIG_BLUE)
    blues = [bb for bb in dresden.component_boxes(blab, bn) if bb[4] >= 60]
    hollow, solid = dresden.classify_dots(dresden.ink_mask(reg_y, cthr))

    # panel
    S = 2
    w, h = x1 - x0, y1 - y0
    def rgb_of(arr):
        g = arr.astype(np.uint8)
        return np.stack([g, g, g], axis=2)
    pig = np.zeros((h, w, 3), dtype=np.uint8)
    for c, col in enumerate([(232, 223, 206), (25, 22, 18),
                             (166, 59, 42), (79, 163, 165)]):
        pig[cls == c] = col
    tiles = [
        ("original", Image.fromarray(reg_rgb)),
        ("freeze %d..%d" % (lo, hi), Image.fromarray(rgb_of(fz))),
        ("shadow %d..%d" % (slo, shi), Image.fromarray(rgb_of(sh))),
        ("pigment classes", Image.fromarray(pig)),
    ]
    wp = Image.fromarray(rgb_of(fz))
    dr2 = ImageDraw.Draw(wp)
    pts = [(x * 1, yv * 1) for (yv, x) in wseq]
    for a, bpt in zip(pts, pts[1:]):
        dr2.line([a, bpt], fill=(255, 200, 30), width=2)
    for i, (x, yv) in enumerate(pts):
        dr2.ellipse([x - 7, yv - 7, x + 7, yv + 7], outline=(0, 220, 255),
                    width=2)
        dr2.text((x + 9, yv - 6), str(i + 1), fill=(0, 220, 255))
    tiles.append(("white path (thr %d)" % wthr, wp))

    panel = Image.new("RGB", ((w * S + 10) * len(tiles) + 10, h * S + 34),
                      (12, 12, 12))
    pd = ImageDraw.Draw(panel)
    for i, (ttl, im) in enumerate(tiles):
        panel.paste(im.resize((w * S, h * S), Image.NEAREST),
                    (10 + i * (w * S + 10), 28))
        pd.text((10 + i * (w * S + 10), 8), ttl, fill=(255, 210, 40))
    pname = "dresden_region_p%s_%d_%d.png" % (label, y0, x0)
    panel.save(os.path.join(DEMO, pname))

    # report
    L = ["# Region report — page %s (scan %d), box y[%d:%d] x[%d:%d]" % (
            label, k, y0, y1, x0, x1),
         "",
         "Panel: `demo/%s` (original | freeze | shadow | pigment | white path)." % pname,
         "",
         "Glyph cells in region: %d. White nodes: %d (path tour %d px). "
         "Blue components (area >= 60): %d. Dots: %d hollow / %d solid." % (
             len(inside), len(wnodes), wtour, len(blues), len(hollow),
             len(solid)),
         "",
         "## Cross-codex form matches (per cell: 3 nearest by ring+dihedral-sector code)",
         "",
         "| Cell (y0,y1,x0,x1) | #1 | #2 | #3 |"]
    L.append("|---|---|---|---|")
    for (b, _), (_, top) in zip(inside, matches):
        cols = ["p%s (%d,%d) d=%d" % (page_label(gk), gb[0], gb[2], dd)
                for dd, gk, gb in top]
        while len(cols) < 3:
            cols.append("—")
        L.append("| (%d,%d,%d,%d) | %s | %s | %s |" % (
            b[0], b[1], b[2], b[3], cols[0], cols[1], cols[2]))
    if blues:
        L += ["", "## Blue components (region coordinates)", ""]
        L += ["- area %d at (y %d..%d, x %d..%d)" % (
            bb[4], bb[0], bb[1], bb[2], bb[3]) for bb in blues]

    ledger = Ledger()
    ledger.record("region_report",
                  {"page": label, "scan": k, "box": [y0, y1, x0, x1],
                   "cells": len(inside), "white_nodes": len(wnodes),
                   "blue_components": len(blues),
                   "hollow": len(hollow), "solid": len(solid)},
                  Ledger.digest(y), Ledger.digest(reg_y))
    L += ["", "Receipts chain head: `%s`" % ledger.chain]

    out = os.path.join(RDOC, "p%s_y%d_x%d.md" % (label, y0, x0))
    with open(out, "w") as f:
        f.write("\n".join(L) + "\n")
    print("report:", out)
    print("panel:", os.path.join("demo", pname))
    print("cells %d, white nodes %d, blue comps %d, dots %d/%d" % (
        len(inside), len(wnodes), len(blues), len(hollow), len(solid)))


if __name__ == "__main__":
    main()
