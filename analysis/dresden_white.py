"""The white-gradient machinery — the illustrations' actual pipeline, built.

The researcher's illustrations depict, in order: (2) a highlights-frozen
render exposing white patterns, (3) a brightest-first numbered path through
white structures ("path of luminance, 1 = brightest"), (7) layered bright
structure. The first machine pass approximated this with glyph-cell median
luma — not what the illustrations show. This run builds the real thing,
exact end to end:

  highlight_freeze  exact order-statistic contrast window (lo/hi milli),
                    integer scaling — the "highlights & contrast frozen" view
  white_nodes       top-quantile bright components (the white fiber/pigment
                    structures), area-filtered, brightest-first
  white_path        the numbered 1..12 brightest-node sequence + exact tour

Demonstrated FIRST on the located p69 column (the researcher's own example,
found at scan 73 (64,768) by analysis/dresden_locate.py), then swept over
every page — overlays for all 78 in data/dresden/derived/white/, catalog in
docs/DRESDEN_WHITE.md. Discovery framing: sequences and coordinates are
MEASURED; what they mean is the researcher's exploration surface.

Usage: python3 analysis/dresden_white.py
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
WDIR = os.path.join(DATA, "derived", "white")
DEMO = os.path.join(ROOT, "demo")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(WDIR, exist_ok=True)

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


def load_luma(k):
    return dresden.int_luma(np.asarray(Image.open(page_path(k)).convert("RGB")))


# --- fixtures -------------------------------------------------------------
ramp = np.arange(256, dtype=np.int64).reshape(16, 16)
check("order_stat exact on ramp",
      dresden.order_stat(ramp, 0) == 0 and dresden.order_stat(ramp, 1000) == 255
      and dresden.order_stat(ramp, 500) == 127)
fz, lo, hi = dresden.highlight_freeze(ramp, 500, 900)
check("freeze endpoints exact", int(fz.min()) == 0 and int(fz.max()) == 255)
check("freeze monotone", bool(np.all(np.diff(fz.ravel()) >= 0)))
syn = np.zeros((40, 40), dtype=np.int64)
syn[5:9, 5:9] = 250      # bright blob A (peak 250)
syn[25:28, 30:33] = 240  # bright blob B
thr, nodes = dresden.white_nodes(syn, top_milli=985, min_area=4)
check("white nodes found and ordered brightest-first",
      len(nodes) == 2 and nodes[0][3] == 250 and nodes[1][3] == 240)
seq, tour = dresden.white_path(nodes)
check("white path exact tour",
      tour == abs(nodes[0][0] - nodes[1][0]) + abs(nodes[0][1] - nodes[1][1]))

# --- the researcher's column first (p69, located) -------------------------
TOP_MILLI, MIN_A, MAX_A = 965, 12, 4000
y73 = load_luma(73)
col = y73[768:1350, 64:274]
fz, lo, hi = dresden.highlight_freeze(col)
thr, nodes = dresden.white_nodes(col, TOP_MILLI, MIN_A, MAX_A)
seq, tour = dresden.white_path(nodes, min_sep=40)


def freeze_rgb(fzarr):
    g = fzarr.astype(np.uint8)
    return np.stack([g, g, g], axis=2)


def draw_path(img, nodes, seq, scale=1):
    d = ImageDraw.Draw(img)
    pts = [(x * scale, y * scale) for (y, x) in seq]
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=(255, 200, 30), width=2)
    for i, (x, y) in enumerate(pts):
        d.ellipse([x - 8, y - 8, x + 8, y + 8], outline=(0, 220, 255), width=2)
        d.text((x + 10, y - 7), str(i + 1), fill=(0, 220, 255))
    return img


orig = Image.open(page_path(73)).convert("RGB").crop((64, 768, 274, 1350))
S = 3
panel = Image.new("RGB", (210 * S * 3 + 40, 582 * S + 40), (10, 10, 10))
pd = ImageDraw.Draw(panel)
o3 = orig.resize((210 * S, 582 * S), Image.NEAREST)
f3 = Image.fromarray(freeze_rgb(fz)).resize((210 * S, 582 * S), Image.NEAREST)
p3 = draw_path(f3.copy(), nodes, seq, scale=S)
for i, (im, ttl) in enumerate([(o3, "1. original (p69 column, located)"),
                               (f3, "2. highlights & contrast frozen (exact %d..%d)" % (lo, hi)),
                               (p3, "3. white path, 1 = brightest (thr %d, %d nodes)" % (thr, len(nodes)))]):
    panel.paste(im, (10 + i * (210 * S + 10), 30))
    pd.text((10 + i * (210 * S + 10), 8), ttl, fill=(255, 210, 40))
panel.save(os.path.join(DEMO, "dresden_white_p69.png"))
L.append("p69 column (the researcher's example): freeze window [%d..%d], "
         "white threshold %d, %d white nodes, 12-node tour %d px (L1). "
         "Panel: demo/dresden_white_p69.png" % (lo, hi, thr, len(nodes), tour))
check("p69 column yields a white-node sequence", len(nodes) >= 12)

# --- codex-wide sweep -----------------------------------------------------
ledger = Ledger()
rows = []
for k in range(1, 79):
    y = load_luma(k)
    fzp, lop, hip = dresden.highlight_freeze(y)
    thrp, nodesp = dresden.white_nodes(y, TOP_MILLI, MIN_A, MAX_A)
    seqp, tourp = dresden.white_path(nodesp, min_sep=60)
    fimg = Image.fromarray(freeze_rgb(fzp))
    fimg.resize((342, 675), Image.NEAREST).save(
        os.path.join(WDIR, "scan%02d_freeze.jpg" % k), quality=78)
    overlay = draw_path(fimg, nodesp, seqp)
    overlay.resize((342, 675), Image.NEAREST).save(
        os.path.join(WDIR, "scan%02d_whitepath.jpg" % k), quality=78)
    rows.append((k, lop, hip, thrp, len(nodesp), tourp,
                 seqp[:12]))
    ledger.record("white_sweep",
                  {"scan": k, "page": page_label(k), "freeze": [lop, hip],
                   "white_thr": thrp, "top_milli": TOP_MILLI,
                   "nodes": len(nodesp), "tour12_l1": tourp},
                  Ledger.digest(y), Ledger.digest(fzp))
check("white sweep covered all 78 pages", len(rows) == 78)

with open(os.path.join(DATA, "white_receipts.json"), "w") as f:
    f.write(ledger.export())

# --- catalog --------------------------------------------------------------
out = [
    "# White-gradient sweep — highlight-freeze + white-node paths, whole codex",
    "",
    "Run: `python3 analysis/dresden_white.py` — deterministic, exact.",
    "Receipts: `data/dresden/white_receipts.json`.",
    "Overlays for every page: `data/dresden/derived/white/scanNN_freeze.jpg`",
    "and `scanNN_whitepath.jpg` (numbered 1..12, brightest first).",
    "",
    "**%s exact checks, %d failures.**" % ("{:,}".format(R["checks"]), R["fails"]),
    "",
    "Named transforms, fixed parameters: freeze window = exact order",
    "statistics at 500/970 milli of each page's own luma; white threshold =",
    "order statistic at %d milli; nodes = 8-conn components of the white" % TOP_MILLI,
    "mask, area window [%d, %d]; sequence = brightest-first by exact median" % (MIN_A, MAX_A),
    "(ties: peak, then reading order); tour = exact L1. Every value is an",
    "exact function of the scan integers — nothing is enhanced or synthesized.",
    "",
    "The researcher's p69 column is the worked example:",
    "`demo/dresden_white_p69.png` (original | frozen | numbered white path).",
    "",
    "## Per-page white-node table",
    "",
    "| Scan | Page | Freeze lo..hi | White thr | Nodes | 12-node tour (L1 px) | First 5 stations (y,x) |",
    "|---|---|---|---|---|---|---|",
]
for k, lop, hip, thrp, nn, tourp, seq5 in rows:
    out.append("| %d | %s | %d..%d | %d | %d | %d | %s |" % (
        k, page_label(k), lop, hip, thrp, nn, tourp,
        " ".join("(%d,%d)" % (y, x) for y, x in seq5[:5])))
out += [
    "",
    "Reading note (discovery framing): node sequences are exact measurements",
    "of where each page's brightest structures sit and how a brightest-first",
    "walk orders them. Cross-page comparison of station layouts, and overlap",
    "of stations with glyph cells vs substrate, are the open exploration",
    "surfaces; the blank-page autocorrelation caveat from DRESDEN_MACHINE.md",
    "applies to any claim that a tour is *designed*, and constrains, not",
    "forbids, the exploration.",
]
with open(os.path.join(DOCS, "DRESDEN_WHITE.md"), "w") as f:
    f.write("\n".join(out) + "\n")

print("\n".join(x for x in L if x.startswith("  FAIL")) or "no FAIL lines")
print("\n".join(x for x in L if not x.startswith("  FAIL")))
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
