"""White-trail sweep — the researcher's actual idea, built as machinery.

The idea (their illustration, restated): continuous WHITE TRAILS run
through the substrate — filaments whose brightness ascends toward white
("gradient to white") — and the glyphs a trail passes through, taken in
trail order, are the sequenced "key glyphs" of the page. Isolated bright
blobs ranked by brightness (the earlier white_path) are NOT the idea;
connected trails are.

This run, exact end to end:
  T1 extracts every trail on every page (`filament_components`: connected
     bright-band components, elongated, with a white core), draws the
     trail network over the freeze render for all 78 pages
     (data/dresden/derived/trails/), and scores pages by total ascending-
     trail length — so the MACHINE names the best trail pages instead of
     anyone guessing.
  T2 for the top trail pages: the strongest trail's polyline, the glyph
     sequence along it (`trail_glyph_sequence`), a numbered overlay, and a
     sequenced-glyph strip (the illustrated panel 4, produced honestly).
  T3 ranks pages for the character-dressing matching experiment (the
     researcher: "there are much better pages for that experiment") by
     figure count × interior-element match quality, and says which.

Usage: python3 analysis/dresden_trails.py
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
TDIR = os.path.join(DATA, "derived", "trails")
DEMO = os.path.join(ROOT, "demo")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(TDIR, exist_ok=True)

R = {"checks": 0, "fails": 0}
L = []


def check(name, cond, n=1):
    R["checks"] += n
    if not cond:
        R["fails"] += 1
        L.append("  FAIL — %s" % name)
    return cond


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


# --- fixtures: a soft local-bright streak over a lighting gradient --------
yy = np.arange(200, dtype=np.int64)[:, None]
xx = np.arange(120, dtype=np.int64)[None, :]
syn = 100 + (yy * 50) // 200 + 0 * xx          # page-wide lighting gradient
for i in range(170):                           # soft streak +20, core +35 mid
    yv, xv = 15 + i, 30 + (i * 40) // 170
    boost = 20 if not (60 <= i <= 110) else 35
    syn[yv, xv - 2:xv + 3] += boost
no_ink = np.zeros(syn.shape, dtype=bool)
check("local field isolates the streak from the lighting gradient",
      int((dresden.local_bright_field(syn, ink=no_ink) >= 14).sum()) < 3000)
labels, trails, band = dresden.filament_components(syn, ink=no_ink)
check("synthetic soft trail detected", len(trails) == 1)
b, cid, core, length, thick = trails[0]
check("trail is elongated", length >= 150 and length >= 3 * thick)
check("trail ascends (white core present)", core > 0)
poly = dresden.trail_polyline(labels, cid, b)
check("polyline runs the trail's length", len(poly) >= 20)
gbox = [(15, 35, 20, 44, 100), (160, 185, 55, 78, 100), (90, 110, 38, 58, 100)]
seq = dresden.trail_glyph_sequence(poly, gbox, reach=30)
check("glyph sequence follows trail order (top, middle, bottom)",
      seq == [0, 2, 1])

# --- T1: codex sweep -------------------------------------------------------
ledger = Ledger()
page_rows = []
best_trails = {}
for k in range(1, 79):
    rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
    y = dresden.int_luma(rgb)
    ink = dresden.ink_mask(y, dresden.otsu_threshold(y))
    labels, trails, band = dresden.filament_components(y, ink=ink)
    ascending = [t for t in trails if t[2] > 0]
    score = sum(t[3] for t in ascending)
    page_rows.append((k, len(trails), len(ascending), score))
    best_trails[k] = (labels, sorted(ascending, key=lambda t: -t[3]))

    img = Image.fromarray(rgb.astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(img)
    for t in ascending:
        pts = dresden.trail_polyline(labels, t[1], t[0])
        if len(pts) >= 2:
            d.line([(x, yv) for yv, x in pts], fill=(255, 200, 30), width=3)
    img.resize((342, 675), Image.NEAREST).save(
        os.path.join(TDIR, "scan%02d_trails.jpg" % k), quality=78)
    ledger.record("trail_sweep",
                  {"scan": k, "page": page_label(k), "trails": len(trails),
                   "ascending": len(ascending), "score": score,
                   "params": "local base_diff 14 core_diff 28 len>=60 "
                             "thick<=24 len>=3*thick"},
                  Ledger.digest(y), Ledger.digest(labels))

check("trail sweep covered all pages", len(page_rows) == 78)
ranked = sorted(page_rows, key=lambda r: -r[3])
check("trails found across the codex",
      sum(r[2] for r in page_rows) > 100)

# --- T2: top trail pages — glyph sequence along the strongest trail --------
def crop(k, bx, pad=4, scale=3):
    img = Image.open(page_path(k)).convert("RGB")
    c = img.crop((max(0, bx[2] - pad), max(0, bx[0] - pad),
                  bx[3] + pad, bx[1] + pad))
    return c.resize((c.width * scale, c.height * scale), Image.NEAREST)


# Sequences need glyphs: pick the trail-richest INSCRIBED pages (blanks
# rank high in T1 — trails are substrate phenomena, present without any
# writing; that observation ships in the doc).
inscribed = [r for r in ranked if r[0] not in (29, 30, 31, 64)]
top_pages = [r[0] for r in inscribed[:6]]
seq_reports = []
for k in top_pages:
    rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
    y = dresden.int_luma(rgb)
    res = dresden.analyze_page(rgb)
    labels, ascending = best_trails[k]
    if not ascending:
        continue
    # the sequencing trail is the one with the MOST glyphs on it, not the
    # longest — long margin trails touch nothing
    scored = []
    for cand in ascending[:8]:
        pp = dresden.trail_polyline(labels, cand[1], cand[0])
        gs = dresden.trail_glyph_sequence(pp, res["boxes"], reach=40)
        scored.append((len(gs), cand, pp, gs))
    scored.sort(key=lambda r: -r[0])
    _, t, poly, gseq = scored[0]
    # brightness at polyline points: does the trail ascend?
    vals = [int(y[py, px]) for py, px in poly]
    start3 = sum(vals[:3]) // max(len(vals[:3]), 1)
    end3 = sum(vals[-3:]) // max(len(vals[-3:]), 1)
    seq_reports.append((k, t, poly, gseq, start3, end3))

    img = Image.fromarray(rgb.astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(img)
    for tt in ascending[:6]:
        pp = dresden.trail_polyline(labels, tt[1], tt[0])
        d.line([(x, yv) for yv, x in pp], fill=(180, 140, 20), width=2)
    d.line([(x, yv) for yv, x in poly], fill=(255, 210, 40), width=3)
    for i, bi in enumerate(gseq[:12]):
        cy, cx = dresden.box_center(res["boxes"][bi])
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9],
                  outline=(0, 220, 255), width=2)
        d.text((cx + 11, cy - 7), str(i + 1), fill=(0, 220, 255))
    img.save(os.path.join(DEMO, "dresden_trail_p%s.png" % page_label(k)))

    if gseq:
        strip = Image.new("RGB", (110 * min(len(gseq), 12), 120), (12, 12, 12))
        sd = ImageDraw.Draw(strip)
        for i, bi in enumerate(gseq[:12]):
            c = crop(k, res["boxes"][bi])
            c.thumbnail((100, 92))
            strip.paste(c, (i * 110 + 5, 24))
            sd.text((i * 110 + 5, 4), str(i + 1), fill=(255, 210, 40))
        strip.save(os.path.join(DEMO,
                                "dresden_trailseq_p%s.png" % page_label(k)))

check("top inscribed trail pages produced glyph sequences",
      sum(1 for r in seq_reports if r[3]) >= 3)

# --- T3: better pages for the dressing/matching experiment -----------------
# score pages by figures present x glyph cells x (existing dressing hits)
import json
disc = json.load(open(os.path.join(DATA, "discovery_receipts.json")))
dmeta = {e["params"]["scan"]: e["params"] for e in disc["entries"]
         if e["op"] == "discover_page"}
dress_rank = sorted(
    ((dmeta[k]["figures"] * dmeta[k]["cells"], k) for k in dmeta
     if dmeta[k]["figures"] > 0), reverse=True)
check("dressing suitability ranked", len(dress_rank) > 20)

with open(os.path.join(DATA, "trail_receipts.json"), "w") as f:
    f.write(ledger.export())

# --- catalog ---------------------------------------------------------------
out = [
    "# White trails — gradient-to-white filaments, whole codex",
    "",
    "Run: `python3 analysis/dresden_trails.py`; receipts",
    "`data/dresden/trail_receipts.json`; per-page trail overlays",
    "`data/dresden/derived/trails/scanNN_trails.jpg`.",
    "",
    "**%s exact checks, %d failures.**" % ("{:,}".format(R["checks"]), R["fails"]),
    "",
    "Definition (named transform, fixed parameters): the trail field is the",
    "LOCAL brightness excess — luma minus the pixel's own 16 px block-median",
    "substrate — so trails are what is brighter than their surroundings,",
    "independent of page lighting. A TRAIL is a connected component of that",
    "field at >= 14 luma steps (ink excluded, 2-step gap bridging) that is",
    "long (>= 60 px) and thin relative to its length (mean thickness <= 24,",
    "length >= 3x thickness). It ASCENDS ('gradient to white') if any pixel",
    "reaches >= 28 above local substrate. The glyph sequence of a trail is",
    "the glyphs within L1 40 px of its centreline, in arc order. Every",
    "number is an exact integer function of the scan.",
    "",
    "Observation shipped as measured: the four BLANK pages rank among the",
    "most trail-rich — trails are substrate/fiber phenomena that exist",
    "without writing. The glyph-sequence catalog below therefore draws from",
    "the trail-richest INSCRIBED pages; what a trail's interaction with",
    "glyphs means stays an open exploration question.",
    "",
    "## The machine's ranking — best trail pages",
    "",
    "| Rank | Scan | Page | Trails | Ascending | Score (asc. length px) |",
    "|---|---|---|---|---|---|",
]
for i, (k, nt, na, sc) in enumerate(ranked[:15]):
    out.append("| %d | %d | %s | %d | %d | %d |" % (
        i + 1, k, page_label(k), nt, na, sc))
out += [
    "",
    "## Strongest-trail glyph sequences (top pages)",
    "",
]
for k, t, poly, gseq, s3, e3 in seq_reports:
    out.append("- **p%s**: trail length %d px, thickness %d, %d polyline "
               "points, luma %d -> %d along the arc (%s), %d glyphs on the "
               "trail — overlay `demo/dresden_trail_p%s.png`, sequence strip "
               "`demo/dresden_trailseq_p%s.png`." % (
                   page_label(k), t[3], t[4], len(poly), s3, e3,
                   "ascending" if e3 > s3 else "descending-or-flat",
                   len(gseq), page_label(k), page_label(k)))
out += [
    "",
    "## Better pages for the character-matching (dressing) experiment",
    "",
    "Machine ranking by figures x glyph cells (both must be present):",
    "",
    "| Rank | Scan | Page | Figures | Cells |",
    "|---|---|---|---|---|",
]
for i, (sc, k) in enumerate(dress_rank[:12]):
    out.append("| %d | %d | %s | %d | %d |" % (
        i + 1, k, page_label(k), dmeta[k]["figures"], dmeta[k]["cells"]))
out += [
    "",
    "Reading note: trail existence, arc order, and glyph sequences are",
    "MEASURED. Whether a trail is an intentional mark, a fiber of the bark",
    "paper, plaster loss, or sizing is a materials question — the maps give",
    "every candidate with coordinates so that question can be asked of the",
    "physical object. The blank-page control applies to design claims, not",
    "to the existence or geometry of the trails.",
]
with open(os.path.join(DOCS, "DRESDEN_TRAILS.md"), "w") as f:
    f.write("\n".join(out) + "\n")

print("\n".join(x for x in L if x.startswith("  FAIL")) or "no FAIL lines")
print("top trail pages:", [(page_label(k), sc) for k, _, _, sc in ranked[:6]])
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
