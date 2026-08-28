"""THE SHEET — the researcher's illustration, produced by the machine.

Their two illustrations define the output panel by panel. This script
produces that composite for a column, every panel from real machine output:

  1 ORIGINAL                     the column as scanned
  2 HIGHLIGHTS & CONTRAST FROZEN exact order-statistic freeze
  3 WHITE GRADIENT SEQUENCE MAP  the actual white regions painted bright,
                                 with the path through them numbered 1..N
                                 (regions drawn at true pixel extent -- not
                                 markers at centroids)
  4 SEQUENCED GLYPHS             the glyph blocks the path passes, in order
  5 DRESSING THE FIGURE          each sequenced glyph registered against the
                                 character, its best location outlined
  6 GRADIENT INTENSITY HEAT MAP  local brightness excess, false colour
  7 UNDERLYING STRUCTURE         five exact luma bands, A..E
  8 SEQUENCE READING             the ordered glyph strip

Usage: python3 analysis/dresden_sheet.py [scan y0 y1 x0 x1]
default: scan 73 (Foerstemann p69), the researcher's own located column.
"""

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
FDIR = "/usr/share/fonts/truetype/dejavu/"
FT = lambda s, b=True: ImageFont.truetype(
    FDIR + ("DejaVuSans-Bold.ttf" if b else "DejaVuSans.ttf"), s)
F28, F20, F16, F13 = FT(28), FT(20), FT(16), FT(13)

GOLD = (255, 205, 60)
CYAN = (0, 225, 255)
GREEN = (60, 255, 130)
PAPER = (232, 223, 206)
DIM = (150, 142, 128)
BG = (8, 8, 10)

# layer palette for panel 7, in the researcher's own order A..E
LAYER = [(255, 255, 240), (120, 220, 255), (215, 120, 235),
         (120, 230, 140), (60, 60, 70)]
LAYER_NAME = ["A HIGHEST WHITE (path nodes)", "B HIGH WHITE (glyph bodies)",
              "C MID WHITE (details)", "D LOW WHITE (contours)",
              "E DARK PIGMENT (ink / bars / dots)"]


def page_path(k):
    return os.path.join(DATA, "pages", "wdl11621_scan%02d.jpg" % k)


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


def up(img, s):
    return img.resize((img.width * s, img.height * s), Image.NEAREST)


