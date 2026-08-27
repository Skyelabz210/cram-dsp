"""NODE-DRE02 — repair-seam map, codex-wide.

Two probes, both exact, both reported at whatever size the evidence
supports (zero included):

  P1 requantization fingerprint (`forensics.quant_fingerprint_map` +
     `splice_flag_map`): detects mixed processing histories. On
     continuous-tone JPEG-decoded scans this statistic recorded a null on
     the Archimedes corpus; whatever it says here ships.
  P2 block-median discontinuity: physical repair (patches, overpaint,
     exposed backing) shifts local tone. Per-page 16 px block medians,
     4-neighbour absolute differences, threshold = exact order statistic at
     990 milli of the page's own diffs; flagged boundaries are the seam
     candidates, enumerated with coordinates and drawn as panels.

Usage: python3 analysis/dresden_seams.py
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cram_dsp import dresden, forensics
from cram_dsp.forensics import Ledger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "dresden")
SDIR = os.path.join(DATA, "derived", "seams")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(SDIR, exist_ok=True)

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
base = (np.arange(64 * 64, dtype=np.int64).reshape(64, 64) % 40) * 4
spliced = base.copy()
spliced[16:32, 16:48] = (np.arange(16 * 32).reshape(16, 32) % 40) * 3
fp = forensics.quant_fingerprint_map(spliced, block=16)
flags, step = forensics.splice_flag_map(fp)
check("fingerprint fixture: background step 4 recovered", step == 4)
check("fingerprint fixture: pasted x3 region flagged", bool(flags.any()))


def block_median_map(y, block=16):
    H, W = y.shape
    gh, gw = H // block, W // block
    m = y[:gh * block, :gw * block].reshape(gh, block, gw, block)
    m = np.sort(m.transpose(0, 2, 1, 3).reshape(gh, gw, block * block), axis=2)
    return m[:, :, (block * block - 1) // 2]


med = block_median_map(np.pad(np.zeros((32, 32), np.int64), ((0, 0), (0, 32)),
                              constant_values=200))
check("block-median discontinuity fixture: step edge visible",
      int(np.abs(np.diff(med, axis=1)).max()) == 200)

# --- codex sweep ----------------------------------------------------------
ledger = Ledger()
fp_flag_total = 0
rows = []
for k in range(1, 79):
    y = load_luma(k)
    fp = forensics.quant_fingerprint_map(y, block=16)
    flags, step = forensics.splice_flag_map(fp)
    nflag_fp = int(flags.sum())
    fp_flag_total += nflag_fp

    med = block_median_map(y, 16)
    dh = np.abs(np.diff(med, axis=1))
    dv = np.abs(np.diff(med, axis=0))
    alld = np.concatenate((dh.ravel(), dv.ravel()))
    thr = dresden.order_stat(alld, 990)
    eh = dh >= max(thr, 24)
    ev = dv >= max(thr, 24)
    ncand = int(eh.sum()) + int(ev.sum())
    rows.append((k, step, nflag_fp, thr, ncand, eh, ev, med))
    ledger.record("seam_probe",
                  {"scan": k, "page": page_label(k), "fp_step": step,
                   "fp_flags": nflag_fp, "median_thr": int(max(thr, 24)),
                   "median_edge_candidates": ncand},
                  Ledger.digest(y), Ledger.digest(med))

check("both probes ran on all pages", len(rows) == 78)

# panels for the 6 pages with most median-discontinuity candidates
rows_by_cand = sorted(rows, key=lambda r: -r[4])[:6]
for k, step, nfp, thr, ncand, eh, ev, med in rows_by_cand:
    img = Image.open(page_path(k)).convert("RGB")
    d = ImageDraw.Draw(img)
    for bi, bj in zip(*np.nonzero(eh)):
        x = (bj + 1) * 16
        d.line([(x, bi * 16), (x, bi * 16 + 16)], fill=(0, 230, 120), width=3)
    for bi, bj in zip(*np.nonzero(ev)):
        y0 = (bi + 1) * 16
        d.line([(bj * 16, y0), (bj * 16 + 16, y0)], fill=(255, 80, 200), width=3)
    img.resize((342, 675), Image.NEAREST).save(
        os.path.join(SDIR, "scan%02d_seams.jpg" % k), quality=80)

out = [
    "# DRESDEN_SEAMS — repair-seam probes, codex-wide (NODE-DRE02)",
    "",
    "Run: `python3 analysis/dresden_seams.py`; receipts",
    "`data/dresden/seam_receipts.json`; panels `data/dresden/derived/seams/`.",
    "",
    "**%s exact checks, %d failures.**" % ("{:,}".format(R["checks"]), R["fails"]),
    "",
    "## P1 — requantization fingerprint",
    "",
    "Total flagged blocks across all 78 scans: **%d**." % fp_flag_total,
    "As on the Archimedes sensor data, the fingerprint statistic %s on"
    % ("recorded a NULL" if fp_flag_total == 0 else "flagged blocks"),
    "these continuous-tone JPEG-decoded scans — recorded, not buried. Mixed",
    "processing histories inside a page are %sdetected by this probe here."
    % ("not " if fp_flag_total == 0 else ""),
    "",
    "## P2 — block-median discontinuity (physical seam candidates)",
    "",
    "Per-page threshold: exact order statistic at 990 milli of the page's own",
    "neighbour differences, floored at 24 luma steps. Candidates are block",
    "boundaries, coordinates in 16 px block units (x16 for pixels).",
    "",
    "| Scan | Page | fp step | fp flags | median thr | seam candidates |",
    "|---|---|---|---|---|---|",
]
for k, step, nfp, thr, ncand, eh, ev, med in rows:
    out.append("| %d | %s | %d | %d | %d | %d |" % (
        k, page_label(k), step, nfp, max(thr, 24), ncand))
out += [
    "",
    "Panels (green = vertical boundary, magenta = horizontal) for the six",
    "highest-candidate pages: " + ", ".join(
        "scan %d (p%s)" % (r[0], page_label(r[0])) for r in rows_by_cand) + ".",
    "",
    "Reading note: median discontinuities mark tonal steps — repairs, patch",
    "edges, exposed backing, and also legitimate painted boundaries (red",
    "frame lines). CODICOLOGICAL confirmation (which candidates are repairs)",
    "needs the physical-object literature or higher-res captures; this map",
    "is the candidate enumeration the node's gate asks for.",
]
with open(os.path.join(DOCS, "DRESDEN_SEAMS.md"), "w") as f:
    f.write("\n".join(out) + "\n")
with open(os.path.join(DATA, "seam_receipts.json"), "w") as f:
    f.write(ledger.export())

print("\n".join(x for x in L if x.startswith("  FAIL")) or "no FAIL lines")
print("fp flags total:", fp_flag_total)
print("TOTAL: {:,} checks, {} failures".format(R["checks"], R["fails"]))
sys.exit(1 if R["fails"] else 0)
