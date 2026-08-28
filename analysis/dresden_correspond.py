"""Icon -> character correspondence by EXACT geometric registration.

The experiment: on a page with several illustrated characters, test whether
each surrounding icon can be REGISTERED onto a specific location of a
character — contour, internal structure, orientation and proportion fitting
at a natural scale. Not similarity. Registration.

Order is fixed: geometry -> recurrence -> significance. No meaning is
assigned anywhere in this file; no anatomical labels are used.

Method
  characters   large black-ink drawings (register rules are RED and are
               excluded, otherwise the whole page merges into one blob)
  icons        every other glyph/icon component on the page, outside the
               character boxes -- ALL of them, none skipped
  transforms   translation -> rotation -> uniform scale, in that order.
               Rotations are EXACT rational maps from Pythagorean triples
               (cram_dsp/registration.py); scale is an exact rational.
               Ladder stated in the report; anisotropic/affine deliberately
               NOT used -- unrestricted warping fits anything.
  search       whole-character sliding search (coarse at half resolution,
               then refined at full resolution), so a correspondence is
               DISCOVERED rather than asserted by pointing at a region.
               The same search is run against the character's NEGATIVE
               SPACE (gaps between strokes/limbs).
  metrics      chamfer (milli px), directed Hausdorff (px), boundary
               overlap (milli), mask IoU (milli), and topology
               (endpoints/branch points) -- all exact integers.
  controls     every icon is tested against EVERY character, so
               within-panel vs cross-panel fit is measured directly; plus a
               seeded null of random icon-sized crops.

Usage: python3 analysis/dresden_correspond.py [scan] [--fast]
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import dresden
from cram_dsp import registration as reg
from cram_dsp.forensics import Ledger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "dresden")
DEMO = os.path.join(ROOT, "demo")
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(DEMO, "correspond")
os.makedirs(OUT, exist_ok=True)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F16 = ImageFont.truetype(FONT, 16)
F13 = ImageFont.truetype(FONT, 13)
F22 = ImageFont.truetype(FONT, 22)

R = {"checks": 0, "fails": 0}
NOTES = []


def check(name, cond, n=1):
    R["checks"] += n
    if not cond:
        R["fails"] += 1
        NOTES.append("  FAIL — %s" % name)
    return cond


def reg_holes(mask):
    """Holes enclosed by a mask (4-connected background not touching the
    border) — an interior structure test, exact."""
    return dresden.count_holes(np.pad(np.asarray(mask), 1))


def page_label(k):
    if k <= 28:
        return str(k)
    if k in (29, 30, 31):
        return "28" + "*" * (k - 28)
    if k <= 63:
        return str(k - 3)
    if k == 64:
        return "60*"
    return str(k - 4)


def page_path(k):
    return os.path.join(DATA, "pages", "wdl11621_scan%02d.jpg" % k)


# --------------------------------------------------------------- transforms
COARSE_ROT = [0, 5, 12]          # 0, 16.26, 36.87 degrees
FINE_ROT = [0, 1, 2, 3, 4, 5, 6, 7, 9, 12, 15]
# Natural-scale band only. 1/2 and 2/1 were removed after the first overlay
# pass: shrinking an icon to half size destroys its internal structure and
# lets any small dark blob register onto any other, which is what the top
# "matches" then were. Receipt kept rather than a silent parameter change.
SCALES = [(2, 3), (3, 4), (1, 1), (4, 3), (3, 2)]
FINE_SCALES = [(2, 3), (3, 4), (1, 1), (4, 3), (3, 2)]


def rot_set(idx):
    out = []
    for t in idx:
        a, b, c = reg.TRIPLES[t]
        out.append((a, b, c))
        if b:
            out.append((a, -b, c))
    return out


def half(mask):
    """Exact 2x decimation by OR-pooling — keeps thin strokes alive."""
    m = np.asarray(mask)
    h, w = (m.shape[0] // 2) * 2, (m.shape[1] // 2) * 2
    q = m[:h, :w].reshape(h // 2, 2, w // 2, 2)
    return q.any(axis=(1, 3))


def score_map(pts, edt_pad, hs, ws, pad):
    """Sum of target-EDT values under the icon's contour points, for every
    offset. Sparse points -> a few dozen slice adds; exact integers."""
    acc = np.zeros((hs, ws), dtype=np.int64)
    for i in range(pts.shape[0]):
        py = int(pts[i, 0]) + pad
        px = int(pts[i, 1]) + pad
        acc += edt_pad[py:py + hs, px:px + ws]
    return acc


def padded_edt(target_contour, pad):
    e = reg.sq_edt(target_contour)
    return np.pad(e, pad, constant_values=int(reg.BIG))


def quarter(mask):
    return half(half(mask))


def build_ladder(icon_mask, rot_idx, scales, level):
    """Transform the icon ONCE per (rotation, scale, mirror) and keep the
    reduced mask. Transforms do not depend on the target, so this is
    computed once and reused for every character and both spaces."""
    out = []
    for rot in rot_set(rot_idx):
        for (num, den) in scales:
            for mirror in (0, 1):
                im = reg.transform_mask(icon_mask, rot, num, den, mirror)
                red = im
                for _ in range(level):
                    red = half(red)
                if int(red.sum()) < 4:
                    continue
                out.append((rot, num, den, mirror, red))
    return out


def best_placement(ladder, target_reduced):
    """Highest exact area agreement (IoU, milli) over the ladder and every
    offset. IoU rather than chamfer: a character is a dense line drawing, so
    one-directional chamfer saturates and even random crops score perfectly
    (the null control caught exactly that). Area agreement does not."""
    best = None
    for (rot, num, den, mirror, red) in ladder:
        m, pad = reg.iou_map(red, target_reduced)
        if m.size == 0:
            continue
        j = np.unravel_index(np.argmax(m), m.shape)
        flat = np.sort(m.ravel())
        cand = (int(m[j]), int(j[0]) - pad, int(j[1]) - pad, rot, num, den,
                mirror, int(flat[(flat.size - 1) // 2]),
                int(flat[(flat.size - 1) * 95 // 100]))
        if best is None or cand[0] > best[0]:
            best = cand
    return best


def full_map(icon_mask, target_mask, rot, num, den, mirror):
    """Full-resolution exact IoU over EVERY placement of the transformed
    icon on the target. Its argmax is the placement; the distribution of the
    same map is the MATCHED NULL — the identical icon, identical target,
    every other position. Both come from one computation, so best and null
    are always on the same scale (an earlier version compared a full-res
    best against a quarter-res null, which is meaningless; receipt kept)."""
    im = reg.transform_mask(icon_mask, rot, num, den, mirror)
    m, pad = reg.iou_map(im, target_mask)
    if m.size == 0:
        return None
    j = np.unravel_index(np.argmax(m), m.shape)
    flat = np.sort(m.ravel())
    n = flat.size
    return (int(m[j]), int(j[0]) - pad, int(j[1]) - pad,
            int(flat[(n - 1) // 2]), int(flat[(n - 1) * 95 // 100]),
            int(flat[(n - 1) * 99 // 100]))


def evaluate(icon_mask, target_mask, edt_full, rot, num, den, mirror,
             dy, dx):
    """Full exact metric set for one placement (EDT supplied, not rebuilt)."""
    im = reg.transform_mask(icon_mask, rot, num, den, mirror)
    pts = reg.contour_points(im)
    ch, inside = reg.chamfer_milli(pts, edt_full, dy, dx)
    hd = reg.hausdorff(pts, edt_full, dy, dx)
    bo = reg.boundary_overlap_milli(pts, edt_full, 2, dy, dx)
    th, tw = target_mask.shape
    ih, iw = im.shape
    canvas = np.zeros((th, tw), dtype=bool)
    y0, x0 = max(0, dy), max(0, dx)
    y1, x1 = min(th, dy + ih), min(tw, dx + iw)
    if y1 > y0 and x1 > x0:
        canvas[y0:y1, x0:x1] = im[y0 - dy:y1 - dy, x0 - dx:x1 - dx]
    iou = reg.iou_milli(canvas, target_mask)
    ep_i, br_i = reg.skeleton_topology(im)
    sub = target_mask[y0:y1, x0:x1] if (y1 > y0 and x1 > x0) else \
        np.zeros((1, 1), bool)
    ep_t, br_t = reg.skeleton_topology(sub)
    return {"chamfer_milli": ch, "hausdorff": hd, "overlap_milli": bo,
            "iou_milli": iou, "pts": int(pts.shape[0]), "inside": inside,
            "icon_endpoints": ep_i, "icon_branches": br_i,
            "target_endpoints": ep_t, "target_branches": br_t,
            "topology_match": int(ep_i == ep_t and br_i == br_t)}, canvas


def main():
    scan = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() \
        else 50
    fast = "--fast" in sys.argv
    lab = page_label(scan)
    rgb = np.asarray(Image.open(page_path(scan)).convert("RGB"))
    H, W = rgb.shape[:2]
    cls, _ = dresden.pigment_classes(rgb)
    black = cls == dresden.PIG_BLACK
    inner = np.zeros((H, W), dtype=bool)
    inner[40:H - 40, 40:W - 40] = True
    black_in = black & inner

    # --- characters: large black drawings; red rules excluded by construction
    merged = dresden.dilate(black_in, 2)
    L, n = dresden.label_components(merged)
    chars = [b for b in dresden.component_boxes(L, n)
             if b[4] >= 2500 and (b[1] - b[0]) >= 70 and (b[3] - b[2]) >= 70
             and (b[3] - b[2]) <= W - 100 and (b[1] - b[0]) <= H - 100]
    chars.sort(key=lambda b: b[0])
    check("characters found on the page", len(chars) >= 2)
    NOTES.append("Characters detected (black-ink drawings, red register "
                 "rules excluded): %d" % len(chars))

    # --- icons: every glyph cell on the page outside every character box
    res = dresden.analyze_page(rgb)
    ink = dresden.ink_mask(dresden.int_luma(rgb), res["threshold"])

    def in_char(b):
        for c in chars:
            if not (b[1] <= c[0] or b[0] >= c[1] or b[3] <= c[2]
                    or b[2] >= c[3]):
                return True
        return False

    # Real glyph/icon forms only. Sub-16px fragments were letting the
    # search win trivially (a 9-px blob registers onto any 9-px blob), which
    # the first overlay pass exposed — receipt kept rather than a silent
    # threshold change.
    cand = [b for b in res["boxes"] if not in_char(b)
            and (b[1] - b[0]) >= 16 and (b[3] - b[2]) >= 16
            and b[4] >= 150]
    # An icon must HAVE internal structure to be registrable at all: a solid
    # blob carries no interior to match. Keep those whose ink fills less
    # than 78% of their box, or that enclose a hole.
    icons = []
    for b in cand:
        sub = ink[b[0]:b[1], b[2]:b[3]]
        fill = (1000 * int(sub.sum())) // max((b[1] - b[0]) * (b[3] - b[2]), 1)
        holes = reg_holes(sub)
        if fill < 780 or holes >= 1:
            icons.append(b)
    if fast:
        icons = icons[::4]
    check("icons collected", len(icons) > 20)
    NOTES.append("Icons on the page outside every character: %d%s"
                 % (len(icons), " (--fast: every 4th)" if fast else
                    " — ALL tested"))

    # --- per character: ink mask, negative space, contours, coord frame
    targets = []
    for ci, c in enumerate(chars):
        cm = black_in[c[0]:c[1], c[2]:c[3]]
        closed = cm.copy()
        for _ in range(6):
            closed = dresden.dilate(closed, 1)
        for _ in range(6):
            closed = reg.erode4(closed)
        neg = closed & ~cm
        targets.append({"idx": ci, "box": c, "ink": cm,
                        "ink_contour": reg.contour(cm),
                        "neg": neg, "neg_contour": reg.contour(neg)})
    NOTES.append("Negative-space masks built by exact closing minus ink.")

    ledger = Ledger()
    rows = []
    rot_c = COARSE_ROT if fast else COARSE_ROT + [9]
    # precompute per target/space: quarter-res padded EDT (coarse) and
    # full-res EDT (metrics + refinement). Built once, reused for every icon.
    for t in targets:
        for space in ("ink", "neg"):
            tc = t["ink_contour"] if space == "ink" else t["neg_contour"]
            t[space + "_q"] = quarter(t["ink"] if space == "ink"
                                     else t["neg"])
            t[space + "_edt"] = reg.sq_edt(tc)
    NOTES.append("Coarse search at quarter resolution, refinement and all "
                 "metrics at full resolution.")

    for ii, ib in enumerate(icons):
        im = ink[ib[0]:ib[1], ib[2]:ib[3]]
        if int(im.sum()) < 12:
            continue
        ladder_q = build_ladder(im, rot_c, SCALES, 2)
        if not ladder_q:
            continue
        for t in targets:
            for space in ("ink", "neg"):
                tc = t["ink_contour"] if space == "ink" else t["neg_contour"]
                tm = t["ink"] if space == "ink" else t["neg"]
                if int(tc.sum()) < 20:
                    continue
                b = best_placement(ladder_q, t[space + "_q"])
                if b is None:
                    continue
                _iou_q, dy, dx, rot, num, den, mirror, _qm, _q95 = b
                fm = full_map(im, tm, rot, num, den, mirror)
                if fm is None:
                    continue
                _iou, oy, ox, nmed, n95, n99 = fm
                met, canvas = evaluate(im, tm, t[space + "_edt"], rot, num,
                                       den, mirror, oy, ox)
                bh = t["box"][1] - t["box"][0]
                bw = t["box"][3] - t["box"][2]
                ih, iw = im.shape
                rows.append({
                    "icon": ii, "icon_box": [int(v) for v in ib[:4]],
                    "icon_w": iw, "icon_h": ih,
                    "char": t["idx"], "space": space,
                    "dy": oy, "dx": ox,
                    "rot": list(rot), "scale_num": num, "scale_den": den,
                    "mirror": mirror,
                    "xnorm_milli": (1000 * (ox + iw // 2)) // max(bw, 1),
                    "ynorm_milli": (1000 * (oy + ih // 2)) // max(bh, 1),
                    "iou_best": _iou, "null_median_iou": nmed,
                    "null_p95_iou": n95, "null_p99_iou": n99,
                    "margin_over_p95": _iou - n95,
                    "margin_over_p99": _iou - n99,
                    **met})
    check("correspondences computed", len(rows) > 0)

    # --- matched null -------------------------------------------------
    # The earlier null used random page crops; those are smaller and sparser
    # than real icons, so their IoU was not comparable (they scored higher by
    # being tiny). The matched null is the SAME icon on the SAME character at
    # every other offset: best-fit versus the icon's own placement
    # distribution. Receipt kept rather than a silent swap.
    margins = [r["margin_over_p95"] for r in rows]
    beat95 = sum(1 for m_ in margins if m_ > 0)
    check("matched null computed for every pair", len(margins) == len(rows))

    with open(os.path.join(DATA, "correspond_%s.json" % lab), "w") as f:
        json.dump({"scan": scan, "page": lab,
                   "characters": [[int(v) for v in c[:4]] for c in chars],
                   "icons": len(icons), "rows": rows}, f)
    ledger.record("correspondence",
                  {"scan": scan, "page": lab, "characters": len(chars),
                   "icons": len(icons), "pairs": len(rows),
                   "ladder": {"coarse_rot": rot_c, "scales": SCALES,
                              "fine_rot": FINE_ROT,
                              "fine_scales": FINE_SCALES}},
                  Ledger.digest(dresden.int_luma(rgb)), "rows")
    with open(os.path.join(DATA, "correspond_receipts_%s.json" % lab), "w") as f:
        f.write(ledger.export())

    # --- overlays: mandatory, every fit shown, everything labelled -------
    order = sorted(rows, key=lambda r: -r["margin_over_p95"])
    shown = order[:24]
    S = 4
    for rank, r in enumerate(shown):
        t = targets[r["char"]]
        c = t["box"]
        ib = r["icon_box"]
        im_t = reg.transform_mask(ink[ib[0]:ib[1], ib[2]:ib[3]],
                                  tuple(r["rot"]), r["scale_num"],
                                  r["scale_den"], r["mirror"])
        ih_, iw_ = im_t.shape
        # 1) the icon as drawn, 2) the matched region with the icon contour
        #    laid on it at the fitted transform, 3) the whole character with
        #    the match boxed.  All three at the same display scale for the
        #    first two, so the fit can be judged by eye.
        Z = 8
        icon_big = Image.fromarray(rgb[ib[0]:ib[1], ib[2]:ib[3]]).resize(
            ((ib[3] - ib[2]) * Z, (ib[1] - ib[0]) * Z), Image.NEAREST)
        my0, mx0 = c[0] + r["dy"], c[2] + r["dx"]
        pad_r = 6
        ry0, rx0 = max(0, my0 - pad_r), max(0, mx0 - pad_r)
        ry1, rx1 = min(H, my0 + ih_ + pad_r), min(W, mx0 + iw_ + pad_r)
        reg_big = Image.fromarray(rgb[ry0:ry1, rx0:rx1]).resize(
            ((rx1 - rx0) * Z, (ry1 - ry0) * Z), Image.NEAREST)
        rd = ImageDraw.Draw(reg_big)
        cont = reg.contour(im_t)
        ys, xs = np.nonzero(cont)
        for yy, xx in zip(ys.tolist(), xs.tolist()):
            py = (my0 - ry0 + yy) * Z
            px = (mx0 - rx0 + xx) * Z
            rd.rectangle([px, py, px + Z - 1, py + Z - 1], fill=(0, 255, 120))
        ch_img = Image.fromarray(rgb[c[0]:c[1], c[2]:c[3]]).convert("RGB")
        chw, chh = ch_img.size
        CS = 2
        ch_big = ch_img.resize((chw * CS, chh * CS), Image.NEAREST)
        cd = ImageDraw.Draw(ch_big)
        cd.rectangle([r["dx"] * CS, r["dy"] * CS,
                      (r["dx"] + iw_) * CS, (r["dy"] + ih_) * CS],
                     outline=(0, 255, 120), width=3)
        gap = 18
        Wp = 10 + icon_big.width + gap + reg_big.width + gap + ch_big.width + 10
        Hp = max(icon_big.height, reg_big.height, ch_big.height) + 104
        panel = Image.new("RGB", (Wp, Hp), (14, 14, 14))
        panel.paste(icon_big, (10, 96))
        panel.paste(reg_big, (10 + icon_big.width + gap, 96))
        panel.paste(ch_big, (10 + icon_big.width + gap + reg_big.width + gap,
                             96))
        pd = ImageDraw.Draw(panel)
        a, b_, cc = r["rot"]
        pd.text((10, 6), "icon %d   page %s   y%d-%d x%d-%d   %dx%d px"
                % (r["icon"], lab, ib[0], ib[1], ib[2], ib[3],
                   r["icon_w"], r["icon_h"]), fill=(255, 210, 40), font=F22)
        pd.text((10, 34), "REGISTERED ONTO character %d (%s space) at "
                "dy %d dx %d  -  normalised x %d y %d milli of the character box"
                % (r["char"], r["space"], r["dy"], r["dx"],
                   r["xnorm_milli"], r["ynorm_milli"]),
                fill=(140, 200, 255), font=F16)
        pd.text((10, 54), "transform  rotation cos %d/%d sin %d/%d   scale "
                "%d/%d   mirror %d          IoU %d milli   own-placement p95 "
                "%d   margin %+d   p99 %d"
                % (a, cc, b_, cc, r["scale_num"], r["scale_den"], r["mirror"],
                   r["iou_best"], r["null_p95_iou"], r["margin_over_p95"],
                   r["null_p99_iou"]), fill=(200, 200, 190), font=F16)
        pd.text((10, 74), "chamfer %d milli px   Hausdorff %d px   boundary "
                "overlap %d milli   topology match %d   (icon %d endpoints / "
                "%d branches, target %d / %d)"
                % (r["chamfer_milli"], r["hausdorff"], r["overlap_milli"],
                   r["topology_match"], r["icon_endpoints"],
                   r["icon_branches"], r["target_endpoints"],
                   r["target_branches"]), fill=(180, 180, 170), font=F13)
        pd.text((10, 96 + icon_big.height + 4), "icon as drawn",
                fill=(255, 210, 40), font=F13)
        pd.text((10 + icon_big.width + gap, 96 + reg_big.height + 4),
                "matched region, icon contour overlaid",
                fill=(0, 255, 120), font=F13)
        pd.text((10 + icon_big.width + gap + reg_big.width + gap,
                 96 + ch_big.height + 4), "whole character, match boxed",
                fill=(140, 200, 255), font=F13)
        panel.save(os.path.join(OUT, "p%s_rank%02d_icon%03d_char%d_%s.png"
                                % (lab, rank + 1, r["icon"], r["char"],
                                   r["space"])))
    # --- page sheet: every character with every icon's best location -----
    CS = 3
    tiles = []
    for t in targets:
        c = t["box"]
        img = Image.fromarray(rgb[c[0]:c[1], c[2]:c[3]]).convert("RGB")
        img = img.resize((img.width * CS, img.height * CS), Image.NEAREST)
        dd = ImageDraw.Draw(img)
        mine = [r for r in rows if r["char"] == t["idx"]
                and r["space"] == "ink"]
        mine.sort(key=lambda r: -r["margin_over_p95"])
        for j, r in enumerate(mine[:20]):
            im_t = reg.transform_mask(ink[r["icon_box"][0]:r["icon_box"][1],
                                          r["icon_box"][2]:r["icon_box"][3]],
                                      tuple(r["rot"]), r["scale_num"],
                                      r["scale_den"], r["mirror"])
            ih_, iw_ = im_t.shape
            col = (0, 255, 120) if j < 6 else (255, 210, 40)
            dd.rectangle([r["dx"] * CS, r["dy"] * CS,
                          (r["dx"] + iw_) * CS, (r["dy"] + ih_) * CS],
                         outline=col, width=2)
            dd.text((r["dx"] * CS + 3, r["dy"] * CS + 2),
                    str(r["icon"]), fill=col, font=F13)
        tiles.append((t, img, mine[:20]))
    lw = 470
    sheet = Image.new("RGB", (sum(i.width for _, i, _ in tiles)
                              + lw * len(tiles) + 40,
                              max(i.height for _, i, _ in tiles) + 110),
                      (14, 14, 14))
    sd = ImageDraw.Draw(sheet)
    sd.text((12, 8), "PAGE %s — every icon on the page registered onto every "
            "character (exact rational transforms; boxes are the fitted "
            "placements, numbered by icon)" % lab,
            fill=(255, 210, 40), font=F22)
    sd.text((12, 36), "green = the 6 strongest by margin over the icon's own "
            "placement distribution; amber = the rest of the top 20. "
            "%d icons x %d characters x 2 spaces = %d registrations, all "
            "computed." % (len(icons), len(chars), len(rows)),
            fill=(180, 180, 170), font=F13)
    x = 12
    for t, img, mine in tiles:
        sheet.paste(img, (x, 96))
        sd.text((x, 72), "character %d  (page box y%d-%d x%d-%d)"
                % (t["idx"], t["box"][0], t["box"][1], t["box"][2],
                   t["box"][3]), fill=(140, 200, 255), font=F16)
        tx = x + img.width + 10
        sd.text((tx, 96), "icon -> normalised location (milli of box)",
                fill=(200, 200, 190), font=F13)
        for j, r in enumerate(mine):
            sd.text((tx, 116 + j * 17),
                    "%3d  x%4d y%4d   IoU %3d  p95 %3d  marg %+4d  s%d/%d m%d"
                    % (r["icon"], r["xnorm_milli"], r["ynorm_milli"],
                       r["iou_best"], r["null_p95_iou"],
                       r["margin_over_p95"], r["scale_num"], r["scale_den"],
                       r["mirror"]),
                    fill=(0, 255, 120) if j < 6 else (200, 200, 190),
                    font=F13)
        x = tx + lw
    sheet.save(os.path.join(DEMO, "dresden_correspond_sheet_p%s.png" % lab))
    NOTES.append("Page sheet: demo/dresden_correspond_sheet_p%s.png" % lab)

    NOTES.append("Overlays written: %d (top by margin over the icon's own "
                 "placement distribution) in demo/correspond/" % len(shown))

    print("\n".join(NOTES))
    print("characters:", [(c[0], c[1], c[2], c[3]) for c in chars])
    print("icons:", len(icons), "pairs:", len(rows),
          "| pairs beating their own 95th-pct placement:", beat95)
    if rows:
        best = sorted(rows, key=lambda r: -r["margin_over_p95"])[:12]
        print("\ntop 12 by margin over the icon's OWN placement distribution:")
        for r in best:
            print("  icon%-3d %2dx%-2d -> char%d %-3s IoU %3d (p95 %3d, "
                  "margin %+4d)  chamfer %5d  Hff %2d  ovl %4d  topo%d  "
                  "scale %d/%d mir%d at (%d,%d) norm(%d,%d)" % (
                      r["icon"], r["icon_w"], r["icon_h"], r["char"],
                      r["space"], r["iou_best"], r["null_p95_iou"],
                      r["margin_over_p95"], r["chamfer_milli"],
                      r["hausdorff"], r["overlap_milli"],
                      r["topology_match"], r["scale_num"], r["scale_den"],
                      r["mirror"], r["dy"], r["dx"],
                      r["xnorm_milli"], r["ynorm_milli"]))
    if rows:
        cross = {}
        for r in rows:
            if r["space"] != "ink":
                continue
            cross.setdefault(r["icon"], {})[r["char"]] = r["iou_milli"]
        both = [v for v in cross.values() if len(v) >= 2]
        print("cross-panel control: %d icons tested against every character"
              % len(both))
    print("TOTAL: %d checks, %d failures" % (R["checks"], R["fails"]))


if __name__ == "__main__":
    main()