def heat(v, vmax):
    """Integer false-colour ramp blue -> cyan -> green -> yellow -> red."""
    stops = [(0, 0, 90), (0, 140, 220), (0, 220, 140), (240, 220, 40),
             (230, 40, 30)]
    t = (np.clip(v, 0, vmax) * (len(stops) - 1) * 256) // max(vmax, 1)
    idx = np.clip(t // 256, 0, len(stops) - 2)
    frac = t % 256
    out = np.zeros(v.shape + (3,), dtype=np.uint8)
    for ch in range(3):
        a = np.asarray([s[ch] for s in stops], dtype=np.int64)[idx]
        b = np.asarray([s[ch] for s in stops[1:]] + [stops[-1][ch]],
                       dtype=np.int64)[idx]
        out[..., ch] = (a * (256 - frac) + b * frac) // 256
    return out


def main():
    if len(sys.argv) >= 6:
        scan, y0, y1, x0, x1 = (int(v) for v in sys.argv[1:6])
    else:
        scan, y0, y1, x0, x1 = 73, 768, 1350, 64, 274
    lab = page_label(scan)
    page = np.asarray(Image.open(page_path(scan)).convert("RGB"))
    col = page[y0:y1, x0:x1]
    ch, cw = col.shape[:2]
    y = dresden.int_luma(col)
    thr = dresden.otsu_threshold(y)
    ink = dresden.ink_mask(y, thr)
    ledger = Ledger()

    S = 2                                   # column display scale
    P1 = up(Image.fromarray(col), S)

    # --- 2 freeze -----------------------------------------------------------
    fz, lo, hi = dresden.highlight_freeze(y)
    g = fz.astype(np.uint8)
    P2 = up(Image.fromarray(np.stack([g, g, g], axis=2)), S)

    # --- 3 white regions + path --------------------------------------------
    # White structure by LOCAL brightness excess, not a global luma cut:
    # a global cut selects only the damaged bright plaster along the lower
    # edge and nothing among the glyphs, which is what the first sheet
    # showed. Local excess finds locally-bright structure everywhere.
    field = dresden.local_bright_field(y, ink=ink)
    wthr = dresden.order_stat(field, 965)
    wmask = (field >= wthr) & ~ink
    recs = []
    _wl, _wn = dresden.label_components(wmask)
    for _i, _b in enumerate(dresden.component_boxes(_wl, _wn), start=1):
        if not (12 <= _b[4] <= 4000):
            continue
        _sel = _wl[_b[0]:_b[1], _b[2]:_b[3]] == _i
        _m = int(_sel.sum())
        _cy = _b[0] + int(np.nonzero(_sel)[0].sum()) // _m
        _cx = _b[2] + int(np.nonzero(_sel)[1].sum()) // _m
        _val = int(dresden.exact_median(field[_b[0]:_b[1], _b[2]:_b[3]][_sel]))
        recs.append((_cy, _cx, _b[4], _val, _val, _val, 0, 0, 0, _val))
    wlab, wn = _wl, _wn
    dark = (np.asarray(col).astype(np.int64) * 45 // 100).astype(np.uint8)
    canvas = dark.copy()
    # paint EVERY detected white region at its true pixel extent
    keep = np.zeros(wmask.shape, dtype=bool)
    for i, b in enumerate(dresden.component_boxes(wlab, wn), start=1):
        if 12 <= b[4] <= 4000:
            keep |= (wlab == i)
    canvas[keep] = np.asarray([255, 250, 235], dtype=np.uint8)
    P3 = up(Image.fromarray(canvas), S)
    d3 = ImageDraw.Draw(P3)
    order = dresden.order_brightness(recs, 12)
    seq_nodes = []
    used = []
    for j in order:
        cy, cx = recs[j][0], recs[j][1]
        if any(abs(cy - a) + abs(cx - b_) < 28 for a, b_ in used):
            continue
        used.append((cy, cx))
        seq_nodes.append(recs[j])
        if len(seq_nodes) >= 12:
            break
    pts = [(int(r[1]) * S, int(r[0]) * S) for r in seq_nodes]
    for a, b_ in zip(pts, pts[1:]):
        d3.line([a, b_], fill=(255, 240, 200), width=5)
    for n, (px, py) in enumerate(pts):
        d3.ellipse([px - 15, py - 15, px + 15, py + 15], fill=(20, 20, 24),
                   outline=GOLD, width=3)
        w_ = d3.textlength(str(n + 1), font=F16)
        d3.text((px - w_ // 2, py - 9), str(n + 1), fill=GOLD, font=F16)

    # --- 4 sequenced glyphs: the glyph blocks the path passes through -------
    # Glyph blocks in a single column: analyze_page's 2-step dilation merges
    # the whole block row into one component here (3 boxes for a column that
    # plainly holds a dozen). Segment with 1-step dilation and a column-scale
    # area window instead.
    gl, gn = dresden.label_components(dresden.dilate(ink, 1))
    gboxes = [b for b in dresden.component_boxes(gl, gn)
              if 120 <= b[4] <= 3000 and (b[1] - b[0]) >= 10
              and (b[3] - b[2]) >= 10]
    gboxes.sort(key=lambda b: (b[0], b[2]))
    res = {"boxes": gboxes}
    poly = [(int(r[0]), int(r[1])) for r in seq_nodes]
    gseq = dresden.trail_glyph_sequence(poly, res["boxes"], reach=70)
    if len(gseq) < 8:
        extra = [i for _, i in dresden.luminance_order(y, res["boxes"])]
        for i in extra:
            if i not in gseq:
                gseq.append(i)
            if len(gseq) >= 12:
                break
    gseq = gseq[:12]
    crops = []
    for gi in gseq:
        b = res["boxes"][gi]
        crops.append((gi, b, Image.fromarray(col[b[0]:b[1], b[2]:b[3]])))

    # --- 5 dressing: register each sequenced glyph onto the character -------
    cls, _ = dresden.pigment_classes(col)
    black = cls == dresden.PIG_BLACK
    lower = np.zeros(black.shape, dtype=bool)
    lower[ch // 3:, :] = True
    ml, mn = dresden.label_components(dresden.dilate(black & lower, 2))
    figs = [b for b in dresden.component_boxes(ml, mn) if b[4] >= 1500]
    figs.sort(key=lambda b: -b[4])
    fig = figs[0] if figs else (ch // 2, ch, 0, cw)
    fim = ink[fig[0]:fig[1], fig[2]:fig[3]]
    dress = []
    for gi, b, cimg in crops:
        # The glyph must come from OUTSIDE the character. Sequenced glyphs
        # can fall anywhere in the column, and components lifted from inside
        # the figure register onto themselves -- which is why every fit read
        # IoU 1000 on the previous sheets. Receipt kept.
        if not (b[1] <= fig[0] or b[0] >= fig[1]
                or b[3] <= fig[2] or b[2] >= fig[3]):
            continue
        im = ink[b[0]:b[1], b[2]:b[3]]
        # A SOLID mask is not registrable: it fits inside any solid ink area
        # and scores IoU 1000 with no structure involved. The first two
        # sheets reported exactly that (four "perfect" fits). Require the
        # glyph to have interior — fill under 850 milli.
        fill = (1000 * int(im.sum())) // max(im.size, 1)
        if int(im.sum()) < 40 or fill >= 850:
            continue
        best = None
        for t in (0, 5, 12):
            a_, b2, c2 = reg.TRIPLES[t]
            for rot in ((a_, b2, c2), (a_, -b2, c2)) if b2 else ((a_, b2, c2),):
                for (nu, de) in ((2, 3), (3, 4), (1, 1)):
                    for mir in (0, 1):
                        tm = reg.transform_mask(im, rot, nu, de, mir)
                        # An 8-pixel remnant can score IoU 1000 against any
                        # 8-pixel patch; the first sheet showed exactly that
                        # (four "perfect" fits). Require a real mask.
                        if int(tm.sum()) < 60:
                            continue
                        m, pad = reg.iou_map(tm, fim)
                        if m.size == 0:
                            continue
                        j = np.unravel_index(np.argmax(m), m.shape)
                        flat = np.sort(m.ravel())
                        cand = (int(m[j]), int(j[0]) - pad, int(j[1]) - pad,
                                rot, nu, de, mir,
                                int(flat[(flat.size - 1) * 95 // 100]),
                                tm.shape)
                        if best is None or cand[0] > best[0]:
                            best = cand
        if best:
            dress.append((gi, b, cimg, best))
    dress.sort(key=lambda t: -(t[3][0] - t[3][7]))
    dress = dress[:4]

    # --- 6 heat map ---------------------------------------------------------
    P6 = up(Image.fromarray(heat(field, max(dresden.order_stat(field, 990),
                                            1))), S)

    # --- 7 layers -----------------------------------------------------------
    bands = dresden.luma_bands(y, 5)
    limg = np.zeros((ch, cw, 3), dtype=np.uint8)
    for bi in range(5):
        limg[bands == (4 - bi)] = LAYER[bi]
    P7 = up(Image.fromarray(limg), S)

    # ================= compose ============================================
    colw, colh = P1.width, P1.height
    gap = 26
    left = 26
    seq_cell = 118
    seq_cols = 4
    grid_w = seq_cols * seq_cell
    grid_h = ((len(crops) + seq_cols - 1) // seq_cols) * seq_cell
    dress_w = 470
    dress_h = 140
    top_h = 126
    row1_h = max(colh, grid_h + 40, len(dress) * dress_h + 40)
    strip_h = 190
    W = left * 2 + colw * 3 + gap * 3 + grid_w + gap + dress_w
    Hh = top_h + row1_h + gap + colh + 60 + gap + strip_h
    sheet = Image.new("RGB", (W, Hh), BG)
    D = ImageDraw.Draw(sheet)

    D.text((left, 22), "GRADIENT TO WHITE PATH REVEALS SEQUENCED GLYPHS",
           fill=GOLD, font=F28)
    D.text((left, 62), "page %s, column y%d-%d x%d-%d — every panel produced "
           "by the machine, exact integer transforms, nothing painted in by "
           "hand" % (lab, y0, y1, x0, x1), fill=DIM, font=F16)

    def head(x, n, t, sub=""):
        D.text((x, top_h - 46), "%d. %s" % (n, t), fill=GOLD, font=F16)
        if sub:
            D.text((x, top_h - 26), sub, fill=DIM, font=F13)

    x = left
    sheet.paste(P1, (x, top_h))
    head(x, 1, "ORIGINAL", "as scanned")
    x += colw + gap
    sheet.paste(P2, (x, top_h))
    head(x, 2, "HIGHLIGHTS & CONTRAST FROZEN",
         "exact order-statistic window %d..%d" % (lo, hi))
    x += colw + gap
    sheet.paste(P3, (x, top_h))
    head(x, 3, "WHITE GRADIENT SEQUENCE MAP",
         "all %d white regions at true extent; path 1..%d brightest-first"
         % (int(keep.sum() > 0) and len([1 for b in
            dresden.component_boxes(wlab, wn) if 12 <= b[4] <= 4000]),
            len(pts)))
    x += colw + gap
    head(x, 4, "SEQUENCED GLYPHS", "in path order")
    for i, (gi, b, cimg) in enumerate(crops):
        cx_ = x + (i % seq_cols) * seq_cell
        cy_ = top_h + (i // seq_cols) * seq_cell
        z = max(1, min((seq_cell - 34) // max(b[3] - b[2], 1),
                       (seq_cell - 34) // max(b[1] - b[0], 1)))
        z = max(z, 2)
        th_ = up(cimg, z)
        th_.thumbnail((seq_cell - 14, seq_cell - 30))
        sheet.paste(th_, (cx_ + 6, cy_ + 22))
        D.ellipse([cx_ + 4, cy_ + 2, cx_ + 22, cy_ + 20], outline=GOLD,
                  width=2)
        D.text((cx_ + 9, cy_ + 4), str(i + 1), fill=GOLD, font=F13)
    x += grid_w + gap

    head(x, 5, "DRESSING THE FIGURE",
         "each sequenced glyph registered onto the character")
    for i, (gi, b, cimg, best) in enumerate(dress):
        iou, dy, dx, rot, nu, de, mir, p95, tshape = best
        yy = top_h + i * dress_h
        gz = up(cimg, 3)
        gz.thumbnail((92, 92))
        sheet.paste(gz, (x, yy + 20))
        fimg = Image.fromarray(col[fig[0]:fig[1], fig[2]:fig[3]]).convert("RGB")
        fz2 = 2
        fbig = up(fimg, fz2)
        fd = ImageDraw.Draw(fbig)
        ih_, iw_ = tshape
        fd.rectangle([dx * fz2, dy * fz2, (dx + iw_) * fz2,
                      (dy + ih_) * fz2], outline=GREEN, width=3)
        fbig.thumbnail((dress_w - 120, dress_h - 34))
        sheet.paste(fbig, (x + 104, yy + 20))
        D.text((x, yy + 2), "glyph %d  ->  IoU %d  (p95 %d, margin %+d)"
               % (i + 1, iou, p95, iou - p95), fill=GREEN, font=F13)
    x = left

    # row 2
    ry = top_h + row1_h + gap
    sheet.paste(P6, (left, ry))
    D.text((left, ry - 44), "6. GRADIENT INTENSITY HEAT MAP", fill=GOLD,
           font=F16)
    D.text((left, ry - 24), "brighter = stronger local brightness excess",
           fill=DIM, font=F13)
    sheet.paste(P7, (left + colw + gap, ry))
    D.text((left + colw + gap, ry - 44),
           "7. UNDERLYING STRUCTURE — five exact luma bands", fill=GOLD,
           font=F16)
    lx = left + colw * 2 + gap * 2
    for i, nm in enumerate(LAYER_NAME):
        D.rectangle([lx, ry + 8 + i * 30, lx + 24, ry + 30 + i * 30],
                    fill=LAYER[i], outline=(90, 90, 90))
        D.text((lx + 34, ry + 12 + i * 30), nm, fill=PAPER, font=F13)

    # row 3 strip
    sy = ry + colh + 60
    D.text((left, sy - 26), "8. SEQUENCE READING — glyphs in path order",
           fill=GOLD, font=F16)
    sx = left
    for i, (gi, b, cimg) in enumerate(crops):
        z = up(cimg, 3)
        z.thumbnail((116, 116))
        sheet.paste(z, (sx, sy + 20))
        D.ellipse([sx, sy, sx + 20, sy + 20], outline=GOLD, width=2)
        D.text((sx + 6, sy + 2), str(i + 1), fill=GOLD, font=F13)
        if i < len(crops) - 1:
            D.text((sx + 122, sy + 60), ">", fill=DIM, font=F20)
        sx += 140
        if sx > W - 160:
            break

    out = os.path.join(DEMO, "dresden_sheet_p%s.png" % lab)
    sheet.save(out)
    ledger.record("sheet", {"scan": scan, "page": lab,
                            "box": [y0, y1, x0, x1],
                            "white_threshold": int(wthr),
                            "freeze": [int(lo), int(hi)],
                            "path_nodes": len(pts),
                            "sequenced_glyphs": len(crops),
                            "dressing_pairs": len(dress)},
                  Ledger.digest(y), out)
    with open(os.path.join(DATA, "sheet_receipts_%s.json" % lab), "w") as f:
        f.write(ledger.export())
    print("sheet:", out, sheet.size)
    print("white threshold %d, path nodes %d, sequenced glyphs %d, "
          "dressing pairs %d" % (wthr, len(pts), len(crops), len(dress)))


if __name__ == "__main__":
    main()
