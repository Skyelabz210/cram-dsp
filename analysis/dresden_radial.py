"""Radial character decomposition — the researcher's center-outward search.

The instruction, restated precisely: do not "find glyphs near the
character". Start at the CHARACTER'S CENTER, build concentric rings, divide
each ring into angular sectors, extract the internal structure of what sits
in each sector, and search OUTWARD ring by ring — matching each piece
against the rest of the page and the codex. The result is a radial
coordinate system for the character: ring 0 → ring 1 → ring 2 …, and within
a ring, sector 0 → sector 1 → …

Per-pose reporting is mandatory (RULES_OF_EXPLORATION rule 6 in spirit):
every match is reported as DIRECT / ROTATED / MIRRORED / ROT+MIR separately,
never collapsed, so "repetition" can be inspected for what kind it is.
Matching runs on EVIDENCE representations only (rule 4): the ink mask from
the page's own integer Otsu threshold, never a contrast-boosted render.

Usage:
  python3 analysis/dresden_radial.py <page> [cy cx radius]
  default: page 69, the located character in the researcher's column.
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
RDOC = os.path.join(ROOT, "docs", "regions")
os.makedirs(RDOC, exist_ok=True)

POSES = ["direct", "rotated", "mirrored", "rot+mir"]


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


def scan_for_page(label: str) -> int:
    if label.endswith("*"):
        base = int(label.rstrip("*"))
        stars = len(label) - len(str(base))
        return 28 + stars if base == 28 else 64
    p = int(label)
    return p if p <= 28 else (p + 3 if p <= 60 else p + 4)


def page_path(k):
    return os.path.join(DATA, "pages", "wdl11621_scan%02d.jpg" % k)


def pose_of(variant_index: int) -> str:
    """dihedral_variants order: 4 rotations, then 4 reflected rotations."""
    if variant_index == 0:
        return "direct"
    if variant_index < 4:
        return "rotated"
    if variant_index == 4:
        return "mirrored"
    return "rot+mir"


def ring_sector_cells(mask, cy, cx, radius, n_rings=4, n_sectors=8,
                      min_area=40, max_area=6000):
    """Components of the ink mask inside the character disc, each tagged
    with the (ring, sector) it falls in — the character's own radial
    coordinate system. Exact integers: ring by exact isqrt of the squared
    distance, sector by axis-centred octant."""
    h, w = mask.shape
    y0, y1 = max(0, cy - radius), min(h, cy + radius)
    x0, x1 = max(0, cx - radius), min(w, cx + radius)
    sub = mask[y0:y1, x0:x1]
    labels, n = dresden.label_components(sub)
    out = []
    for i, b in enumerate(dresden.component_boxes(labels, n), start=1):
        by0, by1, bx0, bx1, area = b
        if not (min_area <= area <= max_area):
            continue
        ccy = y0 + (by0 + by1) // 2
        ccx = x0 + (bx0 + bx1) // 2
        dy, dx = ccy - cy, ccx - cx
        d2 = dy * dy + dx * dx
        if d2 > radius * radius:
            continue
        d = int(dresden._isqrt_grid(np.asarray([[d2]]))[0][0])
        ring = min((d * n_rings) // max(radius, 1), n_rings - 1)
        sect = int(dresden.octant_index(np.asarray([[dy]]),
                                        np.asarray([[dx]]))[0][0])
        gbox = (y0 + by0, y0 + by1, x0 + bx0, x0 + bx1, area)
        out.append((ring, sect, gbox, d))
    out.sort(key=lambda r: (r[0], r[1], r[3]))
    return out


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "69"
    k = scan_for_page(label)
    rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
    y = dresden.int_luma(rgb)
    thr = dresden.otsu_threshold(y)
    mask = dresden.ink_mask(y, thr)          # EVIDENCE representation

    if len(sys.argv) >= 5:
        cy, cx, radius = (int(v) for v in sys.argv[2:5])
    else:
        # the located character in the researcher's p69 column:
        # figure region under the bar/dot rows, centre of its ink mass
        sub = mask[980:1330, 70:270]
        ys, xs = np.nonzero(sub)
        cy = 980 + int(ys.sum()) // max(ys.size, 1)
        cx = 70 + int(xs.sum()) // max(xs.size, 1)
        radius = 150

    cells = ring_sector_cells(mask, cy, cx, radius)

    # page-wide + codex-wide candidate pool (evidence representations)
    pool_cells, pool_ring, pool_sect = [], [], []
    for kk in range(1, 79):
        rr = np.asarray(Image.open(page_path(kk)).convert("RGB"))
        yy = dresden.int_luma(rr)
        res = dresden.analyze_page(rr)
        mm = dresden.ink_mask(yy, res["threshold"])
        for b, rs in zip(res["boxes"], res["signatures"]):
            pool_cells.append((kk, b))
            pool_ring.append(rs)
            pool_sect.append(dresden.sector_signature(mm[b[0]:b[1], b[2]:b[3]]))
    PR = np.asarray(pool_ring, dtype=np.int64)
    PV = np.stack([dresden.dihedral_variants(s) for s in pool_sect])

    rows = []
    for ring, sect, gbox, dist in cells:
        q_ring = dresden.ring_signature(mask[gbox[0]:gbox[1], gbox[2]:gbox[3]])
        q_sect = dresden.sector_signature(mask[gbox[0]:gbox[1], gbox[2]:gbox[3]])
        dr = np.abs(PR - np.asarray(q_ring)).sum(axis=1)
        best_by_pose = {}
        for v in range(8):
            dv = np.abs(np.asarray(q_sect)[None, :] - PV[:, v, :]).sum(axis=1)
            tot = dr + dv
            pose = pose_of(v)
            for gi in np.argsort(tot, kind="stable")[:6]:
                gk, gb = pool_cells[int(gi)]
                if gk == k and gb == gbox:
                    continue
                cur = best_by_pose.get(pose)
                if cur is None or int(tot[gi]) < cur[0]:
                    best_by_pose[pose] = (int(tot[gi]), gk, gb)
                break
        rows.append((ring, sect, gbox, dist, best_by_pose))

    # --- render: the radial coordinate system over the character ---------
    S = 3
    y0, y1 = max(0, cy - radius), min(1350, cy + radius)
    x0, x1 = max(0, cx - radius), min(684, cx + radius)
    img = Image.fromarray(rgb[y0:y1, x0:x1]).resize(
        ((x1 - x0) * S, (y1 - y0) * S), Image.NEAREST)
    d = ImageDraw.Draw(img)
    ccy, ccx = (cy - y0) * S, (cx - x0) * S
    for r in range(1, 5):
        rr = (radius * r // 4) * S
        d.ellipse([ccx - rr, ccy - rr, ccx + rr, ccy + rr],
                  outline=(255, 210, 40), width=2)
    for s in range(8):
        # octant boundaries drawn on the axis-centred bins
        import math
        ang = (s * 45 - 22) * math.pi / 180
        d.line([(ccx, ccy), (ccx + int(radius * S * math.cos(ang)),
                             ccy + int(radius * S * math.sin(ang)))],
               fill=(120, 100, 30), width=1)
    for i, (ring, sect, gbox, dist, bp) in enumerate(rows):
        bx = [(gbox[2] - x0) * S, (gbox[0] - y0) * S,
              (gbox[3] - x0) * S, (gbox[1] - y0) * S]
        d.rectangle(bx, outline=(0, 220, 255), width=2)
        d.text((bx[0], bx[1] - 12), "r%d s%d" % (ring, sect),
               fill=(0, 220, 255))
    d.ellipse([ccx - 6, ccy - 6, ccx + 6, ccy + 6], fill=(255, 80, 40))
    img.save(os.path.join(DEMO, "dresden_radial_p%s.png" % label))

    # --- report ------------------------------------------------------------
    L = ["# Radial decomposition — page %s (scan %d), centre (%d, %d), radius %d"
         % (label, k, cy, cx, radius),
         "",
         "Method: character centre → 4 concentric rings → 8 axis-centred",
         "sectors; ink components inside the disc are read OUTWARD, ring by",
         "ring, sector by sector, and each is matched against all %d glyph"
         % len(pool_cells),
         "cells in the codex under all 8 dihedral poses. Matching runs on the",
         "EVIDENCE representation (integer-Otsu ink mask), never on a",
         "contrast-enhanced render. Poses are reported separately — direct,",
         "rotated, mirrored, rot+mir — and never collapsed.",
         "",
         "Panel: `demo/dresden_radial_p%s.png`." % label,
         "",
         "| Ring | Sector | Piece (y0,y1,x0,x1) | dist from centre | direct | rotated | mirrored | rot+mir |",
         "|---|---|---|---|---|---|---|---|"]
    for ring, sect, gbox, dist, bp in rows:
        cols = []
        for pose in POSES:
            v = bp.get(pose)
            cols.append("p%s (%d,%d) d=%d" % (page_label(v[1]), v[2][0],
                                              v[2][2], v[0]) if v else "—")
        L.append("| %d | %d | (%d,%d,%d,%d) | %d | %s | %s | %s | %s |" % (
            ring, sect, gbox[0], gbox[1], gbox[2], gbox[3], dist, *cols))

    # pose summary: which kind of repetition dominates
    tally = {p: 0 for p in POSES}
    for _, _, _, _, bp in rows:
        if not bp:
            continue
        best = min(bp.items(), key=lambda kv: kv[1][0])
        tally[best[0]] += 1
    # Chance baseline for the pose tally: the 8 dihedral variants split
    # 1 direct : 3 rotated : 1 mirrored : 3 rot+mir, so a code with no pose
    # preference lands in those proportions. Stating the baseline stops the
    # tally from reading as a finding when it is arithmetic.
    n_pieces = sum(tally.values())
    expect = {"direct": n_pieces, "rotated": 3 * n_pieces,
              "mirrored": n_pieces, "rot+mir": 3 * n_pieces}
    L += ["", "Pose tally over pieces (which pose gives each piece its best "
          "match), with the chance baseline from pose multiplicity "
          "(1 direct : 3 rotated : 1 mirrored : 3 rot+mir):",
          "",
          "| Pose | Observed | Expected at chance (x1000) |",
          "|---|---|---|"]
    for p in POSES:
        L.append("| %s | %d | %d |" % (p, tally[p], (1000 * expect[p]) // 8))
    L += ["",
          "Status: MEASURED. Whether any pose class exceeds its multiplicity",
          "baseline is visible in the table; no verdict is drawn here, and",
          "no claim is made about what the radial sequence encodes",
          "(docs/RULES_OF_EXPLORATION.md)."]

    ledger = Ledger()
    ledger.record("radial_decomposition",
                  {"page": label, "scan": k, "center": [cy, cx],
                   "radius": radius, "rings": 4, "sectors": 8,
                   "pieces": len(rows), "pool": len(pool_cells),
                   "pose_tally": tally},
                  Ledger.digest(y), Ledger.digest(mask))
    L += ["", "Receipts chain head: `%s`" % ledger.chain]
    out = os.path.join(RDOC, "radial_p%s.md" % label)
    with open(out, "w") as f:
        f.write("\n".join(L) + "\n")
    print("report:", out)
    print("pieces:", len(rows), "pose tally:", tally)


if __name__ == "__main__":
    main()
