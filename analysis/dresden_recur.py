"""Cross-page recurrence of ONE researcher-selected glyph, at high resolution.

The researcher pointed at it: p7 element 162 is a merged block of glyph
cartouches, and inside it — cartouche c2 — is a face in profile inside a
dotted oval frame. Their claim: "162 I've seen on other pages." This searches
for it.

Two things are different from every earlier search in this repo:

  1. It runs on the SLUB scans (3874x7649), not the 684x1350 pages embedded
     in the source PDF. At 684 this glyph is 63x31 px and its interior — the
     eye, the snout, the jaw — is not resolved at all. At the working
     resolution here it is 178x87 px.
  2. The template is a glyph the RESEARCHER selected, not one the agent
     surfaced, so the question is theirs and the machine only answers it.

Method: weighted edge-orientation planes, midrank-normalized on both sides
(a phone photograph and a library scan have unrelated tone curves; equalizing
marginals removes that confound), pooled, compared by exact integer cosine so
scores from different pages are on one scale. Dihedral poses are searched,
because a recurring sign need not recur in the same orientation.

Control battery, per docs/RULES_OF_EXPLORATION.md rule 5: the query's own
score distribution across all 78 pages, its score on the near-blank pages,
the self-match as positive control, the hard negative named, and the rank
percentile. "It appears on page X" alone is not a result.

Nothing here is closed and no meaning is assigned to the glyph.

Usage: python3 analysis/dresden_recur.py
"""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import dresden
from cram_dsp.forensics import Ledger

Image.MAX_IMAGE_PIXELS = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "dresden")
HI = os.path.join(DATA, "hires")
OUT = os.path.join(DATA, "derived", "recur")
DEMO = os.path.join(ROOT, "demo")
os.makedirs(OUT, exist_ok=True)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                       22)
FB = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)

WORK_W = 1937           # working width: half the SLUB scan, 2.8x the PDF page
POOL = 6
BLANKS = (29, 30, 31, 64)

# p7 element 162, cartouche c2 — in SLUB page-07 pixel coordinates
QUERY = {"page": 7, "y0": 4960, "y1": 5134, "x0": 1337, "x1": 1693,
         "label": "p7 el.162 c2 — face in profile inside a dotted oval"}


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


def hires(k):
    return Image.open(os.path.join(HI, "slub_p%02d.jpg" % k)).convert("RGB")


