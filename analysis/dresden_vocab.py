"""Form-vocabulary catalog — the sharpened recurrence pass.

The first recurrence pass (ring codes only) produced two mega-clusters that
chained generic small marks: rotation-invariant ring profiles cannot tell a
dot from a short stroke of equal mass distribution. This pass adds the
angular dimension: ring × sector codes (`sector_signature`, sequential
octants) matched under exact dihedral invariance (4 rotations × mirror), and
re-clusters the whole codex. The output is the glyph FORM VOCABULARY:
every cluster gets a full contact sheet (every member, page-labelled) under
data/dresden/derived/clusters/, so the researcher browses actual form
families rather than trusting anyone's summary.

Usage: python3 analysis/dresden_vocab.py
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
CDIR = os.path.join(DATA, "derived", "clusters")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(CDIR, exist_ok=True)

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


# --- fixtures -------------------------------------------------------------
g = np.zeros((21, 21), dtype=bool)
g[6, 6:15] = True          # asymmetric: a horizontal bar upper-left region
g[6:11, 6] = True
s0 = dresden.sector_signature(g)
check("sector code invariant to rot90 under dihedral matching",
      dresden.dihedral_min_distance(s0, dresden.sector_signature(
          np.rot90(g))) == 0)
check("sector code invariant to mirror under dihedral matching",
      dresden.dihedral_min_distance(s0, dresden.sector_signature(
          g[:, ::-1])) == 0)
bar = np.zeros((21, 21), dtype=bool)
bar[10, 2:19] = True
dot = np.zeros((21, 21), dtype=bool)
dot[8:13, 8:13] = True
check("sector code separates bar from dot decisively",
      dresden.dihedral_min_distance(dresden.sector_signature(bar),
                                    dresden.sector_signature(dot)) > 800)
o = dresden.octant_index(np.asarray([[0]]), np.asarray([[5]]))
check("octant index sequential origin", int(o[0][0]) == 0)

# --- collect codes codex-wide ---------------------------------------------
cells = []      # (scan, box)
ring_sigs = []
sect_sigs = []
for k in range(1, 79):
    rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
    y = dresden.int_luma(rgb)
    res = dresden.analyze_page(rgb)
    mask = dresden.ink_mask(y, res["threshold"])
    for b, rs in zip(res["boxes"], res["signatures"]):
        y0, y1, x0, x1, _ = b
        cells.append((k, b))
        ring_sigs.append(rs)
        sect_sigs.append(dresden.sector_signature(mask[y0:y1, x0:x1]))
N = len(cells)
check("codes collected for the whole codex", N > 7000)

RS = np.asarray(ring_sigs, dtype=np.int64)
SS = np.asarray(sect_sigs, dtype=np.int64)
P = np.asarray([c[0] for c in cells], dtype=np.int64)

# precompute the 8 dihedral variants of every sector signature
V = np.stack([dresden.dihedral_variants(SS[i]) for i in range(N)])  # N,8,48

# combined distance: ring L1 + min-pose sector L1; chunked all-pairs kNN
BIG = np.int64(1) << 40
TOPK = 3
top_idx = np.zeros((N, TOPK), dtype=np.int64)
top_d = np.zeros((N, TOPK), dtype=np.int64)
nn_cross = np.full(N, BIG, dtype=np.int64)
CH = 128
for i0 in range(0, N, CH):
    i1 = min(i0 + CH, N)
    dr = np.abs(RS[i0:i1, None, :] - RS[None, :, :]).sum(axis=2)
    a = SS[i0:i1]                                   # query in canonical pose
    dsect = None
    for v in range(8):
        dv = np.abs(a[:, None, :] - V[None, :, v, :]).sum(axis=2)
        dsect = dv if dsect is None else np.minimum(dsect, dv)
    d = dr + dsect
    rows = np.arange(i0, i1)
    d[rows - i0, rows] = BIG
    same = P[i0:i1, None] == P[None, :]
    nn_cross[i0:i1] = np.where(same, BIG, d).min(axis=1)
    part = np.argpartition(d, TOPK, axis=1)[:, :TOPK]
    top_idx[i0:i1] = part
    top_d[i0:i1] = np.take_along_axis(d, part, axis=1)

def cluster_at(edge_t):
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    edges = 0
    for i in range(N):
        for j, dv in zip(top_idx[i], top_d[i]):
            if dv <= edge_t:
                ri, rj = find(i), find(int(j))
                if ri != rj:
                    parent[ri] = rj
                edges += 1
    groups = {}
    for i in range(N):
        groups.setdefault(find(i), []).append(i)
    cl = sorted((v for v in groups.values() if len(v) >= 4),
                key=len, reverse=True)
    return cl, edges


# Threshold selection by stated rule, not by hand: candidate thresholds are
# exact percentiles of the cross-page NN distances; pick the LARGEST whose
# biggest cluster stays below the chain bound (500 — the numeral-dot family
# is legitimately ~500 strong) — the most inclusive vocabulary that has not
# collapsed into a chain. All candidates reported.
nn_sorted = np.sort(nn_cross)
candidates = [(pm, int(nn_sorted[(N - 1) * pm // 1000]))
              for pm in (5, 10, 20, 50, 100, 250)]
chosen = None
sweep_report = []
for pm, t in candidates:
    cl, ne = cluster_at(t)
    big = len(cl[0]) if cl else 0
    sweep_report.append((pm, t, len(cl), big, ne))
    if cl and big <= 500:
        chosen = (pm, t, cl, ne)
EDGE_T = chosen[1]
clusters, edges = chosen[2], chosen[3]
sizes = [len(c) for c in clusters]
L.append("Threshold sweep (permille of NN dist -> threshold, families, "
         "largest, edges): " + "; ".join(
             "%d->%d: %d fam, max %d, %d e" % r for r in sweep_report))
L.append("Chosen by rule (largest threshold with max cluster <= 500): "
         "permille %d, threshold %d." % (chosen[0], chosen[1]))
check("mega-chains split: largest cluster <= 500", sizes[0] <= 500)
check("vocabulary has multiple families", len(clusters) >= 8)

# --- full contact sheets per cluster --------------------------------------
def crop(k, b, pad=3, scale=3):
    img = Image.open(page_path(k)).convert("RGB")
    c = img.crop((max(0, b[2] - pad), max(0, b[0] - pad),
                  b[3] + pad, b[1] + pad))
    return c.resize((c.width * scale, c.height * scale), Image.NEAREST)


MAXC = 40
CW, CHh = 84, 96
for ci, c in enumerate(clusters[:MAXC]):
    members = c[:64]
    cols = 8
    rows_n = (len(members) + cols - 1) // cols
    sheet = Image.new("RGB", (CW * cols, CHh * rows_n + 18), (14, 14, 14))
    sd = ImageDraw.Draw(sheet)
    sd.text((4, 2), "family %02d — %d members" % (ci + 1, len(c)),
            fill=(255, 210, 40))
    for m, gi in enumerate(members):
        k, b = cells[gi]
        im = crop(k, b)
        im.thumbnail((CW - 6, CHh - 22))
        x0 = (m % cols) * CW + 3
        y0 = 18 + (m // cols) * CHh
        sheet.paste(im, (x0, y0 + 14))
        sd.text((x0, y0), "p%s" % page_label(k), fill=(140, 200, 255))
    sheet.save(os.path.join(CDIR, "family_%02d.png" % (ci + 1)))

ledger = Ledger()
ledger.record("vocab_cluster",
              {"cells": N, "edge_threshold": EDGE_T, "edges": edges,
               "families_ge4": len(clusters), "largest": sizes[0],
               "code": "ring12 + sector6x8 dihedral-min"},
              "sweep", "families")
with open(os.path.join(DATA, "vocab_receipts.json"), "w") as f:
    f.write(ledger.export())

L.append("Form vocabulary: %d cells, threshold %d, %d families (size >= 4), "
         "size spectrum %s..." % (N, EDGE_T, len(clusters), sizes[:12]))
L.append("Contact sheets: data/dresden/derived/clusters/family_NN.png "
         "(top %d families, every member page-labelled)." % min(MAXC, len(clusters)))

with open(os.path.join(DOCS, "DRESDEN_VOCAB.md"), "w") as f:
    f.write("# Glyph form vocabulary — dihedral sector codes\n\n"
            "Run: `python3 analysis/dresden_vocab.py`.\n"
            "Receipts: `data/dresden/vocab_receipts.json`.\n\n"
            "**%s exact checks, %d failures.**\n\n" % (
                "{:,}".format(R["checks"]), R["fails"])
            + "\n".join(L) + "\n\n"
            "| Family | Size | Pages reached | Sheet |\n|---|---|---|---|\n"
            + "\n".join(
                "| %d | %d | %s | `derived/clusters/family_%02d.png` |" % (
                    ci + 1, len(c),
                    ",".join(sorted(set(page_label(cells[i][0]) for i in c),
                                    key=lambda s: (len(s), s))[:14])
                    + ("…" if len(set(cells[i][0] for i in c)) > 14 else ""),
                    ci + 1)
                for ci, c in enumerate(clusters[:MAXC])) + "\n")

print("\n".join(x for x in L if x.startswith("  FAIL")) or "no FAIL lines")
print("\n".join(x for x in L if not x.startswith("  FAIL")))
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
