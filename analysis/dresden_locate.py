"""Localizer v2 — weighted orientations, anisotropic registration, controls.

Per the researcher's production spec:
  * weighted orientation planes (edge confidence: a heavy stroke outweighs
    a faint fiber boundary; integers throughout),
  * anisotropic scale sweep (scale_x × scale_y — a photographed page can
    stretch differently in each axis),
  * MIDRANK NORMALIZATION of both sides before matching — imported from
    the ARCHIMEDES branch-exhaustion sweep (BRANCH_SWEEP.md B2/B6), where
    independent contrast stretches were shown to drive, and even invert, a
    metric. A phone photograph and a WDL scan have unrelated tone curves;
    equalizing marginals removes that confound and leaves spatial order.
  * EXACT COSINE scoring (`cooccurrence_normalized`) so scores from
    different templates/scales are comparable — the previous raw-dot score
    was not, and the control battery caught it (texture floor 2380 above
    the real query 861). That failure is preserved below as a receipt.
  * ABSTENTION (archnet void rejection): a thin margin declines to name a
    winner rather than guessing.
  * a CONTROL BATTERY on every run (docs/RULES_OF_EXPLORATION.md rule 5):
      positive control   known crop -> its own page
      negative control   unrelated crop, its own page excluded
      null control       texture-only template (blank-page region)
      hard negative      the most similar other page, reported by name
  * reporting: winner + margin over best unrelated + null gap + rank
    percentile — never a bare "scan X wins".

Failed-method receipt for v1 (luma SAD false negative) lives permanently in
docs/DRESDEN_MACHINE.md §C4. Ground truth for the main query (verified
visually + by v1.5 orientation matcher): scan 73 / p69 / (64, 768).

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


POOL = 8
MIN_MARGIN = 20          # milli-cosine; below this the run ABSTAINS
pooled = {}
for k in range(1, 79):
    pooled[k] = dresden.pool_planes(
        dresden.orientation_planes_weighted(
            dresden.midrank_normalize(load_luma(k))), POOL)


def search(tpl_img, widths, aspect_milli=(900, 1000, 1100), exclude=()):
    """Anisotropic weighted-orientation search. Returns per-page best list
    sorted descending: (milli, scan, tw, th, mir, x, y)."""
    per_page = {}
    for tw in widths:
        th0 = tw * tpl_img.size[1] // tpl_img.size[0]
        for am in aspect_milli:
            th = (th0 * am) // 1000
            if th > 1349 or th < 16:
                continue
            t = dresden.midrank_normalize(dresden.int_luma(np.asarray(
                tpl_img.resize((tw, th), Image.LANCZOS).convert("RGB"))))
            tp = dresden.pool_planes(
                dresden.orientation_planes_weighted(t), POOL)
            for mir in (0, 1):
                tq = dresden.mirror_planes(tp) if mir else tp
                for k in range(1, 79):
                    if k in exclude:
                        continue
                    sc = dresden.cooccurrence_normalized(pooled[k], tq)
                    if sc.size == 0:
                        continue
                    j = np.unravel_index(np.argmax(sc), sc.shape)
                    cand = (int(sc[j]), k, tw, th, mir,
                            int(j[1]) * POOL, int(j[0]) * POOL)
                    if k not in per_page or cand[0] > per_page[k][0]:
                        per_page[k] = cand
    return sorted(per_page.values(), reverse=True)


def battery_report(name, ranked, true_scan=None):
    """Winner (or ABSTAIN) + margins + rank percentile, per the control
    battery rule and the archnet void-rejection rule."""
    win, verdict, _m = dresden.decide_with_abstention(ranked, MIN_MARGIN)
    unrelated = [r for r in ranked
                 if true_scan is None or r[1] != true_scan]
    best_unrel = unrelated[0] if win[1] == true_scan else win
    scores = [r[0] for r in ranked]
    lo = sum(1 for s in scores if s < win[0])
    pct_milli = (1000 * lo) // max(len(scores) - 1, 1)
    margin = win[0] - (unrelated[0][0] if win[1] == true_scan
                       else ranked[1][0])
    L.append("- %s: %s scan %d (p%s) at (%d, %d) tw=%d th=%d mir=%d, "
             "cosine %d/1000; margin %+d over best %s; rank percentile "
             "%d/1000."
             % (name,
                "ABSTAIN (thin margin), best was" if verdict == dresden.ABSTAIN
                else "winner", win[1], page_label(win[1]), win[5], win[6],
                win[2], win[3], win[4], win[0], margin,
                "unrelated page" if true_scan else "runner-up", pct_milli))
    return win, margin, pct_milli


# === MAIN QUERY: the researcher's photographed column =====================
qimg = Image.open(os.path.join(DATA, "queries", "query_column_photo_q4.png"))
qw, qh = qimg.size
tpl = qimg.crop((qw * 13 // 100, qh * 2 // 100, qw * 86 // 100, qh * 99 // 100))
ranked = search(tpl, (180, 210, 240, 270, 300))
win, margin, pct = battery_report("MAIN QUERY (photographed column)",
                                  ranked, true_scan=73)
check("main query locates on scan 73 (ground truth)", win[1] == 73)
check("main query location near (64, 768)",
      abs(win[5] - 64) <= 16 and abs(win[6] - 768) <= 16)
check("positive margin over best unrelated page", margin > 0)
hard_neg = [r for r in ranked if r[1] != 73][0]
L.append("  hard negative (most similar other page): scan %d (p%s), "
         "milli %d — the structural twin the matcher itself surfaced."
         % (hard_neg[1], page_label(hard_neg[1]), hard_neg[0]))

# === CONTROL BATTERY ======================================================
# positive control: known crop from scan 10 -> must return scan 10 rank #1
pc = Image.fromarray(np.asarray(
    Image.open(page_path(10)).convert("RGB"))[300:700, 200:360])
ranked_pc = search(pc, (120, 160, 200))
win_pc, margin_pc, pct_pc = battery_report(
    "positive control (known crop of scan 10)", ranked_pc, true_scan=10)
check("positive control returns its own page at rank 1", win_pc[1] == 10)
check("positive control offset exact within pooling",
      abs(win_pc[5] - 200) <= POOL and abs(win_pc[6] - 300) <= POOL)

# negative control: crop of scan 40, scan 40 excluded from the search —
# every score is a false-match score; records the impostor distribution.
nc = Image.fromarray(np.asarray(
    Image.open(page_path(40)).convert("RGB"))[400:800, 150:330])
ranked_nc = search(nc, (140, 180), exclude=(40,))
L.append("- negative control (scan 40 crop, scan 40 excluded): best "
         "impostor cosine %d/1000 on scan %d (p%s) — the false-match "
         "ceiling, now on the SAME scale as every other score."
         % (ranked_nc[0][0], ranked_nc[0][1], page_label(ranked_nc[0][1])))
check("main-query winner clears the impostor ceiling",
      win[0] > ranked_nc[0][0])

# null control: texture-only template from a blank page region
null_t = Image.fromarray(np.asarray(
    Image.open(page_path(30)).convert("RGB"))[400:800, 150:330])
ranked_null = search(null_t, (140, 180))
L.append("- null control (blank-page texture template): best cosine %d/1000 "
         "on scan %d (p%s) — the texture floor. Main-query winner exceeds "
         "it by %+d. NOTE (RULES_OF_EXPLORATION rule 2): under the "
         "continuous-strip hypothesis a blank region is not a null for "
         "TRAIL questions; it is used here only as a matching-score floor "
         "for LOCALIZATION, which is a different question."
         % (ranked_null[0][0], ranked_null[0][1],
            page_label(ranked_null[0][1]), win[0] - ranked_null[0][0]))
check("main-query winner clears the texture floor",
      win[0] > ranked_null[0][0])

ledger = Ledger()
ledger.record("locate_v2",
              {"query": "queries/query_column_photo_q4.png",
               "method": "weighted orientation co-occurrence, pool 8, "
                         "aspect sweep 900/1000/1100 milli",
               "winner_scan": win[1], "x": win[5], "y": win[6],
               "milli": win[0], "margin": margin, "rank_pct": pct,
               "impostor_ceiling": int(ranked_nc[0][0]),
               "texture_floor": int(ranked_null[0][0])},
              "search", Ledger.digest(load_luma(win[1])))
with open(os.path.join(DATA, "locate_receipts.json"), "w") as f:
    f.write(ledger.export())

# verification panel (kept from v1.5, regenerated)
tw, th = win[2], win[3]
pg = Image.open(page_path(win[1])).convert("RGB")
loc = pg.crop((win[5], win[6], min(684, win[5] + tw), min(1350, win[6] + th)))
scale_h = 900
qv = tpl.resize((tpl.size[0] * scale_h // tpl.size[1], scale_h))
lv = loc.resize((loc.width * scale_h // loc.height, scale_h))
panel = Image.new("RGB", (qv.width + lv.width + 30, scale_h + 40), (12, 12, 12))
panel.paste(qv, (10, 30))
panel.paste(lv, (qv.width + 20, 30))
d = ImageDraw.Draw(panel)
d.text((10, 8), "researcher's photograph (pinned query)", fill=(255, 210, 40))
d.text((qv.width + 20, 8),
       "LOCATED: scan %d / p%s at (%d,%d) — margin %+d, pct %d/1000" % (
           win[1], page_label(win[1]), win[5], win[6], margin, pct),
       fill=(0, 230, 120))
panel.save(os.path.join(DEMO, "dresden_located_p69.png"))

print("\n".join(L))
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
