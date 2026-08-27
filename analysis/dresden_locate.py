"""Localization of the researcher's photographed column — the fixed matcher.

History, kept on the record: the first matcher (median-centred luma SAD at
1/8 scale) returned a FALSE NEGATIVE for the researcher's photographed
column — blank pages out-scored everything because brightness statistics do
not survive a change of scan generation/colour grade. The researcher called
it: pattern matching was broken. This run is the fix — integer
edge-orientation co-occurrence (`dresden.orientation_planes` /
`dresden.locate`), which matches ink structure instead of brightness.

Expected ground truth (verified visually this session): the column lives on
scan 73 = Förstemann page 69, near (64, 772) at full resolution.

Usage: python3 analysis/dresden_locate.py
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
DEMO = os.path.join(ROOT, "demo")

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


# --- fixtures: the localizer must find a known crop in its own page -------
y10 = load_luma(10)
crop = y10[300:700, 200:360]
score, x, y, mir = dresden.locate(y10, crop)
check("self-crop located at true offset (block quantized)",
      abs(x - 200) <= 8 and abs(y - 300) <= 8 and mir == 0)
score20 = dresden.locate(load_luma(20), crop)[0]
check("true page out-scores a different page on the same crop",
      score > score20)
sm, xm, ym, mirm = dresden.locate(y10, crop[:, ::-1])
check("mirrored crop detected as mirrored at the same spot",
      mirm == 1 and abs(xm - 200) <= 8 and abs(ym - 300) <= 8)

# --- full search: pinned photographed column vs every page ----------------
qimg = Image.open(os.path.join(DATA, "queries", "query_column_photo_q4.png"))
qw, qh = qimg.size
tpl_img = qimg.crop((qw * 13 // 100, qh * 2 // 100,
                     qw * 86 // 100, qh * 99 // 100))

pooled = {}
for k in range(1, 79):
    pooled[k] = dresden.pool_planes(
        dresden.orientation_planes(load_luma(k)), 8)

results = []
tcounts = {}
for tw in (180, 210, 240, 270, 300, 340):
    th = tw * tpl_img.size[1] // tpl_img.size[0]
    if th > 1349:
        continue
    t_luma = dresden.int_luma(np.asarray(
        tpl_img.resize((tw, th), Image.LANCZOS).convert("RGB")))
    tp = dresden.pool_planes(dresden.orientation_planes(t_luma), 8)
    tcounts[tw] = max(int(tp.sum()), 1)
    for mir in (0, 1):
        tq = dresden.mirror_planes(tp) if mir else tp
        for k in range(1, 79):
            sc = dresden.cooccurrence_map(pooled[k], tq)
            if sc.size == 0:
                continue
            j = np.unravel_index(np.argmax(sc), sc.shape)
            results.append((1000 * int(sc[j]) // tcounts[tw], k, tw, mir,
                            int(j[1]) * 8, int(j[0]) * 8))

results.sort(reverse=True)
top = results[0]
others = [r for r in results if r[1] != top[1]]
margin_milli = 1000 * (top[0] - others[0][0]) // max(others[0][0], 1)

L.append("Top 10 placements (milli-score, scan, template width, mirrored, "
         "x, y):")
for r in results[:10]:
    L.append("  %5d  scan %2d (p%s)  tw=%d mir=%d at (%d, %d)" % (
        r[0], r[1], page_label(r[1]), r[2], r[3], r[4], r[5]))
L.append("Winner: scan %d (Förstemann p%s) at (%d, %d); margin over the "
         "best other-page placement: %d milli." % (
             top[1], page_label(top[1]), top[4], top[5], margin_milli))

check("photographed column locates on scan 73 (p69)", top[1] == 73)
check("location agrees with the visual verification (64, 772) +- 16",
      abs(top[4] - 64) <= 16 and abs(top[5] - 772) <= 16)
check("winner beats every other page", margin_milli > 0)

# --- verification panel ---------------------------------------------------
tw = top[2]
th = tw * tpl_img.size[1] // tpl_img.size[0]
pg = Image.open(page_path(top[1])).convert("RGB")
loc = pg.crop((top[4], top[5], min(684, top[4] + tw),
               min(1350, top[5] + th)))
scale_h = 900
qv = tpl_img.resize((tpl_img.size[0] * scale_h // tpl_img.size[1], scale_h))
lv = loc.resize((loc.width * scale_h // loc.height, scale_h))
panel = Image.new("RGB", (qv.width + lv.width + 30, scale_h + 40), (12, 12, 12))
panel.paste(qv, (10, 30))
panel.paste(lv, (qv.width + 20, 30))
d = ImageDraw.Draw(panel)
d.text((10, 8), "researcher's photograph (pinned query)", fill=(255, 210, 40))
d.text((qv.width + 20, 8),
       "LOCATED: scan %d / Förstemann p%s at (%d,%d)" % (
           top[1], page_label(top[1]), top[4], top[5]),
       fill=(0, 230, 120))
panel.save(os.path.join(DEMO, "dresden_located_p69.png"))

# marked page overview
pg2 = Image.open(page_path(top[1])).convert("RGB")
d2 = ImageDraw.Draw(pg2)
d2.rectangle([top[4], top[5], top[4] + tw, min(1349, top[5] + th)],
             outline=(0, 230, 120), width=4)
pg2.save(os.path.join(DEMO, "dresden_located_p69_page.png"))

ledger = Ledger()
ledger.record("locate_column",
              {"query": "queries/query_column_photo_q4.png",
               "method": "orientation co-occurrence, block 8, mag_t 18",
               "winner_scan": top[1], "winner_page": page_label(top[1]),
               "x": top[4], "y": top[5], "template_width": tw,
               "milli_score": top[0], "margin_milli": margin_milli},
              "search", Ledger.digest(load_luma(top[1])))
with open(os.path.join(DATA, "locate_receipts.json"), "w") as f:
    f.write(ledger.export())

print("\n".join(L))
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
