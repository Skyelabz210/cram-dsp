"""The discovery sweep — exploratory mode, whole codex, nothing passed silently.

Where analysis/dresden_run.py *tested* the illustrated claims, this sweep
*hunts* for instances of them across all 78 scans and emits ranked catalogs
with coordinates and panels, so that finding things does not depend on a
human (or an AI) happening to look at the right page:

  D1  Recurrence catalog — every glyph cell's ring code matched against all
      others (all pairs, codex-wide), k-NN graph at a data-derived exact
      threshold, clustered; top clusters rendered as crop panels.
  D2  Path gallery — the luminance-ordered sequence drawn on every page,
      pages ranked by tour coherence (permutation rank). Exploratory
      ranking signal; the blank-substrate caveat from DRESDEN_MACHINE.md
      stands and is restated once in the catalog.
  D3  Figure-dressing detector — large figures found automatically; their
      interior elements code-matched against the same page's glyph cells
      outside the figure ("glyphs dress the character" hunted everywhere).
  D4  Dot topology census — small round marks split hollow vs solid by
      exact hole counting (the turtle-shell "stitching holes vs solid
      dots" distinction), per page, codex-wide.
  D5  Tonal band maps — exact quantile-band structure map per page (the
      honest "underlying layers" render).
  D6  Opportunity index — one row per page with every signal, ranked, so
      every page is accounted for.

All measurement integer-exact; renders are display-seam only.
Usage: python3 analysis/dresden_discover.py
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import dresden
from cram_dsp.forensics import Ledger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "dresden")
DER = os.path.join(DATA, "derived")
DEMO = os.path.join(ROOT, "demo")
DOCS = os.path.join(ROOT, "docs")
for d in (os.path.join(DER, "paths"), os.path.join(DER, "bands"),
          os.path.join(DER, "dots")):
    os.makedirs(d, exist_ok=True)

R = {"checks": 0, "fails": 0}
CAT = []          # catalog lines


def check(name, cond, n=1):
    R["checks"] += n
    if not cond:
        R["fails"] += 1
        CAT.append("  FAIL — %s" % name)
    return cond


def note(s):
    CAT.append(s)


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


def load_rgb(k):
    return np.asarray(Image.open(page_path(k)).convert("RGB"))


# ===========================================================================
# §0 fixture checks for the new primitives
# ===========================================================================
ring = np.zeros((9, 9), dtype=bool)
ring[2, 2:7] = ring[6, 2:7] = ring[2:7, 2] = ring[2:7, 6] = True
solid = np.zeros((9, 9), dtype=bool)
solid[3:6, 3:6] = True
check("hollow ring has exactly 1 hole", dresden.count_holes(ring) == 1)
check("solid block has 0 holes", dresden.count_holes(solid) == 0)
both = np.zeros((12, 24), dtype=bool)
both[2:7, 2:7] = ring[2:7, 2:7]
both[3:6, 14:17] = True
hb, sb = dresden.classify_dots(both, min_area=5, max_area=100)
check("dot census separates hollow/solid", len(hb) == 1 and len(sb) == 1)
ramp = np.arange(100, dtype=np.int64).reshape(10, 10)
bands = dresden.luma_bands(ramp, 5)
check("quantile bands partition the ramp evenly",
      [int((bands == i).sum()) for i in range(5)] == [20, 20, 20, 20, 20])
check("l1_matrix exact on knowns",
      dresden.l1_matrix([[0, 0], [3, 4]], [[1, 1]]).tolist() == [[2], [5]])

# ===========================================================================
# §1 sweep every page: cells, codes, raw components, figures, dots, bands
# ===========================================================================
ledger = Ledger()
sums = {}
with open(os.path.join(DATA, "SHA256SUMS.txt")) as f:
    for line in f:
        h, name = line.split()
        sums[name] = h

BAND_COLORS = [(20, 20, 30), (70, 60, 120), (170, 60, 170),
               (240, 150, 60), (250, 250, 230)]

pages = {}
for k in range(1, 79):
    rgb = load_rgb(k)
    y = dresden.int_luma(rgb)
    res = dresden.analyze_page(rgb)
    mask = dresden.ink_mask(y, res["threshold"])
    raw_labels, raw_n = dresden.label_components(mask)
    raw_boxes = dresden.component_boxes(raw_labels, raw_n)
    hollow, solid_d = dresden.classify_dots(mask)

    # figures: dilated components too large for the glyph-cell window
    merged = dresden.dilate(mask, 2)
    mlabels, mn = dresden.label_components(merged)
    figures = [b for b in dresden.component_boxes(mlabels, mn)
               if b[4] > 12000 and (b[1] - b[0]) >= 150]

    pages[k] = {"res": res, "mask": mask, "raw_labels": raw_labels,
                "raw_boxes": raw_boxes, "hollow": hollow, "solid": solid_d,
                "figures": figures, "y": y}

    # D5 tonal band map (quarter res, palette render)
    band = dresden.luma_bands(y, 5)
    bimg = np.zeros((band.shape[0], band.shape[1], 3), dtype=np.uint8)
    for i, c in enumerate(BAND_COLORS):
        bimg[band == i] = c
    Image.fromarray(bimg[::4, ::4]).save(
        os.path.join(DER, "bands", "scan%02d_bands.png" % k))

    # D2 path overlay (half res)
    im = Image.open(page_path(k)).convert("RGB")
    dr = ImageDraw.Draw(im)
    order = [i for _, i in res["luminance_order"]]
    centers = [res["centers"][i] for i in order]
    for (y0, x0), (y1, x1) in zip(centers, centers[1:]):
        dr.line([(x0, y0), (x1, y1)], fill=(255, 210, 40), width=2)
    for rank, (yy, xx) in enumerate(centers[:12]):
        dr.ellipse([xx - 7, yy - 7, xx + 7, yy + 7],
                   outline=(255, 120, 0), width=2)
        dr.text((xx + 9, yy - 6), str(rank + 1), fill=(255, 120, 0))
    im.resize((342, 675), Image.NEAREST).save(
        os.path.join(DER, "paths", "scan%02d_path.jpg" % k), quality=72)

    # D4 dot overlay (half res): hollow cyan boxes, solid orange boxes
    im2 = Image.open(page_path(k)).convert("RGB")
    dr2 = ImageDraw.Draw(im2)
    for b in solid_d:
        dr2.rectangle([b[2] - 1, b[0] - 1, b[3], b[1]],
                      outline=(255, 140, 0))
    for b in hollow:
        dr2.rectangle([b[2] - 2, b[0] - 2, b[3] + 1, b[1] + 1],
                      outline=(0, 220, 255), width=2)
    im2.resize((342, 675), Image.NEAREST).save(
        os.path.join(DER, "dots", "scan%02d_dots.jpg" % k), quality=72)

    ledger.record("discover_page",
                  {"scan": k, "page": page_label(k),
                   "cells": len(res["boxes"]), "raw_components": raw_n,
                   "figures": len(figures), "hollow_dots": len(hollow),
                   "solid_dots": len(solid_d)},
                  sums["pages/wdl11621_scan%02d.jpg" % k],
                  Ledger.digest(y))

check("all 78 pages swept", len(pages) == 78)

# ===========================================================================
# §2 D1 — codex-wide recurrence: all-pairs code matching + clustering
# ===========================================================================
sig_rows, cell_page, cell_box = [], [], []
for k in range(1, 79):
    res = pages[k]["res"]
    for b, s in zip(res["boxes"], res["signatures"]):
        sig_rows.append(s)
        cell_page.append(k)
        cell_box.append(b)
S = np.asarray(sig_rows, dtype=np.int64)
P = np.asarray(cell_page, dtype=np.int64)
N = S.shape[0]
check("global cell stack assembled", N > 7000)

BIG = np.int64(1) << 40
TOPK = 3
nn_same = np.full(N, BIG, dtype=np.int64)
nn_cross = np.full(N, BIG, dtype=np.int64)
nn_cross_j = np.zeros(N, dtype=np.int64)
top_idx = np.zeros((N, TOPK), dtype=np.int64)
top_d = np.zeros((N, TOPK), dtype=np.int64)

CH = 512
for i0 in range(0, N, CH):
    i1 = min(i0 + CH, N)
    d = np.abs(S[i0:i1, None, :] - S[None, :, :]).sum(axis=2)
    rows = np.arange(i0, i1)
    d[rows - i0, rows] = BIG          # self
    same = P[i0:i1, None] == P[None, :]
    ds = np.where(same, d, BIG)
    dc = np.where(~same, d, BIG)
    nn_same[i0:i1] = ds.min(axis=1)
    nn_cross[i0:i1] = dc.min(axis=1)
    nn_cross_j[i0:i1] = dc.argmin(axis=1)
    part = np.argpartition(d, TOPK, axis=1)[:, :TOPK]
    top_idx[i0:i1] = part
    top_d[i0:i1] = np.take_along_axis(d, part, axis=1)

# data-derived exact threshold: lower quartile of cross-page NN distances
nn_sorted = np.sort(nn_cross)
EDGE_T = int(nn_sorted[(N - 1) * 25 // 100])
note_edge = EDGE_T

parent = list(range(N))


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


edges = 0
for i in range(N):
    for j, dv in zip(top_idx[i], top_d[i]):
        if dv <= EDGE_T:
            ri, rj = find(i), find(int(j))
            if ri != rj:
                parent[ri] = rj
            edges += 1

clusters = {}
for i in range(N):
    clusters.setdefault(find(i), []).append(i)
clusters = sorted((v for v in clusters.values() if len(v) >= 4),
                  key=len, reverse=True)
check("recurrence clusters found", len(clusters) >= 10)

# multi-page reach of each cluster
def cluster_pages(c):
    return sorted(set(int(P[i]) for i in c))

# ===========================================================================
# §3 D3 — figure-dressing: interior elements vs the page's glyph cells
# ===========================================================================
dress_hits = []   # (dist, scan, fig_box, int_box, cell_box)
for k in range(1, 79):
    pg = pages[k]
    if not pg["figures"]:
        continue
    res = pg["res"]
    mask = pg["mask"]
    for fb in pg["figures"]:
        fy0, fy1, fx0, fx1, _ = fb
        interior = [b for b in pg["raw_boxes"]
                    if 40 <= b[4] <= 3000
                    and b[0] >= fy0 and b[1] <= fy1
                    and b[2] >= fx0 and b[3] <= fx1]
        outside = [(b, s) for b, s in zip(res["boxes"], res["signatures"])
                   if b[1] <= fy0 or b[0] >= fy1 or b[3] <= fx0 or b[2] >= fx1]
        if not interior or not outside:
            continue
        int_sigs = [dresden.ring_signature(mask[b[0]:b[1], b[2]:b[3]])
                    for b in interior]
        D = dresden.l1_matrix(int_sigs, [s for _, s in outside])
        for ii in range(len(interior)):
            jj = int(D[ii].argmin())
            dress_hits.append((int(D[ii][jj]), k, fb, interior[ii],
                               outside[jj][0]))
dress_hits.sort(key=lambda t: t[0])
check("figure-dressing hits collected", len(dress_hits) > 100)

# ===========================================================================
# §4 panels
# ===========================================================================
def crop(k, b, pad=3, scale=3):
    img = Image.open(page_path(k)).convert("RGB")
    c = img.crop((max(0, b[2] - pad), max(0, b[0] - pad),
                  b[3] + pad, b[1] + pad))
    return c.resize((c.width * scale, c.height * scale), Image.NEAREST)


# top recurrence clusters panel: 16 clusters x up to 8 members
CW, CHh = 84, 96
panel = Image.new("RGB", (CW * 8, CHh * 16), (16, 16, 16))
pd = ImageDraw.Draw(panel)
for row, c in enumerate(clusters[:16]):
    members = c[:8]
    pgs = cluster_pages(c)
    for col, ci in enumerate(members):
        im = crop(int(P[ci]), cell_box[ci])
        im.thumbnail((CW - 6, CHh - 22))
        panel.paste(im, (col * CW + 3, row * CHh + 18))
        pd.text((col * CW + 3, row * CHh + 4),
                "p%s" % page_label(int(P[ci])), fill=(255, 210, 40))
panel.save(os.path.join(DEMO, "dresden_recurrence_clusters.png"))

# dressing panel: top 10 pairs (interior element | matched glyph cell)
panel2 = Image.new("RGB", (240 * 2, 110 * 10), (16, 16, 16))
p2 = ImageDraw.Draw(panel2)
for row, (dist, k, fb, ib, cb) in enumerate(dress_hits[:10]):
    for col, bb in enumerate((ib, cb)):
        im = crop(k, bb)
        im.thumbnail((230, 86))
        panel2.paste(im, (col * 240 + 5, row * 110 + 20))
    p2.text((5, row * 110 + 4),
            "scan %d (p%s) figure@(%d,%d) elem->glyph L1=%d" % (
                k, page_label(k), fb[0], fb[2], dist),
            fill=(255, 210, 40))
panel2.save(os.path.join(DEMO, "dresden_dressing_pairs.png"))

# ===========================================================================
# §5 the catalog
# ===========================================================================
note("## D1 — Recurrence catalog (codex-wide, all-pairs)")
note("")
note("%d glyph cells; %d directed near-edges at the data-derived exact "
     "threshold L1 <= %d (lower quartile of cross-page nearest-neighbour "
     "distances); %d clusters of size >= 4." % (N, edges, note_edge,
                                                len(clusters)))
note("")
note("Top 16 clusters (size, page reach, sample coordinates) — crops in "
     "`demo/dresden_recurrence_clusters.png`, one cluster per row:")
note("")
note("| # | Size | Pages reached | Example (scan: y0,x0) |")
note("|---|---|---|---|")
for i, c in enumerate(clusters[:16]):
    pgs = cluster_pages(c)
    ex = c[0]
    note("| %d | %d | %s | scan %d: %d,%d |" % (
        i + 1, len(c),
        ",".join(page_label(p) for p in pgs[:12]) +
        ("…" if len(pgs) > 12 else ""),
        int(P[ex]), cell_box[ex][0], cell_box[ex][2]))
note("")
xnn = [(int(d), i) for i, d in enumerate(nn_cross)]
xnn.sort()
note("Strongest single cross-page code identities (top 12):")
note("")
note("| Query scan/page (y0,x0) | Match scan/page (y0,x0) | L1 |")
note("|---|---|---|")
for d, i in xnn[:12]:
    j = int(nn_cross_j[i])
    note("| %d/p%s (%d,%d) | %d/p%s (%d,%d) | %d |" % (
        int(P[i]), page_label(int(P[i])), cell_box[i][0], cell_box[i][2],
        int(P[j]), page_label(int(P[j])), cell_box[j][0], cell_box[j][2], d))
note("")

note("## D2 — Path gallery (all 78 pages)")
note("")
note("Overlays: `data/dresden/derived/paths/scanNN_path.jpg` (luminance-"
     "ordered tour, first 12 stations numbered). Pages ranked by tour "
     "coherence (permutation rank, lower = more ordered than chance). "
     "Caveat once: substrate brightness autocorrelation contributes to "
     "this signal on every page (DRESDEN_MACHINE.md §4); ranking is an "
     "exploratory pointer, not a design claim.")
note("")
ranks = sorted((pages[k]["res"]["path_test"][1], k) for k in range(1, 79)
               if pages[k]["res"]["path_test"][2])
note("Most-coherent pages: %s" % ", ".join(
    "scan %d (p%s, rank %d/999)" % (k, page_label(k), r)
    for r, k in ranks[:8]))
note("")

note("## D3 — Figure-dressing catalog")
note("")
nfig = sum(len(pages[k]["figures"]) for k in pages)
note("%d large-figure regions detected codex-wide; %d interior-element -> "
     "glyph-cell code matches collected. Top pairs (crops in "
     "`demo/dresden_dressing_pairs.png`):" % (nfig, len(dress_hits)))
note("")
note("| Scan/page | Figure (y0,x0) | Interior elem (y0,x0) | Matched glyph (y0,x0) | L1 |")
note("|---|---|---|---|---|")
for dist, k, fb, ib, cb in dress_hits[:15]:
    note("| %d/p%s | %d,%d | %d,%d | %d,%d | %d |" % (
        k, page_label(k), fb[0], fb[2], ib[0], ib[2], cb[0], cb[2], dist))
note("")

note("## D4 — Dot topology census (hollow vs solid)")
note("")
hollow_rank = sorted(((len(pages[k]["hollow"]), k) for k in pages),
                     reverse=True)
note("Codex totals: **%d hollow** (ring-topology) vs **%d solid** dots. "
     "Overlays for every page: `data/dresden/derived/dots/` (hollow = cyan, "
     "solid = orange). Pages with the largest hollow-dot populations — the "
     "candidate 'stitching/preparation' loci of the turtle-shell claim:" % (
         sum(len(pages[k]["hollow"]) for k in pages),
         sum(len(pages[k]["solid"]) for k in pages)))
note("")
note("| Scan | Page | Hollow | Solid |")
note("|---|---|---|---|")
for h, k in hollow_rank[:10]:
    note("| %d | %s | %d | %d |" % (k, page_label(k), h,
                                    len(pages[k]["solid"])))
note("")

note("## D5 — Tonal band maps")
note("")
note("Exact quantile-band structure maps for every page: "
     "`data/dresden/derived/bands/scanNN_bands.png` (5 bands, darkest -> "
     "brightest). These are the honest 'underlying layers' renders: each "
     "band is an exact order-statistic partition of the page's own luma.")
note("")

note("## D6 — Opportunity index (every page, no silent passes)")
note("")
note("| Scan | Page | Cells | Raw comps | Figures | Hollow | Solid | "
     "Path rank | Best cross-page L1 |")
note("|---|---|---|---|---|---|---|---|---|")
opp = []
for k in range(1, 79):
    pg = pages[k]
    cells_k = [i for i in range(N) if int(P[i]) == k]
    best_x = min((int(nn_cross[i]) for i in cells_k), default=-1)
    rk = pg["res"]["path_test"][1] if pg["res"]["path_test"][2] else -1
    opp.append((k, len(pg["res"]["boxes"]), len(pg["raw_boxes"]),
                len(pg["figures"]), len(pg["hollow"]), len(pg["solid"]),
                rk, best_x))
    note("| %d | %s | %d | %d | %d | %d | %d | %s | %s |" % (
        k, page_label(k), opp[-1][1], opp[-1][2], opp[-1][3], opp[-1][4],
        opp[-1][5], rk if rk >= 0 else "—", best_x if best_x >= 0 else "—"))
note("")

with open(os.path.join(DATA, "discovery_receipts.json"), "w") as f:
    f.write(ledger.export())

hdr = [
    "# Dresden discovery sweep — ranked catalogs, whole codex",
    "",
    "Run: `python3 analysis/dresden_discover.py` — deterministic, exact.",
    "Receipts: `data/dresden/discovery_receipts.json`. Companion verdicts:",
    "`docs/DRESDEN_MACHINE.md`. Mode: DISCOVERY (extract structure and rank",
    "instances; claim strength stays labeled — coordinates and distances are",
    "MEASURED, interpretations are HYPOTHESIS until they pass a gate).",
    "",
    "**%s exact checks, %d failures.**" % ("{:,}".format(R["checks"]),
                                           R["fails"]),
    "",
]
with open(os.path.join(DOCS, "DRESDEN_DISCOVERIES.md"), "w") as f:
    f.write("\n".join(hdr + CAT) + "\n")

print("\n".join(x for x in CAT if x.startswith("  FAIL")) or "no FAIL lines")
print("clusters:", len(clusters), "edge_T:", note_edge, "dress hits:",
      len(dress_hits))
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
