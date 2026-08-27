"""Pigment lens + shadow lens + localization of the researcher's new exhibits.

The researcher's latest exhibits point at three things the machine did not
yet serve: the Maya-blue painted regions (a full blue glyph column), the
red streaks that run down page folds, and a hand-made SHADOWS adjustment
used to make patterns visible. This run adds all three as machinery:

  L1 pigment lens  — `dresden.pigment_classes`: exact 4-way partition
     (substrate / carbon black / red / blue) by stated integer margins;
     palette render per page; per-page pigment fractions; a codex-wide
     catalog of blue regions (components of the blue class).
  L2 shadow lens   — `highlight_freeze` windowed on the dark end
     (30..500 milli): the exact counterpart of the researcher's manual
     shadows slider, one per page.
  L3 localization  — both new phone exhibits located mechanically with the
     edge-orientation localizer (UI chrome cropped by stated fractions).

Usage: python3 analysis/dresden_pigment.py
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
PDIR = os.path.join(DATA, "derived", "pigment")
DEMO = os.path.join(ROOT, "demo")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(PDIR, exist_ok=True)

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
fix = np.zeros((4, 4, 3), dtype=np.uint8)
fix[0, :] = (200, 60, 50)     # red
fix[1, :] = (40, 120, 140)    # blue/teal
fix[2, :] = (20, 20, 20)      # black
fix[3, :] = (220, 210, 190)   # substrate
cls, thr = dresden.pigment_classes(fix)
check("pigment fixture classes exact",
      [int(v) for v in cls[:, 0]] == [dresden.PIG_RED, dresden.PIG_BLUE,
                                      dresden.PIG_BLACK, dresden.PIG_SUBSTRATE])
fr = dresden.pigment_fractions_milli(cls)
check("pigment fractions sum to 1000", sum(fr) == 1000)

PIG_COLORS = [(232, 223, 206), (25, 22, 18), (166, 59, 42), (79, 163, 165)]

# --- codex sweep: pigment + shadow lenses ---------------------------------
ledger = Ledger()
rows = []
blue_regions = []   # (area, scan, box)
for k in range(1, 79):
    rgb = np.asarray(Image.open(page_path(k)).convert("RGB"))
    y = dresden.int_luma(rgb)
    cls, thr = dresden.pigment_classes(rgb)
    fr = dresden.pigment_fractions_milli(cls)

    img = np.zeros((cls.shape[0], cls.shape[1], 3), dtype=np.uint8)
    for c, col in enumerate(PIG_COLORS):
        img[cls == c] = col
    Image.fromarray(img[::2, ::2]).save(
        os.path.join(PDIR, "scan%02d_pigment.png" % k))

    sh, lo, hi = dresden.highlight_freeze(y, 30, 500)
    g = sh.astype(np.uint8)
    Image.fromarray(np.stack([g, g, g], axis=2)[::2, ::2]).save(
        os.path.join(PDIR, "scan%02d_shadow.jpg" % k), quality=80)

    blabels, bn = dresden.label_components(cls == dresden.PIG_BLUE)
    for b in dresden.component_boxes(blabels, bn):
        if b[4] >= 400:
            blue_regions.append((b[4], k, b))
    rows.append((k, fr))
    ledger.record("pigment_shadow",
                  {"scan": k, "page": page_label(k), "fractions": fr,
                   "shadow_window": [int(lo), int(hi)],
                   "rules": "red R-max(G,B)>=24; blue min(G,B)-R>=12"},
                  Ledger.digest(y), Ledger.digest(cls))

check("pigment sweep covered all pages", len(rows) == 78)
blue_regions.sort(reverse=True)
check("blue regions catalogued", len(blue_regions) > 50)

# blue-region overview panel: top 8 regions cropped
panel = Image.new("RGB", (4 * 190, 2 * 330 + 20), (12, 12, 12))
pd = ImageDraw.Draw(panel)
for i, (area, k, b) in enumerate(blue_regions[:8]):
    im = Image.open(page_path(k)).convert("RGB").crop(
        (max(0, b[2] - 6), max(0, b[0] - 6), b[3] + 6, b[1] + 6))
    im.thumbnail((180, 300))
    x0, y0 = (i % 4) * 190 + 5, 20 + (i // 4) * 330
    panel.paste(im, (x0, y0))
    pd.text((x0, y0 - 14), "p%s a=%d" % (page_label(k), area),
            fill=(79, 163, 165))
pd.text((4, 2), "largest Maya-blue regions (exact chroma partition)",
        fill=(232, 223, 206))
panel.save(os.path.join(DEMO, "dresden_blue_regions.png"))

# --- localize the two new exhibits ----------------------------------------
UP = "/root/.claude/uploads/ab8d2710-9856-5c5b-93ef-8366ff17d46f"
"""Crops exclude phone UI chrome and neighbour-page slivers (stated
fractions); scale ranges sized to the cropped content. First attempt used
a loose crop + short scale range and mis-localized exhibit A to p49 with a
thin margin — caught by the mandatory visual verification, corrected here.
Verify-then-accept is part of the machine now."""
EXHIBITS = [
    ("exhibit A (WDL viewer screenshot, blue column + figures)",
     os.path.join(UP, "57247334-image.jpg"), (30, 14, 97, 62),
     (260, 320, 380, 440, 500, 560, 620)),
    ("exhibit B (researcher's SHADOWS adjustment, right page-half)",
     os.path.join(UP, "0bdb89db-image.jpg"), (50, 8, 87, 80),
     (150, 190, 230, 270, 310, 360)),
]
pooled = {k: dresden.pool_planes(dresden.orientation_planes(
    dresden.int_luma(np.asarray(Image.open(page_path(k)).convert("RGB")))), 8)
    for k in range(1, 79)}

loc_results = []
for name, path, (x0p, y0p, x1p, y1p), scales in EXHIBITS:
    if not os.path.exists(path):
        L.append("- %s: file not present in this container; skipped." % name)
        continue
    im = Image.open(path).convert("RGB")
    W, H = im.size
    tpl = im.crop((W * x0p // 100, H * y0p // 100,
                   W * x1p // 100, H * y1p // 100))
    best = None
    for tw in scales:
        th = tw * tpl.size[1] // tpl.size[0]
        if th > 1349:
            continue
        t = dresden.int_luma(np.asarray(
            tpl.resize((tw, th), Image.LANCZOS).convert("RGB")))
        tp = dresden.pool_planes(dresden.orientation_planes(t), 8)
        tc = max(int(tp.sum()), 1)
        for mir in (0, 1):
            tq = dresden.mirror_planes(tp) if mir else tp
            for k in range(1, 79):
                sc = dresden.cooccurrence_map(pooled[k], tq)
                if sc.size == 0:
                    continue
                j = np.unravel_index(np.argmax(sc), sc.shape)
                cand = (1000 * int(sc[j]) // tc, k, tw, mir,
                        int(j[1]) * 8, int(j[0]) * 8)
                if best is None or cand[0] > best[0]:
                    best = cand
                    runner = None
    # runner-up on a different page, same scale set
    others = []
    for tw in (best[2],):
        th = tw * tpl.size[1] // tpl.size[0]
        t = dresden.int_luma(np.asarray(
            tpl.resize((tw, th), Image.LANCZOS).convert("RGB")))
        tp = dresden.pool_planes(dresden.orientation_planes(t), 8)
        tc = max(int(tp.sum()), 1)
        tq = dresden.mirror_planes(tp) if best[3] else tp
        for k in range(1, 79):
            if k == best[1]:
                continue
            sc = dresden.cooccurrence_map(pooled[k], tq)
            if sc.size == 0:
                continue
            others.append(1000 * int(sc.max()) // tc)
    margin = best[0] - max(others) if others else 0
    loc_results.append((name, best, margin))
    L.append("- %s -> scan %d (p%s) at (%d, %d), tw=%d, mir=%d, milli %d, "
             "margin %+d over best other page." % (
                 name, best[1], page_label(best[1]), best[4], best[5],
                 best[2], best[3], best[0], margin))
    ledger.record("locate_exhibit",
                  {"exhibit": name, "scan": best[1],
                   "page": page_label(best[1]), "x": best[4], "y": best[5],
                   "milli": best[0], "margin_milli": margin},
                  "search", Ledger.digest(pooled[best[1]]))

check("both exhibits localized with positive margin",
      len(loc_results) == 2 and all(m > 0 for _, _, m in loc_results))
check("both exhibits land on scan 73 (p69) — visually verified this session",
      all(b[1] == 73 for _, b, _ in loc_results))

with open(os.path.join(DATA, "pigment_receipts.json"), "w") as f:
    f.write(ledger.export())

# --- catalog --------------------------------------------------------------
out = [
    "# Pigment + shadow lenses; new exhibits located (researcher follow-up)",
    "",
    "Run: `python3 analysis/dresden_pigment.py`; receipts",
    "`data/dresden/pigment_receipts.json`; renders `data/dresden/derived/pigment/`.",
    "",
    "**%s exact checks, %d failures.**" % ("{:,}".format(R["checks"]), R["fails"]),
    "",
    "Pigment partition rules (exact, stated): RED where R-max(G,B) >= 24;",
    "BLUE where min(G,B)-R >= 12; BLACK where luma < page Otsu and not",
    "red/blue; SUBSTRATE otherwise. Shadow lens: exact freeze window",
    "30..500 milli of each page's own luma (the machine version of the",
    "researcher's manual SHADOWS adjustment), `scanNN_shadow.jpg`.",
    "",
    "## Exhibit localization",
    "",
] + [x for x in L if x.startswith("- ")] + [
    "",
    "## Largest blue regions (top 15)",
    "",
    "| Area px | Scan | Page | Box (y0,y1,x0,x1) |",
    "|---|---|---|---|",
] + ["| %d | %d | %s | (%d,%d,%d,%d) |" % (
        a, k, page_label(k), b[0], b[1], b[2], b[3])
     for a, k, b in blue_regions[:15]] + [
    "",
    "Panel: `demo/dresden_blue_regions.png`.",
    "",
    "## Per-page pigment fractions (milli)",
    "",
    "| Scan | Page | Substrate | Black | Red | Blue |",
    "|---|---|---|---|---|---|",
] + ["| %d | %s | %d | %d | %d | %d |" % (k, page_label(k), *fr)
     for k, fr in rows]
with open(os.path.join(DOCS, "DRESDEN_PIGMENT.md"), "w") as f:
    f.write("\n".join(out) + "\n")

print("\n".join(x for x in L if x.startswith("  FAIL")) or "no FAIL lines")
print("\n".join(x for x in L if x.startswith("- ")))
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