def work(im):
    return im.resize((WORK_W, im.height * WORK_W // im.width), Image.LANCZOS)


def planes_of(luma):
    return dresden.pool_planes(
        dresden.orientation_planes_weighted(
            dresden.midrank_normalize(luma)), POOL)


def main():
    q = QUERY
    src = hires(q["page"])
    sc = src.width / WORK_W          # SLUB px per working px
    tpl_full = src.crop((q["x0"], q["y0"], q["x1"], q["y1"]))
    tw = max(8, int((q["x1"] - q["x0"]) / sc))
    th = max(8, int((q["y1"] - q["y0"]) / sc))
    print("query %s\n  SLUB %dx%d px -> working %dx%d px"
          % (q["label"], tpl_full.width, tpl_full.height, tw, th), flush=True)
    tpl_full.save(os.path.join(OUT, "query.png"))

    # dihedral poses of the template: a recurring sign need not recur upright
    poses = []
    for rot in (0, 90, 180, 270):
        for mir in (0, 1):
            im = tpl_full.rotate(rot, expand=True) if rot else tpl_full
            if mir:
                im = im.transpose(Image.FLIP_LEFT_RIGHT)
            w = max(8, int(im.width / sc))
            h = max(8, int(im.height / sc))
            lm = dresden.int_luma(np.asarray(
                im.resize((w, h), Image.LANCZOS).convert("RGB")))
            poses.append(("r%dm%d" % (rot, mir),
                          planes_of(dresden.midrank_normalize(lm))))

    rows = []
    for k in range(1, 79):
        pl = planes_of(dresden.int_luma(np.asarray(work(hires(k)))))
        best = None
        for name, tp in poses:
            s = dresden.cooccurrence_normalized(pl, tp)
            if s.size == 0:
                continue
            j = np.unravel_index(np.argmax(s), s.shape)
            cand = (int(s[j]), name, int(j[1]) * POOL, int(j[0]) * POOL)
            if best is None or cand[0] > best[0]:
                best = cand
        rows.append({"scan": k, "page": page_label(k), "milli": best[0],
                     "pose": best[1], "wx": best[2], "wy": best[3],
                     "sx": int(best[2] * sc), "sy": int(best[3] * sc)})
        print("  scan %2d p%-4s %4d  %s" % (k, page_label(k), best[0],
                                            best[1]), flush=True)

    rows.sort(key=lambda r: -r["milli"])
    with open(os.path.join(OUT, "ranking.json"), "w") as f:
        json.dump({"query": q, "work_w": WORK_W, "pool": POOL,
                   "rows": rows}, f, indent=1)

    sc_all = [r["milli"] for r in rows]
    med = sorted(sc_all)[len(sc_all) // 2]
    self_row = [r for r in rows if r["scan"] == q["page"]][0]
    others = [r for r in rows if r["scan"] != q["page"]]
    blanks = [r for r in rows if r["scan"] in BLANKS]
    print("\nCONTROL BATTERY")
    print("  positive control (self, scan %d): %d/1000, rank %d of 78"
          % (q["page"], self_row["milli"], rows.index(self_row) + 1))
    print("  best OTHER page: scan %d (p%s) %d/1000  [hard negative]"
          % (others[0]["scan"], others[0]["page"], others[0]["milli"]))
    print("  median over 78 pages: %d   min: %d" % (med, min(sc_all)))
    print("  best near-blank page: %d  (gap %+d under best other)"
          % (max(r["milli"] for r in blanks),
             others[0]["milli"] - max(r["milli"] for r in blanks)))

    ledger = Ledger()
    ledger.record("recurrence", {"query": q, "work_w": WORK_W,
                                 "self_milli": self_row["milli"],
                                 "best_other": others[0]["milli"],
                                 "median": med,
                                 "blank_best": max(r["milli"]
                                                   for r in blanks)},
                  "search", Ledger.digest(np.asarray(tpl_full.convert("L"))))
    with open(os.path.join(OUT, "receipts.json"), "w") as f:
        f.write(ledger.export())

    # contact sheet: the query, then the top matches, all at SLUB resolution
    top = [self_row] + others[:11]
    TH = 300
    tiles = []
    for r in top:
        im = hires(r["scan"])
        s2 = im.width / WORK_W
        pw, ph = int(tw * s2), int(th * s2)
        x, y = r["sx"], r["sy"]
        c = im.crop((max(0, x - 20), max(0, y - 20),
                     min(im.width, x + pw + 20), min(im.height, y + ph + 20)))
        c = c.resize((int(c.width * TH / c.height), TH), Image.LANCZOS)
        t = Image.new("RGB", (max(c.width, 300), TH + 62), (14, 14, 14))
        t.paste(c, (0, 62))
        d = ImageDraw.Draw(t)
        tag = "QUERY PAGE (positive control)" if r["scan"] == q["page"] \
            else "scan %d / p%s" % (r["scan"], r["page"])
        d.text((4, 4), tag, fill=(0, 235, 120) if r["scan"] == q["page"]
               else (255, 205, 60), font=F)
        d.text((4, 30), "cosine %d/1000  pose %s" % (r["milli"], r["pose"]),
               fill=(210, 210, 210), font=F)
        tiles.append(t)
    cols = 4
    rws = (len(tiles) + cols - 1) // cols
    cw = max(t.width for t in tiles) + 10
    sheet = Image.new("RGB", (cols * cw, rws * (TH + 72) + 92), (14, 14, 14))
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), "RECURRENCE of %s" % q["label"], fill=(240, 240, 240),
           font=FB)
    d.text((10, 44), "Searched all 78 pages at %d px working width from the "
                     "SLUB 3874x7649 scans, 8 dihedral poses, exact integer "
                     "cosine. Median over pages %d/1000."
           % (WORK_W, med), fill=(150, 150, 150), font=F)
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * cw + 5, 92 + (i // cols) * (TH + 72)))
    sheet.save(os.path.join(DEMO, "dresden_recur_p7_162c2.jpg"), quality=86,
               optimize=True)
    print("\nsheet written")


if __name__ == "__main__":
    main()
