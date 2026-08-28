"""White-field v2 — evidence node records, 3-path agreement, controls.

Implements the researcher's production spec for the white-gradient stage:

  N1 every white node is an EVIDENCE RECORD (center, area, peak, median,
     local contrast, gradient magnitude + direction, chroma spread,
     combined integer score) — global brightness alone can no longer
     masquerade as the white pattern. Records ship as JSON per page
     (data/dresden/derived/nodes/), the raw material for the evidence
     overlay.
  N2 three independently constructed orderings per page — brightness
     ranking, spatial-adjacency chain, gradient-flow chain — with exact
     pairwise agreement in milli. A single-algorithm ordering is a
     visualization; agreement across constructions is the evidence
     (RULES_OF_EXPLORATION.md rule 6).
  N3 figure-region vs plain-substrate comparison, same algorithm both
     sides: node density, contrast, gradient-direction coherence, spacing.
     The comparison is reported, not verdicted.
  N4 cross-page trail continuity: trails ending at a page's edge matched
     against trails starting at the facing edge of the next scan —
     the researcher's continuous-strip prediction, now measurable.
     (Modern scan adjacency ≠ original order; both caveats stated.)

Usage: python3 analysis/dresden_whitefield.py
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
NDIR = os.path.join(DATA, "derived", "nodes")
DEMO = os.path.join(ROOT, "demo")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(NDIR, exist_ok=True)

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


FIELDS = ["cy", "cx", "area", "peak", "median", "local_contrast",
          "grad_mag", "grad_oct", "chroma_spread", "score"]

# --- fixtures -------------------------------------------------------------
fx = np.full((60, 60, 3), 140, dtype=np.uint8)
fx[10:16, 10:16] = 250                       # neutral bright node
fx[40:46, 40:46] = (250, 210, 160)           # warm bright node (paper-like)
thr, recs = dresden.node_records(fx, top_milli=985, min_area=6)
check("node records found both nodes", len(recs) == 2)
neutral = [r for r in recs if r[8] <= 5]
warm = [r for r in recs if r[8] > 5]
check("chroma spread separates neutral white from warm paper",
      len(neutral) == 1 and len(warm) == 1)
check("neutral node outscores equally-bright warm node",
      neutral[0][9] > warm[0][9])
oa = dresden.ordering_agreement_milli([0, 1, 2, 3], [0, 1, 2, 3])
ob = dresden.ordering_agreement_milli([0, 1, 2, 3], [3, 2, 1, 0])
check("agreement metric exact at both extremes", oa == 1000 and ob == 0)

# --- N1+N2 codex sweep ----------------------------------------------------
ledger = Ledger()
rows = []
for k in range(1, 79):
    rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
    thr, recs = dresden.node_records(rgb)
    with open(os.path.join(NDIR, "scan%02d_nodes.json" % k), "w") as f:
        json.dump({"scan": k, "page": page_label(k), "white_thr": int(thr),
                   "fields": FIELDS,
                   "nodes": [[int(v) for v in r] for r in recs]},
                  f, separators=(",", ":"))
    A = dresden.order_brightness(recs)
    B = dresden.order_spatial(recs)
    C = dresden.order_gradient_flow(recs)
    ab = dresden.ordering_agreement_milli(A, B)
    ac = dresden.ordering_agreement_milli(A, C)
    bc = dresden.ordering_agreement_milli(B, C)
    rows.append((k, len(recs), ab, ac, bc))
    ledger.record("whitefield_v2",
                  {"scan": k, "page": page_label(k), "nodes": len(recs),
                   "agreement_ab": ab, "agreement_ac": ac,
                   "agreement_bc": bc},
                  Ledger.digest(dresden.int_luma(rgb)), "nodes-json")
check("node records for all pages", len(rows) == 78)

# --- p69 column: three paths drawn together -------------------------------
rgb73 = np.asarray(Image.open(page_path(73)).convert("RGB"))
col = rgb73[768:1350, 64:274]
thr_c, recs_c = dresden.node_records(col)
A = dresden.order_brightness(recs_c)
B = dresden.order_spatial(recs_c)
C = dresden.order_gradient_flow(recs_c)
S = 3
img = Image.fromarray(col).resize((210 * S, 582 * S), Image.NEAREST)
d = ImageDraw.Draw(img)
COLORS = {"A brightness": (255, 200, 30), "B spatial": (0, 220, 255),
          "C gradient-flow": (255, 90, 200)}
for (name, color), seq in zip(COLORS.items(), (A, B, C)):
    pts = [(recs_c[i][1] * S, recs_c[i][0] * S) for i in seq]
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=color, width=2)
legend = Image.new("RGB", (img.width, img.height + 26), (12, 12, 12))
legend.paste(img, (0, 26))
ld = ImageDraw.Draw(legend)
x = 6
for name, color in COLORS.items():
    ld.text((x, 6), name, fill=color)
    x += 170
ld.text((x, 6), "agree AB %d AC %d BC %d (milli)" % (
    dresden.ordering_agreement_milli(A, B),
    dresden.ordering_agreement_milli(A, C),
    dresden.ordering_agreement_milli(B, C)), fill=(232, 223, 206))
legend.save(os.path.join(DEMO, "dresden_threepaths_p69.png"))

# --- N3 figure vs substrate -----------------------------------------------
def region_stats(recs, sel):
    rs = [r for r in recs if sel(r)]
    if not rs:
        return None
    n = len(rs)
    contrast = sorted(r[5] for r in rs)[(n - 1) // 2]
    octs = [0] * 8
    for r in rs:
        octs[r[7]] += 1
    coher = (1000 * max(octs)) // n
    sp = []
    for r in rs:
        ds = [abs(r[0] - q[0]) + abs(r[1] - q[1]) for q in rs if q is not r]
        if ds:
            sp.append(min(ds))
    spacing = sorted(sp)[(len(sp) - 1) // 2] if sp else 0
    return n, contrast, coher, spacing


fig_sub_rows = []
for k in (73, 69, 49, 26, 4):        # pointed page + top dressing pages
    rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
    y = dresden.int_luma(rgb)
    ink = dresden.ink_mask(y, dresden.otsu_threshold(y))
    # Written zone vs bare substrate by INK DENSITY, not by a figure
    # detector: 32 px blocks, "written" = ink fraction >= 100 milli,
    # "bare" = no ink at all in the block or its 8 neighbours. (The earlier
    # figure detector merged the whole page into one component after
    # dilation — every node landed "inside a figure" and the comparison was
    # vacuous. Receipt kept here rather than silently swapped.)
    H, W = y.shape
    gh, gw = H // 32, W // 32
    blk = ink[:gh * 32, :gw * 32].reshape(gh, 32, gw, 32)
    dens = (1000 * blk.sum(axis=(1, 3))) // 1024
    # Data-derived cut, not a magic constant: the global Otsu ink mask is
    # permissive on aged plaster (median block reads ~375 milli "ink"), so
    # absolute thresholds fail. Written = top-quartile density blocks,
    # bare = bottom-decile blocks, by exact order statistics of this page.
    hi = dresden.order_stat(dens, 750)
    lo = dresden.order_stat(dens, 100)
    written = dens >= hi
    bare = dens <= lo
    _, recs = dresden.node_records(rgb)

    def blk_of(r):
        return min(r[0] // 32, gh - 1), min(r[1] // 32, gw - 1)

    fs = region_stats(recs, lambda r: written[blk_of(r)])
    ss = region_stats(recs, lambda r: bare[blk_of(r)])
    fig_sub_rows.append((k, fs, ss))
check("written-vs-bare comparison computed",
      sum(1 for _, fs, ss in fig_sub_rows if fs and ss) >= 3)

# --- N4 cross-page trail continuity ---------------------------------------
edge_trails = {}
for k in range(1, 79):
    y = dresden.int_luma(np.asarray(Image.open(page_path(k)).convert("RGB")))
    ink = dresden.ink_mask(y, dresden.otsu_threshold(y))
    _, trails, _ = dresden.filament_components(y, ink=ink)
    right = [t[0] for t in trails if t[0][3] >= 684 - 24]
    left = [t[0] for t in trails if t[0][2] <= 24]
    edge_trails[k] = (left, right)

cont_rows = []
total_align = 0
for k in range(1, 78):
    right = edge_trails[k][1]
    left = edge_trails[k + 1][0]
    align = 0
    for rb in right:
        for lb in left:
            if rb[0] <= lb[1] and lb[0] <= rb[1]:   # y-interval overlap
                align += 1
                break
    if right or left:
        cont_rows.append((k, len(right), len(left), align))
    total_align += align
check("continuity scan completed", len(cont_rows) > 10)

with open(os.path.join(DATA, "whitefield_receipts.json"), "w") as f:
    f.write(ledger.export())

# --- report ----------------------------------------------------------------
out = [
    "# White-field v2 — evidence nodes, path agreement, controls, continuity",
    "",
    "Run: `python3 analysis/dresden_whitefield.py`; receipts",
    "`data/dresden/whitefield_receipts.json`; per-page node records",
    "`data/dresden/derived/nodes/scanNN_nodes.json` (fields: %s)." % ", ".join(FIELDS),
    "",
    "**%s exact checks, %d failures.**" % ("{:,}".format(R["checks"]), R["fails"]),
    "",
    "Status vocabulary per docs/RULES_OF_EXPLORATION.md: everything below is",
    "MEASURED; interpretation is OPEN. These orderings are constructions —",
    "agreement between independent constructions is the signal to read.",
    "",
    "## N2 — three-path agreement per page (milli; A=brightness, B=spatial, C=gradient-flow)",
    "",
    "| Scan | Page | Nodes | A~B | A~C | B~C |",
    "|---|---|---|---|---|---|",
]
for k, n, ab, ac, bc in rows:
    out.append("| %d | %s | %d | %d | %d | %d |" % (k, page_label(k), n, ab, ac, bc))
hi = sorted(rows, key=lambda r: -(min(r[2], r[3], r[4])))[:8]
out += [
    "",
    "Pages where all three constructions agree most (min pairwise "
    "agreement): " + ", ".join("p%s (%d)" % (page_label(k), min(ab, ac, bc))
                               for k, n, ab, ac, bc in hi) + ".",
    "",
    "Worked example: `demo/dresden_threepaths_p69.png` — the three paths",
    "drawn together on the researcher's p69 column.",
    "",
    "## N3 — written zone vs bare substrate (same algorithm both sides)",
    "",
    "| Scan | Page | Written: n / contrast / dir-coherence / spacing | Bare substrate: n / contrast / dir-coherence / spacing |",
    "|---|---|---|---|",
]
for k, fs, ss in fig_sub_rows:
    f1 = "%d / %d / %d / %d" % fs if fs else "—"
    s1 = "%d / %d / %d / %d" % ss if ss else "—"
    out.append("| %d | %s | %s | %s |" % (k, page_label(k), f1, s1))
out += [
    "",
    "## N4 — cross-page trail continuity (continuous-strip prediction)",
    "",
    "Facing-edge trail alignments between consecutive scans (y-overlap of",
    "edge-touching trails; modern scan adjacency, which is NOT asserted to",
    "be original order): **%d alignments** across %d scan pairs with edge "
    "trails. Pairs with alignments:" % (total_align, len(cont_rows)),
    "",
    "| Scan pair | Right-edge trails | Left-edge trails | Aligned |",
    "|---|---|---|---|",
]
for k, nr, nl, al in cont_rows:
    if al:
        out.append("| %d–%d | %d | %d | %d |" % (k, k + 1, nr, nl, al))
with open(os.path.join(DOCS, "DRESDEN_WHITEFIELD.md"), "w") as f:
    f.write("\n".join(out) + "\n")

print("\n".join(x for x in L if x.startswith("  FAIL")) or "no FAIL lines")
print("total edge alignments:", total_align)
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
