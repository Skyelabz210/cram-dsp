"""Dot morphology — measured, never assumed.

The researcher's instruction: do NOT encode "hollow dots are stitching
holes" into the detector. Measure morphology, then test whether morphology
predicts anything.

So this run measures, for every small round mark in the codex:
  area · bbox aspect (milli) · fill ratio (milli) · hole count · ring
  thickness (milli) · nearest same-class neighbour · nearest other-class
  neighbour · local ink density (context) · page

and then asks three questions, all as MEASUREMENTS:
  Q1 do open (ring-topology) and filled marks separate on morphology, or
     are they one continuum split by a threshold?
  Q2 does the spacing pattern of open marks differ from filled marks
     (regular vs clustered) — measured as the spread of nearest-neighbour
     distances?
  Q3 which pages carry open-mark populations most similar to the
     researcher's located p69 column — an exact ranking, so the "same
     morphology recurs here" question is answered by the machine rather
     than by picking a page in advance.

No page is labeled "the turtle page" by this script; no mark is labeled a
stitching hole. Per docs/RULES_OF_EXPLORATION.md, results are MEASURED and
interpretation is OPEN.

Usage: python3 analysis/dresden_dots.py
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


def med(vals):
    if not vals:
        return 0
    s = sorted(vals)
    return s[(len(s) - 1) // 2]


def spread_milli(vals):
    """Exact dispersion: (p75 - p25) * 1000 // median. Regular spacing gives
    a small spread; clustered spacing a large one."""
    if len(vals) < 4:
        return 0
    s = sorted(vals)
    q1 = s[(len(s) - 1) * 25 // 100]
    q3 = s[(len(s) - 1) * 75 // 100]
    m = s[(len(s) - 1) // 2]
    return (1000 * (q3 - q1)) // max(m, 1)


# --- fixtures -------------------------------------------------------------
fx = np.zeros((40, 60), dtype=bool)
fx[6:15, 6:15] = True
fx[8:13, 8:13] = False          # ring: hole present
fx[6:15, 30:39] = True          # solid disc
labels, n = dresden.label_components(fx)
boxes = dresden.component_boxes(labels, n)
holes = []
for i, b in enumerate(boxes, start=1):
    comp = np.pad(labels[b[0]:b[1], b[2]:b[3]] == i, 1)
    holes.append(dresden.count_holes(comp))
check("morphology fixture: one ring, one solid", sorted(holes) == [0, 1])
check("fill ratio separates ring from solid",
      (1000 * boxes[0][4]) // 81 < (1000 * boxes[1][4]) // 81)

# --- measure every mark ----------------------------------------------------
ledger = Ledger()
records = []       # (scan, class, area, aspect, fill, thickness, cy, cx)
for k in range(1, 79):
    rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
    y = dresden.int_luma(rgb)
    ink = dresden.ink_mask(y, dresden.otsu_threshold(y))
    labels, n = dresden.label_components(ink)
    boxes = dresden.component_boxes(labels, n)
    H, W = y.shape
    gh, gw = H // 32, W // 32
    blk = ink[:gh * 32, :gw * 32].reshape(gh, 32, gw, 32)
    dens = (1000 * blk.sum(axis=(1, 3))) // 1024
    page_recs = []
    for i, b in enumerate(boxes, start=1):
        y0, y1, x0, x1, area = b
        if not (20 <= area <= 900):
            continue
        h, w = y1 - y0, x1 - x0
        aspect = (1000 * min(h, w)) // max(h, w)
        if aspect < 500:                       # not roundish
            continue
        fill = (1000 * area) // (h * w)
        comp = np.pad(labels[y0:y1, x0:x1] == i, 1)
        nh = dresden.count_holes(comp)
        # ring thickness proxy: filled area over bbox perimeter, exact
        thick = (1000 * area) // max(2 * (h + w), 1)
        cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
        d = int(dens[min(cy // 32, gh - 1), min(cx // 32, gw - 1)])
        page_recs.append((k, 1 if nh >= 1 else 0, area, aspect, fill,
                          thick, cy, cx, d))
    records.extend(page_recs)
    ledger.record("dot_morphology",
                  {"scan": k, "page": page_label(k), "marks": len(page_recs),
                   "open": sum(1 for r in page_recs if r[1] == 1)},
                  Ledger.digest(y), Ledger.digest(ink))

check("marks measured across the codex", len(records) > 10000)
opens = [r for r in records if r[1] == 1]
solids = [r for r in records if r[1] == 0]
check("both classes populated", len(opens) > 500 and len(solids) > 500)

# --- Q1 morphology separation ---------------------------------------------
q1 = []
for name, idx in (("area", 2), ("aspect", 3), ("fill", 4), ("thickness", 5)):
    mo = med([r[idx] for r in opens])
    ms = med([r[idx] for r in solids])
    # overlap: fraction of open marks inside the solid interquartile range
    ss = sorted(r[idx] for r in solids)
    lo = ss[(len(ss) - 1) * 25 // 100]
    hi = ss[(len(ss) - 1) * 75 // 100]
    inside = sum(1 for r in opens if lo <= r[idx] <= hi)
    q1.append((name, mo, ms, (1000 * inside) // max(len(opens), 1)))

# --- Q2 spacing regularity -------------------------------------------------
q2 = []
for k in range(1, 79):
    po = [(r[6], r[7]) for r in opens if r[0] == k]
    ps = [(r[6], r[7]) for r in solids if r[0] == k]
    for cls, pts in (("open", po), ("filled", ps)):
        if len(pts) < 6:
            continue
        nn = []
        for i, (ay, ax) in enumerate(pts):
            best = min((abs(ay - by) + abs(ax - bx)
                        for j, (by, bx) in enumerate(pts) if j != i),
                       default=0)
            nn.append(best)
        q2.append((k, cls, len(pts), med(nn), spread_milli(nn)))
open_sp = [r for r in q2 if r[1] == "open"]
solid_sp = [r for r in q2 if r[1] == "filled"]
check("spacing measured for both classes",
      len(open_sp) > 20 and len(solid_sp) > 20)

# --- Q3 which pages resemble the p69 column's open marks -------------------
REF = [r for r in opens if r[0] == 73 and 768 <= r[6] < 1350 and 64 <= r[7] < 274]
ref_prof = [med([r[i] for r in REF]) for i in (2, 3, 4, 5)] if REF else None
sim_rank = []
if ref_prof:
    for k in range(1, 79):
        po = [r for r in opens if r[0] == k]
        if len(po) < 8:
            continue
        prof = [med([r[i] for r in po]) for i in (2, 3, 4, 5)]
        dist = sum(abs(a - b) for a, b in zip(prof, ref_prof))
        sim_rank.append((dist, k, len(po), prof))
    sim_rank.sort()
check("reference profile built from the located p69 column", bool(ref_prof))

# --- panel: the two classes at scale, straight from the evidence mask ------
panel = Image.new("RGB", (12 * 76, 2 * 92 + 26), (14, 14, 14))
pd = ImageDraw.Draw(panel)
pd.text((6, 4), "open (ring-topology) marks — top row · filled marks — bottom row"
        "  (no semantic label applied)", fill=(255, 210, 40))
for row, cls in enumerate((opens, solids)):
    sample = [r for r in cls if r[0] == 73][:12] or cls[:12]
    for c, r in enumerate(sample):
        img = Image.open(page_path(r[0])).convert("RGB").crop(
            (r[7] - 14, r[6] - 14, r[7] + 14, r[6] + 14)).resize(
            (68, 68), Image.NEAREST)
        panel.paste(img, (c * 76 + 4, 26 + row * 92 + 4))
        pd.text((c * 76 + 4, 26 + row * 92 + 74),
                "p%s" % page_label(r[0]), fill=(140, 200, 255))
panel.save(os.path.join(DEMO, "dresden_dot_morphology.png"))

with open(os.path.join(DATA, "dot_receipts.json"), "w") as f:
    f.write(ledger.export())

# --- report ----------------------------------------------------------------
out = [
    "# Dot morphology — measured, unlabelled",
    "",
    "Run: `python3 analysis/dresden_dots.py`; receipts",
    "`data/dresden/dot_receipts.json`; panel `demo/dresden_dot_morphology.png`.",
    "",
    "**%s exact checks, %d failures.**" % ("{:,}".format(R["checks"]), R["fails"]),
    "",
    "Detector rule (stated, assumption-free): connected ink components with",
    "area 20–900 px and bbox aspect >= 500 milli are 'round marks'; a mark",
    "is OPEN if it encloses at least one 4-connected background component",
    "not touching its border, FILLED otherwise. Nothing is called a stitch",
    "hole, a numeral, or a decoration by this script.",
    "",
    "Population: **%d round marks** — %d open, %d filled." % (
        len(records), len(opens), len(solids)),
    "",
    "## Q1 — do the two classes separate on morphology?",
    "",
    "| Attribute | Open median | Filled median | Open marks inside the filled IQR (milli) |",
    "|---|---|---|---|",
]
for name, mo, ms, ov in q1:
    out.append("| %s | %d | %d | %d |" % (name, mo, ms, ov))
out += [
    "",
    "Reading: a high overlap figure means the classes are one continuum cut",
    "by the topology test; a low one means they are morphologically distinct",
    "populations. Both are reported without a verdict.",
    "",
    "## Q2 — spacing regularity per page and class",
    "",
    "Median nearest-neighbour distance and its dispersion "
    "((p75-p25)*1000/median; small = regular, large = clustered).",
    "",
    "| Class | Pages measured | Median NN distance (median over pages) | Median dispersion |",
    "|---|---|---|---|",
    "| open | %d | %d | %d |" % (len(open_sp), med([r[3] for r in open_sp]),
                                 med([r[4] for r in open_sp])),
    "| filled | %d | %d | %d |" % (len(solid_sp), med([r[3] for r in solid_sp]),
                                   med([r[4] for r in solid_sp])),
    "",
    "Per-page detail (open marks, most regular first):",
    "",
    "| Scan | Page | Open marks | Median NN | Dispersion |",
    "|---|---|---|---|---|",
]
for k, cls, n_, m_, sp in sorted(open_sp, key=lambda r: r[4])[:15]:
    out.append("| %d | %s | %d | %d | %d |" % (k, page_label(k), n_, m_, sp))
out += [
    "",
    "## Q3 — pages whose open-mark morphology most resembles the located p69 column",
    "",
    "Reference profile (median area / aspect / fill / thickness) taken from",
    "the %d open marks inside the located column on p69: %s." % (
        len(REF), ref_prof),
    "",
    "| Rank | Scan | Page | Open marks | L1 distance to reference | Profile |",
    "|---|---|---|---|---|---|",
]
for i, (dist, k, n_, prof) in enumerate(sim_rank[:15]):
    out.append("| %d | %d | %s | %d | %d | %s |" % (
        i + 1, k, page_label(k), n_, dist, prof))
out += [
    "",
    "Status: MEASURED. Whether open marks are preparation holes, a mark",
    "class with a scribal function, or a byproduct of pigment loss is not",
    "decided here — the morphology, spacing and recurrence figures are the",
    "material for that question (docs/RULES_OF_EXPLORATION.md).",
]
with open(os.path.join(DOCS, "DRESDEN_DOTS.md"), "w") as f:
    f.write("\n".join(out) + "\n")

print("\n".join(x for x in L if x.startswith("  FAIL")) or "no FAIL lines")
print("marks:", len(records), "open:", len(opens), "filled:", len(solids))
if sim_rank:
    print("top morphology matches to p69 column:",
          [(page_label(k), d) for d, k, _, _ in sim_rank[:5]])
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
