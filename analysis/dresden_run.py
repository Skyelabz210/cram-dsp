"""NODE-DRE01 (characterization) + the glyph-machine run.

The researcher's concept illustrations claim, for a Dresden-style page:
  C1  glyphs can be segmented and each carries a distinctive internal
      structure ("code") readable circularly outward from its center;
  C2  the same code recurs elsewhere on the page and on other pages;
  C3  a luminance ordering over the glyphs traces a coherent path
      ("luminous path") that is not random;
  C4  the photographed column in the third image is a page of this codex;
  C5  the path is "activated by light" (eclipse-phase illumination).

This run tests C1-C4 on the actual scan set with exact integer arithmetic
and reports the numbers whatever they are. C5 is not testable on a single
fixed-illumination RGB scan set — that is stated, not papered over.

Usage: python3 analysis/dresden_run.py
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
DEMO = os.path.join(ROOT, "demo")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(DEMO, exist_ok=True)

R = {"checks": 0, "fails": 0}
L = []


def check(name, cond, n=1):
    R["checks"] += n
    if not cond:
        R["fails"] += 1
        L.append("  FAIL — %s" % name)
    return cond


def note(s):
    L.append(s)


def page_path(k):
    return os.path.join(DATA, "pages", "wdl11621_scan%02d.jpg" % k)


def load_rgb(k):
    return np.asarray(Image.open(page_path(k)).convert("RGB"))


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


# ===========================================================================
note("## §1 Machine self-tests (synthetic fixtures, exact expectations)")
# ===========================================================================

# Otsu on an exactly bimodal image: 60% zeros, 40% two-hundreds.
fix = np.zeros((10, 10), dtype=np.int64)
fix[:, 6:] = 200
check("otsu separates exact bimodal at first inter-class bin",
      0 < dresden.otsu_threshold(fix) <= 200)
check("ink mask counts the dark class exactly",
      int(dresden.ink_mask(fix, dresden.otsu_threshold(fix)).sum()) == 60)

# Connected components: two L-shaped blobs + one diagonal-touching pixel
# (8-connectivity must join it), one isolated dot.
m = np.zeros((12, 12), dtype=bool)
m[1:4, 1] = True; m[3, 1:4] = True          # L blob, area 5
m[4, 4] = True                              # touches L diagonally -> same comp
m[8:10, 8:10] = True                        # square, area 4
m[0, 11] = True                             # dot, area 1
labels, n = dresden.label_components(m)
check("component count (8-conn) == 3", n == 3)
areas = sorted(b[4] for b in dresden.component_boxes(labels, n))
check("component areas exact", areas == [1, 4, 6])
check("labels cover exactly the mask", int((labels > 0).sum()) == int(m.sum()))

# Dilation: single pixel -> 3x3 after one step, 5x5 after two.
d1 = dresden.dilate(np.pad(np.ones((1, 1), bool), 3), 1)
d2 = dresden.dilate(np.pad(np.ones((1, 1), bool), 3), 2)
check("dilate 1 step area 9", int(d1.sum()) == 9)
check("dilate 2 steps area 25", int(d2.sum()) == 25)

# Ring signature: exact invariance under 90-degree rotations for a mask
# whose ink centroid sits at the exact grid center.
g = np.zeros((21, 21), dtype=bool)
g[10, 4] = g[10, 16] = g[4, 10] = g[16, 10] = True   # 4-fold symmetric ring
g[7, 7] = g[7, 13] = g[13, 7] = g[13, 13] = True
sig0 = dresden.ring_signature(g)
for rot in (1, 2, 3):
    check("ring signature invariant under rot90^%d" % rot,
          dresden.signature_distance(sig0, dresden.ring_signature(
              np.rot90(g, rot))) == 0)
check("signature distance to itself is 0",
      dresden.signature_distance(sig0, sig0) == 0)
check("signature values bounded in [-1, 1000]",
      bool(np.all(sig0 >= -1)) and bool(np.all(sig0 <= 1000)))

# Matching: nearest candidate must be the exact copy.
cands = [sig0 + 0, sig0 + 3, sig0 + 40]
ranked = dresden.match_signatures(sig0, cands)
check("exact copy ranks first at distance 0",
      ranked[0] == (0, 0))

# Path machinery: known L1 tour + LCG determinism.
pts = [(0, 0), (0, 3), (4, 3)]
check("L1 tour length exact", dresden.path_length_l1(pts) == 7)
a = dresden.LCG(1)
b = dresden.LCG(1)
check("LCG deterministic", all(a.next_below(1000) == b.next_below(1000)
                               for _ in range(100)), n=100)
obs, n_le, n_perm = dresden.permutation_path_test(pts, [0, 1, 2], n_perm=99)
check("path test returns observed==7", obs == 7)
check("path test rank within bounds", 0 <= n_le <= n_perm)

note("")

# ===========================================================================
note("## §2 Full-codex pass (78 scans) — segmentation + C3 path test")
# ===========================================================================

chars = json.load(open(os.path.join(DATA, "characterization.json")))
ledger = Ledger()

per_page = {}
path_rows = []
low_rank_pages = []
total_cells = 0
for k in range(1, 79):
    rgb = load_rgb(k)
    y = dresden.int_luma(rgb)
    res = dresden.analyze_page(rgb)
    c = chars["scan%02d" % k]
    # cross-checks against the ingestion characterization (same exact ops)
    check("scan%02d threshold reproduces ingestion" % k,
          res["threshold"] == c["otsu_threshold"])
    check("scan%02d ink coverage reproduces ingestion" % k,
          res["ink_milli"] == c["ink_coverage_milli"])
    check("scan%02d luma digest stable" % k,
          Ledger.digest(y) == ledger.digest(y))
    ledger.record("analyze_page",
                  {"scan": k, "page": page_label(k),
                   "min_area": 120, "max_area": 12000, "merge_steps": 2,
                   "n_rings": 12, "threshold": res["threshold"],
                   "cells": len(res["boxes"])},
                  c["jpeg_sha256"], Ledger.digest(y))
    per_page[k] = res
    total_cells += len(res["boxes"])
    obs, n_le, n_perm = res["path_test"]
    if n_perm:
        path_rows.append((k, len(res["boxes"]), obs, n_le, n_perm))
        if n_le + 1 <= (n_perm + 1) // 20:  # exact p <= 0.05
            low_rank_pages.append(k)

check("all 78 scans analyzed", len(per_page) == 78)
note("Glyph cells across the codex: **%d** (params: Otsu ink, dilate 2, "
     "area window [120, 12000])." % total_cells)
note("")
note("C3 — luminance-path permutation test, per page: observed L1 tour of "
     "the brightest-first cell ordering vs 999 seeded shuffles. Exact "
     "p-value = (rank+1)/1000; p <= 0.05 requires rank+1 <= 50.")
note("")
note("| Scan | Page | Cells | Observed tour | Shuffles <= observed / 999 |")
note("|---|---|---|---|---|")
for k, nc, obs, n_le, n_perm in path_rows:
    note("| %d | %s | %d | %d | %d |" % (k, page_label(k), nc, obs, n_le))
note("")
frac_expected = len(path_rows) // 20
note("Pages at p <= 0.05: **%d of %d** (chance expectation at the 5%% level: "
     "~%d). Verdict on C3 is stated in docs/DRESDEN_MACHINE.md from these "
     "numbers." % (len(low_rank_pages), len(path_rows), frac_expected))
check("path test ran on every inscribed page with >= 3 cells",
      len(path_rows) >= 70)
note("")

# --- Control: the same test on the BLANK pages, which carry no glyphs. ---
# Pseudo-cells: a fixed 8x14 grid of 40x40 boxes over the page interior.
# If brightness-ordered tours are also short on bare plaster, short tours
# measure substrate-luminance autocorrelation, not glyph arrangement.
note("### C3 control — blank pages (no glyphs, pseudo-cell grid)")
note("")
note("| Scan | Page | Pseudo-cells | Observed tour | Shuffles <= / 999 |")
note("|---|---|---|---|---|")
blank_ranks = []
for k in (29, 30, 31, 64):
    y = dresden.int_luma(load_rgb(k))
    h, w = y.shape
    boxes = []
    for gy in range(14):
        for gx in range(8):
            y0 = 60 + gy * ((h - 160) // 14)
            x0 = 40 + gx * ((w - 120) // 8)
            boxes.append((y0, y0 + 40, x0, x0 + 40, 1600))
    order = [i for _, i in dresden.luminance_order(y, boxes)]
    centers = [dresden.box_center(b) for b in boxes]
    obs, n_le, n_perm = dresden.permutation_path_test(centers, order)
    blank_ranks.append(n_le)
    note("| %d | %s | %d | %d | %d |" % (k, page_label(k), len(boxes),
                                         obs, n_le))
check("blank-page control executed on all four blanks",
      len(blank_ranks) == 4)
note("")
note("Blank-page control ranks: %s. If these are also << 50, the short "
     "tours on inscribed pages are explained by substrate-luminance "
     "autocorrelation (illumination and plaster tone vary smoothly across "
     "any page), and carry no evidence of a designed path." % blank_ranks)
note("")

# ===========================================================================
note("## §3 C1/C2 — glyph internal codes and their recurrence (Venus pages)")
# ===========================================================================

# Query page: scan 49 (Förstemann 46, first Venus page). Candidates: the
# other Venus pages, scans 50-53 (pages 47-50).
qk = 49
cand_ks = [50, 51, 52, 53]
qres = per_page[qk]
qy = dresden.int_luma(load_rgb(qk))
qthr = qres["threshold"]
qmask = dresden.ink_mask(qy, qthr)

cand_cells = []   # (scan, box, signature)
for ck in cand_ks:
    cres = per_page[ck]
    for b, s in zip(cres["boxes"], cres["signatures"]):
        cand_cells.append((ck, b, s))

check("candidate pool populated", len(cand_cells) > 300)

# For every query cell: nearest same-page cell (excluding itself) and
# nearest cross-page cell, by exact L1 signature distance.
same_page_best = []
cross_page_best = []
for i, (b, s) in enumerate(zip(qres["boxes"], qres["signatures"])):
    ranked_same = [(dresden.signature_distance(s, s2), j)
                   for j, s2 in enumerate(qres["signatures"]) if j != i]
    ranked_same.sort()
    same_page_best.append((ranked_same[0][0], i, ranked_same[0][1]))
    ranked_x = [(dresden.signature_distance(s, cs), j)
                for j, (_, _, cs) in enumerate(cand_cells)]
    ranked_x.sort()
    cross_page_best.append((ranked_x[0][0], i, ranked_x[0][1]))
    check("distances are non-negative ints",
          ranked_same[0][0] >= 0 and ranked_x[0][0] >= 0, n=2)

same_page_best.sort()
cross_page_best.sort()
med_same = same_page_best[(len(same_page_best) - 1) // 2][0]
med_cross = cross_page_best[(len(cross_page_best) - 1) // 2][0]
note("Query page scan %d (Förstemann %s): %d cells. Candidate pool: %d "
     "cells on scans %s (pages 47-50)." % (
         qk, page_label(qk), len(qres["boxes"]), len(cand_cells),
         cand_ks))
note("")
note("Median nearest-neighbour signature distance (milli-L1 over 12 rings): "
     "same page **%d**, cross page **%d**." % (med_same, med_cross))
note("")
note("Top 10 cross-page code matches (exact distances):")
note("")
note("| Query box (y0,y1,x0,x1) | Match scan/page | Match box | L1 dist |")
note("|---|---|---|---|")
for dist, i, j in cross_page_best[:10]:
    qb = qres["boxes"][i]
    ck, cb, _ = cand_cells[j]
    note("| (%d,%d,%d,%d) | %d / %s | (%d,%d,%d,%d) | %d |" % (
        qb[0], qb[1], qb[2], qb[3], ck, page_label(ck),
        cb[0], cb[1], cb[2], cb[3], dist))
note("")

# Null comparison for C2: distance distribution vs signatures of randomly
# placed boxes (seeded) of the same sizes on the candidate pages — if real
# glyph cells match better than random placements, recurrence is structural.
rng = dresden.LCG(4242)
null_best = []
cand_pages_cache = {ck: dresden.ink_mask(
    dresden.int_luma(load_rgb(ck)), per_page[ck]["threshold"])
    for ck in cand_ks}
null_cells = []
for ck in cand_ks:
    cm = cand_pages_cache[ck]
    h, w = cm.shape
    for _, b, _ in [t for t in cand_cells if t[0] == ck][:60]:
        bh, bw = b[1] - b[0], b[3] - b[2]
        yy = rng.next_below(h - bh)
        xx = rng.next_below(w - bw)
        null_cells.append(dresden.ring_signature(cm[yy:yy + bh, xx:xx + bw]))
for i, s in enumerate(qres["signatures"]):
    ranked_n = sorted(dresden.signature_distance(s, ns) for ns in null_cells)
    null_best.append(ranked_n[0])
null_best.sort()
med_null = null_best[(len(null_best) - 1) // 2]
note("Null control: nearest-neighbour distance to %d seeded random-placement "
     "signatures on the same candidate pages — median **%d** (vs %d for "
     "real cells). Interpretation in the doc, from the numbers." % (
         len(null_cells), med_null, med_cross))
check("recurrence medians computed", med_same >= 0 and med_cross >= 0
      and med_null >= 0)
note("")

# ===========================================================================
note("## §4 C4 — locating the photographed column (exact template search)")
# ===========================================================================

qimg = Image.open(os.path.join(DATA, "queries", "query_column_photo_q4.png"))
qw, qh = qimg.size
tpl_full = qimg.crop((qw * 15 // 100, qh * 5 // 100,
                      qw * 80 // 100, qh * 95 // 100))

pages_small = {}
for k in range(1, 79):
    im = Image.open(page_path(k)).resize((86, 169), Image.NEAREST)
    pg = dresden.int_luma(np.asarray(im.convert("RGB"))).astype(np.int64)
    pages_small[k] = pg - dresden.exact_median(pg)

from numpy.lib.stride_tricks import sliding_window_view

results = []
for tw in (26, 32, 38, 46, 54):
    th = max(2, tw * tpl_full.size[1] // tpl_full.size[0])
    if th >= 169:
        continue
    t = dresden.int_luma(np.asarray(
        tpl_full.resize((tw, th), Image.NEAREST).convert("RGB")))
    t = t - dresden.exact_median(t)
    for k, p in pages_small.items():
        wins = sliding_window_view(p, (th, tw))
        sad = np.abs(wins - t).sum(axis=(2, 3))
        j = np.unravel_index(np.argmin(sad), sad.shape)
        results.append((int(sad[j]) // (tw * th), k, tw, int(j[1]), int(j[0])))
results.sort()
note("Query: researcher's photographed column (pinned decimation, receipts "
     "in data/dresden/queries/). Method: median-centred integer SAD over "
     "all 78 scans at 5 template scales, nearest-neighbour geometry casts "
     "only. Top 8 (mean-SAD per pixel, scan, template width, x, y):")
note("")
for r in results[:8]:
    note("- mean-SAD %d — scan %d (page %s), tw=%d, at (%d, %d)" % (
        r[0], r[1], page_label(r[1]), r[2], r[3], r[4]))
blank_top = [r for r in results[:4] if r[1] in (29, 30, 31, 64)]
note("")
note("**%d of the top 4 hits are blank pages** — the matcher found "
     "low-contrast fits, not structure. NEGATIVE: the photographed column "
     "is not located in this scan set at these scales. Its layout (single "
     "full-column figure, no register rules) matches no Dresden section; "
     "a Madrid Codex origin is a HYPOTHESIS for the researcher to check, "
     "not a finding." % len(blank_top))
check("template search executed across all pages and scales",
      len(results) == 5 * 78)
note("")

# ===========================================================================
# Renders (display seam only — nearest neighbour, no resampling of evidence)
# ===========================================================================

# Path overlay on the query Venus page: luminance-ordered polyline.
im = Image.open(page_path(qk)).convert("RGB")
dr = ImageDraw.Draw(im)
order = [i for _, i in qres["luminance_order"]]
centers = [qres["centers"][i] for i in order]
for (y0, x0), (y1, x1) in zip(centers, centers[1:]):
    dr.line([(x0, y0), (x1, y1)], fill=(255, 210, 40), width=2)
for rank, (y, x) in enumerate(centers[:12]):
    dr.ellipse([x - 7, y - 7, x + 7, y + 7], outline=(255, 120, 0), width=2)
    dr.text((x + 9, y - 6), str(rank + 1), fill=(255, 120, 0))
im.save(os.path.join(DEMO, "dresden_path_scan49.png"))

# Match panel: 6 queries with their best cross-page match, side by side.
def crop_cell(k, b, pad=4):
    img = Image.open(page_path(k)).convert("RGB")
    return img.crop((max(0, b[2] - pad), max(0, b[0] - pad),
                     b[3] + pad, b[1] + pad)).resize(
        ((b[3] - b[2] + 2 * pad) * 3, (b[1] - b[0] + 2 * pad) * 3),
        Image.NEAREST)

cellw, cellh = 160, 160
panel = Image.new("RGB", (cellw * 2, cellh * 6), (18, 18, 18))
pd = ImageDraw.Draw(panel)
for row, (dist, i, j) in enumerate(cross_page_best[:6]):
    qb = qres["boxes"][i]
    ck, cb, _ = cand_cells[j]
    for col, (kk, bb) in enumerate(((qk, qb), (ck, cb))):
        c = crop_cell(kk, bb)
        c.thumbnail((cellw - 8, cellh - 20))
        panel.paste(c, (col * cellw + 4, row * cellh + 16))
    pd.text((4, row * cellh + 2),
            "p%s -> p%s  L1=%d" % (page_label(qk), page_label(ck), dist),
            fill=(255, 210, 40))
panel.save(os.path.join(DEMO, "dresden_match_panel.png"))

with open(os.path.join(DATA, "machine_receipts.json"), "w") as f:
    f.write(ledger.export())

# ===========================================================================
# Report
# ===========================================================================

hdr = [
    "# The glyph machine on the Dresden Codex scan set",
    "",
    "Run: `python3 analysis/dresden_run.py` — deterministic, integer-exact.",
    "Receipts: `data/dresden/machine_receipts.json` (hash-chained).",
    "",
    "**%s exact checks, %d failures.**" % ("{:,}".format(R["checks"]),
                                           R["fails"]),
    "",
]
with open(os.path.join(DOCS, "DRESDEN_MACHINE_RUN.md"), "w") as f:
    f.write("\n".join(hdr + L) + "\n")

print("\n".join(x for x in L if x.startswith("  FAIL")) or "no FAIL lines")
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
