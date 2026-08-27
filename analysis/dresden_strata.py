"""NODE-DRE04 — KELD strata + tonal-window scan (discovery mode).

Per the archeoastronomy-codex evidence standard: pattern-level structure
extraction with named transforms and fixed parameters; pale fields are NOT
assumed blank — they get tonal windows.

  S1 KELD strata: `core.keld_map` with the STAR8 dual track — band index
     floor(L/36) read from a residue pair (A2-compliant: K-Elimination, no
     positional decode). An exact 8-band stratification of every page,
     rendered as a fixed palette.
  S2 Tonal windows: pale fields (16 px blocks whose median sits at/above
     the page's 800-milli order statistic) scanned with narrow exact luma
     windows — 6 consecutive windows spanning the pale range — rendered as
     binary maps. Latent structure in "blank" plaster shows up as coherent
     shapes inside a window; noise shows up as salt. The maps ship either
     way.

Usage: python3 analysis/dresden_strata.py
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import dresden
from cram_dsp.core import keld_map, STAR8
from cram_dsp.forensics import Ledger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "dresden")
TDIR = os.path.join(DATA, "derived", "strata")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(TDIR, exist_ok=True)

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


# --- fixtures -------------------------------------------------------------
ramp = np.arange(256, dtype=np.int64)
kb = keld_map(ramp, STAR8)
check("KELD strata on 8-bit ramp: band == L // 36 exactly",
      bool(np.all(kb == ramp // 36)))
check("KELD strata count on 8-bit range", int(kb.max()) == 255 // 36)

STRATA_COLORS = [(12, 12, 30), (40, 40, 110), (90, 50, 160), (170, 60, 150),
                 (230, 110, 70), (250, 180, 60), (250, 235, 160), (255, 255, 240)]

# --- sweep ----------------------------------------------------------------
ledger = Ledger()
rows = []
pale_rank = []
for k in range(1, 79):
    y = load_luma(k)
    strata = keld_map(y, STAR8)
    occ = [int((strata == b).sum()) for b in range(8)]
    img = np.zeros((y.shape[0], y.shape[1], 3), dtype=np.uint8)
    for b, c in enumerate(STRATA_COLORS):
        img[strata == b] = c
    Image.fromarray(img[::2, ::2]).save(
        os.path.join(TDIR, "scan%02d_keld.png" % k))

    # pale-field fraction (block medians at/above the 800-milli order stat)
    H, W = y.shape
    gh, gw = H // 16, W // 16
    blocks = y[:gh * 16, :gw * 16].reshape(gh, 16, gw, 16)
    med = np.sort(blocks.transpose(0, 2, 1, 3).reshape(gh, gw, 256),
                  axis=2)[:, :, 127]
    pale_thr = dresden.order_stat(y, 800)
    pale = med >= pale_thr
    pale_milli = (1000 * int(pale.sum())) // (gh * gw)
    pale_rank.append((pale_milli, k))
    rows.append((k, occ, pale_milli))
    ledger.record("keld_strata",
                  {"scan": k, "page": page_label(k), "track": "STAR8 M=36",
                   "occupancy": occ, "pale_milli": pale_milli},
                  Ledger.digest(y), Ledger.digest(strata))

check("strata computed for all pages", len(rows) == 78)

# --- tonal windows on the palest inscribed + blank pages -------------------
pale_rank.sort(reverse=True)
targets = [k for _, k in pale_rank[:6]]
for k in targets:
    y = load_luma(k)
    lo = dresden.order_stat(y, 780)
    hi = dresden.order_stat(y, 995)
    if hi <= lo:
        hi = lo + 6
    span = hi - lo
    panel = Image.new("RGB", (342 * 3, 675 * 2 + 20), (10, 10, 10))
    pd = ImageDraw.Draw(panel)
    for w in range(6):
        wlo = lo + (span * w) // 6
        whi = lo + (span * (w + 1)) // 6
        m = ((y >= wlo) & (y < whi)).astype(np.uint8) * 255
        wm = Image.fromarray(m).convert("RGB").resize((342, 675), Image.NEAREST)
        x0 = (w % 3) * 342
        y0 = 20 + (w // 3) * 675
        panel.paste(wm, (x0, y0))
        pd.text((x0 + 4, y0 + 2), "win %d..%d" % (wlo, whi),
                fill=(255, 210, 40))
    pd.text((4, 2), "scan %d (p%s) tonal windows over pale range %d..%d"
            % (k, page_label(k), lo, hi), fill=(0, 220, 255))
    panel.save(os.path.join(TDIR, "scan%02d_windows.png" % k))

out = [
    "# DRESDEN_STRATA — KELD strata + tonal windows (NODE-DRE04)",
    "",
    "Run: `python3 analysis/dresden_strata.py`; receipts",
    "`data/dresden/strata_receipts.json`; renders `data/dresden/derived/strata/`.",
    "",
    "**%s exact checks, %d failures.**" % ("{:,}".format(R["checks"]), R["fails"]),
    "",
    "S1 — KELD stratification (STAR8, M=36: band = floor(L/36) read from the",
    "residue pair; A2-compliant). Palette maps for every page",
    "(`scanNN_keld.png`). Occupancy per band (pixels), pale fraction (milli",
    "of 16 px blocks whose median sits at/above the page's 800-milli order",
    "statistic):",
    "",
    "| Scan | Page | B0..B7 occupancy | Pale milli |",
    "|---|---|---|---|",
]
for k, occ, pale_milli in rows:
    out.append("| %d | %s | %s | %d |" % (
        k, page_label(k), " ".join(str(o) for o in occ), pale_milli))
out += [
    "",
    "S2 — tonal windows over the palest six pages: " + ", ".join(
        "scan %d (p%s)" % (k, page_label(k)) for k in targets) + " —",
    "`scanNN_windows.png`, six exact windows spanning each page's own",
    "780..995-milli luma range. Reading note (per the working standard):",
    "pale fields are not assumed blank; coherent shapes inside a narrow",
    "window are latent-content candidates for higher-res or multispectral",
    "follow-up, and salt-noise windows are the null. The maps ship either",
    "way; nothing here is enhancement — every pixel is an exact membership",
    "test against stated integer bounds.",
]
with open(os.path.join(DOCS, "DRESDEN_STRATA.md"), "w") as f:
    f.write("\n".join(out) + "\n")
with open(os.path.join(DATA, "strata_receipts.json"), "w") as f:
    f.write(ledger.export())

print("\n".join(x for x in L if x.startswith("  FAIL")) or "no FAIL lines")
print("pale top:", pale_rank[:6])
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
