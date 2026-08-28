"""p17 (scan 17) — icon-to-character exact geometric registration.

The researcher picked this page: "Do page 17 of 78, I definitely see this
page." It is the concept illustration's layout made literal. Unlike p47
(polychrome paintings inside bounded panels) or p69 (one figure beside a
text column), here the small oval icons float in the SAME OPEN FIELD as the
figures — above, below and between them — which is exactly the arrangement
the illustrations depict.

Order is fixed and not reversed: geometry -> recurrence -> significance ->
interpretation. Nothing here assigns meaning, and nothing here closes
anything (docs/RULES_OF_EXPLORATION.md).

HOW THE PAGE IS SPLIT (the part that is new)

The figures on p17 are drawn in a much finer line than the icons. Three
attempts at separating them are kept as receipts:

  1. Global Otsu ink.  Sees the icons, misses the figures completely. The
     page's five "figures" under the previous detector were blocks of
     WRITING; not one of the four real figures was found.
  2. A second global threshold.  The band between the two Otsu cuts is
     323/1000 of the whole page, because it also selects shaded plaster.
     Line and shading do not separate against a global reference.
  3. Removing heavy ink from the local dark field.  Destroys the figures
     (fine fill drops to ~0/1000): the figure line is NOT lighter than the
     Otsu cut. Brightness was the wrong axis the whole time.

What separates them is STROKE WIDTH. The icons are drawn thick, the figures
thin, so an opening by a radius-2 element keeps the icons and erases the
figure line. Targets and icons are therefore a disjoint partition of the
same ink — which also means an icon can never trivially register onto
itself, the failure that forced a bounding-box exclusion on p47.

TARGETS ARE NOT HAND-PICKED. Every large thin-stroke component is a target,
figures and blocks of writing alike, each carrying only measured
statistics and no semantic label. If icons register onto the figures and
not onto the writing, that contrast is the measurement; if they register
onto both, that is the measurement. The writing blocks are the cross-target
control at no extra cost, and the machine — not the agent — decides what
gets tested.

Usage: python3 analysis/dresden_p17.py
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import dresden
from cram_dsp import registration as reg
from cram_dsp.forensics import Ledger
from analysis.dresden_correspond import (build_ladder, best_placement,
                                         full_map, evaluate, quarter,
                                         COARSE_ROT, FINE_ROT)
from analysis import dresden_correspond as _dc
from analysis.dresden_segment import leaf_block, despeckle

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "dresden")
OUT = os.path.join(DATA, "derived", "p17"
                   + ("" if os.environ.get("P17_SCALE", "natural") == "natural"
                      else "_ladder"))
DEMO = os.path.join(ROOT, "demo")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(OUT, exist_ok=True)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                       13)
FB = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)

SCAN = 17
DARK_MARGIN = 22        # luma below the local substrate level
STROKE_R = 2            # kept for the receipt in extract(); see the partition
CONTROL_SCAN = 5        # foreign-icon control: a different page, same rule

# The researcher's specification is explicit: measure the icon's ORIGINAL
# dimensions before resizing, and test warping last. NATURAL is that run —
# scale locked to 1/1, so a fit cannot be bought by shrinking the icon until
# it fits anything. LADDER is the permissive band kept for comparison. In the
# ladder run every one of the top eight results chose 2/3 or 3/4, which is
# the scale-shrinkage bias already receipted on p47 reappearing here.
NATURAL = [(1, 1)]
LADDER = [(2, 3), (3, 4), (1, 1), (4, 3), (3, 2)]
SCALES = NATURAL if os.environ.get("P17_SCALE", "natural") == "natural" \
    else LADDER


def erode(m, k):
    return ~dresden.dilate(~m, k)


def opening(m, k):
    return dresden.dilate(erode(m, k), k)


def extract(rgb):
    """Return (leaf, ink, targets, icons) — all masks in leaf coordinates."""
    ly0, ly1, lx0, lx1 = leaf_block(dresden.int_luma(rgb))
    leaf_y0, leaf_x0 = ly0, lx0
    sub = rgb[ly0:ly1, lx0:lx1]
    y = dresden.int_luma(sub)
    H, W = y.shape
    cls, _thr = dresden.pigment_classes(sub)
    inset = np.zeros((H, W), dtype=bool)
    inset[16:H - 16, 16:W - 16] = True
    # red rules and the damaged leaf edge chain every component into one
    # page-spanning blob; both are excluded before anything is labelled
    ink = despeckle((dresden.local_dark_field(y) >= DARK_MARGIN)
                    & ~(cls == dresden.PIG_RED) & inset, 12)

    # ---- the partition: closed compact LOOPS are icons, everything else --
    #
    # RECEIPT — three attempts, all kept.
    #  (a) STROKE WIDTH. The figures are drawn finer than the writing, so an
    #      opening by a radius-2 element was used to split them. It does
    #      separate figure from writing, but NOT figure from icon: the ovals
    #      are thin-outlined rings, so the opening erased them too and the
    #      only "icons" it returned were the solid fills inside the figures
    #      (a headdress, a waistband).
    #  (b) Icons from the segmentation cells, targets from the thin-stroke
    #      components. The ovals are thin, so after the dilation they JOINED
    #      the figure's component and every target silently contained the
    #      icons surrounding it. That run's top result — icon 32 to T5, IoU
    #      547, boundary overlap 982/1000 — is visibly, in its own overlay,
    #      the icon landing on the edge of a NEIGHBOURING OVAL, outside the
    #      figure entirely. The icon set was registering onto itself.
    #  (c) Cutting every segmentation cell out of the targets. On this page
    #      the cell pass also boxes parts of the figures, so this shredded
    #      all four figures below the size floor and left only writing.
    #
    # What actually separates them is TOPOLOGY. Each oval is a small CLOSED
    # loop; the figure line is a large open structure. Measured at dilation
    # zero: 67 compact components carry a hole, median 34x41 px, against 6
    # large structures. Icons and targets are now disjoint by component
    # identity, so an icon cannot register onto itself or onto a neighbour
    # that leaked into the target.
    lab0, n0 = dresden.label_components(ink)
    boxes0 = dresden.component_boxes(lab0, n0)
    icon_ids, icons = [], []
    for i, b in enumerate(boxes0, start=1):
        h, w = b[1] - b[0], b[3] - b[2]
        if not (15 <= h <= 65 and 15 <= w <= 65 and b[4] >= 100):
            continue
        m = lab0[b[0]:b[1], b[2]:b[3]] == i
        if dresden.count_holes(np.pad(m, 1)) < 1:
            continue
        icon_ids.append(i)
        icons.append({"box": [int(v) for v in b[:4]], "mask": m,
                      "area": int(b[4]),
                      "fill_milli": (1000 * int(b[4])) // max(h * w, 1),
                      "holes": int(dresden.count_holes(np.pad(m, 1)))})
    icon_union = np.isin(lab0, np.asarray(icon_ids, dtype=np.int64)) \
        if icon_ids else np.zeros_like(ink)
    body = despeckle(ink & ~icon_union, 12)

    tl, tn = dresden.label_components(dresden.dilate(body, 3))
    targets = []
    for i, b in enumerate(dresden.component_boxes(tl, tn), start=1):
        h, w = b[1] - b[0], b[3] - b[2]
        if b[4] < 6000 or h < 90 or w < 90:
            continue
        if w > (W * 4) // 5 or h > (H * 2) // 5:
            continue
        m = (tl[b[0]:b[1], b[2]:b[3]] == i) & body[b[0]:b[1], b[2]:b[3]]
        if int(m.sum()) < 2000:
            continue
        targets.append({"box": [int(v) for v in b[:4]], "mask": m,
                        "area": int(m.sum())})
    targets.sort(key=lambda t: -t["area"])
    thin, thick = body, icon_union
    icons.sort(key=lambda c: (c["box"][0], c["box"][2]))
    return (ly0, ly1, lx0, lx1), ink, thin, thick, targets, icons


def main():
    rgb = np.asarray(Image.open(os.path.join(
        DATA, "pages", "wdl11621_scan%02d.jpg" % SCAN)).convert("RGB"))
    leaf, ink, thin, thick, targets, icons = extract(rgb)
    print("leaf", leaf)
    print("targets", len(targets), "icons", len(icons))
    for i, t in enumerate(targets):
        b = t["box"]
        print("  T%d scan y%d-%d x%d-%d  area %d"
              % (i, b[0] + leaf[0], b[1] + leaf[0],
                 b[2] + leaf[2], b[3] + leaf[2], t["area"]))
    np.save(os.path.join(OUT, "_masks.npy"),
            np.stack([ink, thin, thick]).astype(np.uint8))
    with open(os.path.join(OUT, "_inventory.json"), "w") as f:
        json.dump({"leaf": list(leaf),
                   "targets": [{"box": t["box"], "area": t["area"]}
                               for t in targets],
                   "icons": [{"box": c["box"], "area": c["area"],
                              "fill_milli": c["fill_milli"],
                              "holes": c["holes"]}
                             for c in icons]}, f)

    # inventory overlay — inspected before any registration is run
    # Draw on the high-resolution scan when it is present (see the same
    # receipt in analysis/dresden_segment.py): the analysis runs on the PDF's
    # 684x1350 pages, but delivering the overlay on them made the picture
    # unreadable. Boxes are the same exact integers in scan coordinates.
    _hp = os.path.join(DATA, "hires", "slub_p%02d.jpg" % SCAN)
    if os.path.exists(_hp):
        _b = Image.open(_hp).convert("RGB")
        _OW = 1700
        img = _b.resize((_OW, _b.height * _OW // _b.width), Image.LANCZOS)
        S = _OW / rgb.shape[1]
    else:
        S = 2
        img = Image.fromarray(rgb).convert("RGB").resize(
            (rgb.shape[1] * S, rgb.shape[0] * S), Image.LANCZOS)
    pan = Image.new("RGB", (img.width, img.height + 46), (16, 16, 16))
    pan.paste(img, (0, 46))
    d = ImageDraw.Draw(pan)
    d.text((8, 6), "p17 INVENTORY — %d targets (thin stroke, green) / %d "
                   "icons (thick stroke, yellow). EVIDENCE overlay."
           % (len(targets), len(icons)), fill=(240, 240, 240), font=FB)
    d.text((8, 26), "Targets are NOT hand-picked: every large thin-stroke "
                    "component is one, writing blocks included, as the "
                    "cross-target control.", fill=(150, 150, 150), font=F)
    for i, t in enumerate(targets):
        b = t["box"]
        d.rectangle([int(S * (b[2] + leaf[2])), int(S * (b[0] + leaf[0])) + 46,
                     int(S * (b[3] + leaf[2])), int(S * (b[1] + leaf[0])) + 46],
                    outline=(0, 235, 120), width=3)
        d.text((int(S * (b[2] + leaf[2])) + 4, int(S * (b[0] + leaf[0])) + 49),
               "T%d" % i, fill=(0, 235, 120), font=FB)
    for j, c in enumerate(icons):
        b = c["box"]
        d.rectangle([int(S * (b[2] + leaf[2])), int(S * (b[0] + leaf[0])) + 46,
                     int(S * (b[3] + leaf[2])), int(S * (b[1] + leaf[0])) + 46],
                    outline=(255, 205, 60), width=2)
        d.text((int(S * (b[2] + leaf[2])) + 2, int(S * (b[0] + leaf[0])) + 47),
               str(j), fill=(255, 205, 60), font=F)
    pan.save(os.path.join(DEMO, "dresden_p17_inventory.jpg"), quality=80,
             optimize=True)
    print("inventory overlay written")

    if os.environ.get("P17_INVENTORY_ONLY"):
        return

    # === EXHAUSTION: every icon x every target x {ink, negative space} =====
    # The target EDT and the quarter-resolution target are properties of the
    # TARGET alone, so they are computed once per (target, space) rather than
    # once per registration. The first version rebuilt them inside the icon
    # loop and cost ~2 minutes per icon; nothing about the numbers changes.
    ladders = []
    for c in icons:
        ladders.append(build_ladder(c["mask"], COARSE_ROT, SCALES, 2))
    recs = []
    for ti, t in enumerate(targets):
        tm = t["mask"]
        for space, target_mask in (("ink", tm), ("negative", ~tm)):
            tq = quarter(target_mask)
            edt = reg.sq_edt(reg.contour(target_mask))
            for j, c in enumerate(icons):
                lad = ladders[j]
                if not lad:
                    continue
                bp = best_placement(lad, tq)
                if bp is None:
                    continue
                fm = full_map(c["mask"], target_mask,
                              bp[3], bp[4], bp[5], bp[6])
                if fm is None:
                    continue
                iou, dy, dx, med, p95, p99 = fm
                met, _canvas = evaluate(c["mask"], target_mask, edt,
                                        bp[3], bp[4], bp[5], bp[6], dy, dx)
                ih, iw = c["mask"].shape
                im = reg.transform_mask(c["mask"], bp[3], bp[4], bp[5], bp[6])
                recs.append({
                    "icon": j, "holes": c["holes"], "target": ti,
                    "space": space,
                    "icon_box_scan": [c["box"][0] + leaf[0],
                                      c["box"][1] + leaf[0],
                                      c["box"][2] + leaf[2],
                                      c["box"][3] + leaf[2]],
                    "icon_wh_original": [iw, ih],
                    "icon_wh_placed": [im.shape[1], im.shape[0]],
                    "rot": list(bp[3]), "scale": [bp[4], bp[5]],
                    "mirror": bp[6], "dy": dy, "dx": dx,
                    "iou_milli": iou, "null_median": med,
                    "null_p95": p95, "null_p99": p99,
                    "margin_over_p99": iou - p99,
                    "chamfer_milli": met["chamfer_milli"],
                    "hausdorff": met["hausdorff"],
                    "overlap_milli": met["overlap_milli"],
                    "topology_match": met["topology_match"],
                    "icon_endpoints": met["icon_endpoints"],
                    "icon_branches": met["icon_branches"],
                    "target_endpoints": met["target_endpoints"],
                    "target_branches": met["target_branches"]})
            print("T%d %s done (%d records)" % (ti, space, len(recs)),
                  flush=True)

    # === CONTROL: FOREIGN ICONS ===========================================
    # RECEIPT — the statistic this replaces. The first run reported that
    # 608 of 608 ink registrations "cleared their own matched null" (76 of 76
    # on every single target). That is very close to a tautology: the matched
    # null is the IoU distribution of the SAME icon over every offset on the
    # SAME target, and the argmax of a distribution beats that distribution's
    # own p99 unless its top percentile is flat. It measures nothing about
    # correspondence and is not reported as a result. The same defect was
    # already receipted once on p47; it is recorded again here because the
    # rewritten pipeline reintroduced it.
    #
    # The control that does mean something: icons drawn on a DIFFERENT PAGE,
    # extracted by the identical closed-loop rule, registered against these
    # same targets. If p17's own icons register onto p17's figures better
    # than foreign icons do, the difference is the measurement. If they do
    # not, that is equally the measurement.
    frgb = np.asarray(Image.open(os.path.join(
        DATA, "pages", "wdl11621_scan%02d.jpg" % CONTROL_SCAN)).convert("RGB"))
    _fl, _fi, _ft, _fk, _ftg, foreign = extract(frgb)
    foreign = foreign[:40]
    print("foreign control icons:", len(foreign), "from scan", CONTROL_SCAN)
    ctrl = []
    flad = [build_ladder(c["mask"], COARSE_ROT, SCALES, 2) for c in foreign]
    for ti, t in enumerate(targets):
        tm = t["mask"]
        tq = quarter(tm)
        for j, c in enumerate(foreign):
            if not flad[j]:
                continue
            bp = best_placement(flad[j], tq)
            if bp is None:
                continue
            fm = full_map(c["mask"], tm, bp[3], bp[4], bp[5], bp[6])
            if fm is None:
                continue
            ctrl.append({"icon": j, "target": ti, "source": "scan%d"
                         % CONTROL_SCAN, "iou_milli": fm[0],
                         "scale": [bp[4], bp[5]], "mirror": bp[6]})
        print("control T%d done (%d)" % (ti, len(ctrl)), flush=True)
    with open(os.path.join(OUT, "control_foreign.json"), "w") as f:
        json.dump(ctrl, f)

    with open(os.path.join(OUT, "registrations.json"), "w") as f:
        json.dump(recs, f)
    print("registrations:", len(recs))


if __name__ == "__main__":
    main()
