"""Scales — giving existing readings a unit.

Two numbers the machine already produces have no scale attached, which makes
them unreadable rather than unproven:

  S1 path agreement — "A~B agree 640 milli" means nothing until we know what
     three constructions over the SAME nodes with SHUFFLED POSITIONS agree
     at. The shuffle keeps every node's brightness, contrast and gradient
     exactly, and permutes only where the nodes sit, so it isolates the one
     thing in question: whether spatial arrangement relates to the
     brightness field at all.

  S2 cross-page continuity — "96 facing-edge alignments between consecutive
     scans" means nothing until we know what non-adjacent page pairs give.

Neither scale gates anything and neither can close anything
(docs/RULES_OF_EXPLORATION.md). They convert bare counts into readings with
a unit, which is all they are for.

Usage: python3 analysis/dresden_scales.py
"""

import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import dresden
from cram_dsp.forensics import Ledger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "dresden")
DOCS = os.path.join(ROOT, "docs")

R = {"checks": 0, "fails": 0}
L = []

SHUFFLES = 15
LIMIT = 12          # nodes per ordering, matching the white-field run


def check(name, cond, n=1):
    R["checks"] += n
    if not cond:
        R["fails"] += 1
        L.append("  FAIL — %s" % name)
    return cond


def page_label(k):
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


def med(v):
    if not v:
        return 0
    s = sorted(v)
    return s[(len(s) - 1) // 2]


# --- fixture: the scale machinery itself -----------------------------------
recs_fx = [(10 * i, 10 * i, 50, 200, 190, 20 - i, 5, 0, 2, 100 - i)
           for i in range(8)]
a = dresden.order_brightness(recs_fx, LIMIT)
b = dresden.order_spatial(recs_fx, LIMIT)
check("a perfectly co-linear brightness/space layout agrees at 1000",
      dresden.ordering_agreement_milli(a, b) == 1000)
g1, g2 = dresden.LCG(7), dresden.LCG(7)
check("LCG shuffle is deterministic",
      [g1.next_below(8) for _ in range(5)]
      == [g2.next_below(8) for _ in range(5)])

# ===========================================================================
# S1 — path-agreement scale
# ===========================================================================
ledger = Ledger()
s1_rows = []
for k in range(1, 79):
    rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
    thr, recs = dresden.node_records(rgb)
    if len(recs) < LIMIT:
        continue
    A = dresden.order_brightness(recs, LIMIT)
    B = dresden.order_spatial(recs, LIMIT)
    C = dresden.order_gradient_flow(recs, LIMIT)
    obs = min(dresden.ordering_agreement_milli(A, B),
              dresden.ordering_agreement_milli(A, C),
              dresden.ordering_agreement_milli(B, C))
    # shuffled-position null: keep every attribute, permute positions only
    rng = dresden.LCG(20260828 + k)
    pos = [(r[0], r[1]) for r in recs]
    nulls = []
    for _ in range(SHUFFLES):
        idx = list(range(len(pos)))
        for j in range(len(idx) - 1, 0, -1):
            q = rng.next_below(j + 1)
            idx[j], idx[q] = idx[q], idx[j]
        sh = [(pos[idx[i]][0], pos[idx[i]][1]) + tuple(r[2:])
              for i, r in enumerate(recs)]
        sA = dresden.order_brightness(sh, LIMIT)
        sB = dresden.order_spatial(sh, LIMIT)
        sC = dresden.order_gradient_flow(sh, LIMIT)
        nulls.append(min(dresden.ordering_agreement_milli(sA, sB),
                         dresden.ordering_agreement_milli(sA, sC),
                         dresden.ordering_agreement_milli(sB, sC)))
    nulls.sort()
    ge = sum(1 for v in nulls if v >= obs)
    s1_rows.append((k, len(recs), obs, nulls[0], med(nulls), nulls[-1], ge))
    ledger.record("scale_path_agreement",
                  {"scan": k, "page": page_label(k), "observed": obs,
                   "null_min": nulls[0], "null_med": med(nulls),
                   "null_max": nulls[-1], "null_ge_observed": ge,
                   "shuffles": SHUFFLES},
                  Ledger.digest(dresden.int_luma(rgb)), "scale")
check("S1 computed on the codex", len(s1_rows) > 60)
above = [r for r in s1_rows if r[6] == 0]
inside = [r for r in s1_rows if r[6] > 0]

# ===========================================================================
# S2 — cross-page continuity scale
# ===========================================================================
edges = {}
for k in range(1, 79):
    y = dresden.int_luma(np.asarray(Image.open(page_path(k)).convert("RGB")))
    ink = dresden.ink_mask(y, dresden.otsu_threshold(y))
    _, trails, _ = dresden.filament_components(y, ink=ink)
    edges[k] = ([t[0] for t in trails if t[0][2] <= 24],
                [t[0] for t in trails if t[0][3] >= 684 - 24])


def align(a, b):
    """Facing-edge alignments: right-edge trails of a vs left-edge of b."""
    n = 0
    for rb in edges[a][1]:
        for lb in edges[b][0]:
            if rb[0] <= lb[1] and lb[0] <= rb[1]:
                n += 1
                break
    return n


adj = [(k, align(k, k + 1)) for k in range(1, 78)]
adj_total = sum(n for _, n in adj)
adj_pairs = sum(1 for _, n in adj if n)

rng = dresden.LCG(4242)
non_adj = []
seen = set()
while len(non_adj) < 200:
    i = rng.next_below(78) + 1
    j = rng.next_below(78) + 1
    if abs(i - j) <= 1 or (i, j) in seen:
        continue
    seen.add((i, j))
    non_adj.append(((i, j), align(i, j)))
na_total = sum(n for _, n in non_adj)
na_pairs = sum(1 for _, n in non_adj if n)

adj_rate = (1000 * adj_total) // len(adj)
na_rate = (1000 * na_total) // len(non_adj)
check("S2 sampled both populations",
      len(adj) == 77 and len(non_adj) == 200)
ledger.record("scale_continuity",
              {"adjacent_pairs": len(adj), "adjacent_alignments": adj_total,
               "adjacent_rate_milli": adj_rate,
               "nonadjacent_pairs": len(non_adj),
               "nonadjacent_alignments": na_total,
               "nonadjacent_rate_milli": na_rate},
              "edges", "scale")

with open(os.path.join(DATA, "scale_receipts.json"), "w") as f:
    f.write(ledger.export())

# --- report ----------------------------------------------------------------
out = [
    "# Scales — units for readings the machine already takes",
    "",
    "Run: `python3 analysis/dresden_scales.py`; receipts",
    "`data/dresden/scale_receipts.json`.",
    "",
    "**%s exact checks, %d failures.**" % ("{:,}".format(R["checks"]), R["fails"]),
    "",
    "These two instruments attach a unit to numbers that previously had none.",
    "They gate nothing and close nothing (docs/RULES_OF_EXPLORATION.md); a",
    "reading inside its scale is as interesting as one outside it, and both",
    "are simply readings.",
    "",
    "## S1 — path-agreement scale",
    "",
    "For each page: the minimum pairwise agreement among the three orderings",
    "(brightness / spatial / gradient-flow) over the top %d nodes, against %d"
    % (LIMIT, SHUFFLES),
    "seeded shuffles that permute node POSITIONS while keeping every node's",
    "brightness, contrast, gradient and chroma exactly. The shuffle isolates",
    "one thing: whether where the bright structures sit relates to the",
    "brightness field's own ordering.",
    "",
    "Pages measured: **%d**. Observed agreement above every shuffle: **%d**."
    % (len(s1_rows), len(above)),
    "Observed agreement inside the shuffled range: **%d**." % len(inside),
    "",
    "| Scan | Page | Nodes | Observed | Shuffled min | Shuffled median | Shuffled max | Shuffles >= observed |",
    "|---|---|---|---|---|---|---|---|",
]
for k, n, obs, lo, mid, hi, ge in s1_rows:
    out.append("| %d | %s | %d | %d | %d | %d | %d | %d |" % (
        k, page_label(k), n, obs, lo, mid, hi, ge))
if above:
    out += ["",
            "Pages whose observed agreement exceeded every shuffle: " +
            ", ".join("p%s (obs %d vs shuffled max %d)" %
                      (page_label(k), obs, hi)
                      for k, n, obs, lo, mid, hi, ge in above) + ".", ""]
out += [
    "",
    "## S2 — cross-page continuity scale",
    "",
    "Facing-edge trail alignments (right-edge trails of one scan against",
    "left-edge trails of another, by y-interval overlap).",
    "",
    "| Population | Pairs | Alignments | Alignments per pair (milli) |",
    "|---|---|---|---|",
    "| consecutive scans | %d | %d | %d |" % (len(adj), adj_total, adj_rate),
    "| non-adjacent pairs (seeded sample) | %d | %d | %d |" % (
        len(non_adj), na_total, na_rate),
    "",
    "Consecutive pairs with at least one alignment: %d of %d. Non-adjacent "
    "pairs with at least one: %d of %d." % (adj_pairs, len(adj), na_pairs,
                                            len(non_adj)),
    "",
    "Caveat carried from the trail catalog: modern scan adjacency is not",
    "asserted to be original screenfold order, and edge trails are a",
    "property of the physical strip and of how it was photographed. This",
    "scale says how consecutive pairs compare with unrelated pairs on this",
    "measurement — nothing more, and nothing is concluded from it.",
]
with open(os.path.join(DOCS, "DRESDEN_SCALES.md"), "w") as f:
    f.write("\n".join(out) + "\n")

print("\n".join(x for x in L if x.startswith("  FAIL")) or "no FAIL lines")
print("S1: %d pages, %d above all shuffles, %d inside" % (
    len(s1_rows), len(above), len(inside)))
print("S2: adjacent %d/%d pairs, %d alignments (rate %d milli); "
      "non-adjacent %d/%d pairs, %d alignments (rate %d milli)" % (
          adj_pairs, len(adj), adj_total, adj_rate,
          na_pairs, len(non_adj), na_total, na_rate))
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
