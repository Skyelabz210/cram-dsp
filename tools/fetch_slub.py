"""Fetch the Codex Dresdensis at ORIGINAL resolution from SLUB Dresden.

Why this exists. The researcher's PDF embeds 78 images at 684x1350 — that is
its native resolution, not a downsample applied here. Zooming into it is
blurred because the source is blurred, and every matching number produced so
far carried "the 684x1350 resolution bound" as a named limit. The library
that holds the object publishes it at 3874x7649: 5.7x linear, 32x the
pixels. At 684 the interior structure of a glyph icon is simply not
resolved, which is the most likely reason icon-to-character registration had
nothing to separate.

Object: Codex Dresdensis, Mscr.Dresd.R.310, Saechsische Landesbibliothek —
Staats- und Universitaetsbibliothek Dresden (SLUB). Rights: Public Domain
Mark 1.0, as declared in the object's own METS record.

Receipts, per CLAUDE.md rule 6: every file records its source URL, byte
length and SHA-256 into data/dresden/hires/RECEIPTS.json, and the digests
are pinned in data/dresden/hires/SHA256SUMS.txt. The images themselves stay
out of git (.gitignore) and are regenerable by re-running this tool.

Page correspondence is VERIFIED, not assumed: each fetched page is
downscaled to the PDF page's size and correlated against it; a page that
does not correlate above 0.95 is reported and not silently accepted.

Usage: python3 tools/fetch_slub.py [first] [last]
"""

import hashlib
import json
import os
import sys
import urllib.request

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cram_dsp import dresden

Image.MAX_IMAGE_PIXELS = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "dresden")
HI = os.path.join(DATA, "hires")
os.makedirs(HI, exist_ok=True)

BASE = ("https://digital.slub-dresden.de/data/kitodo/"
        "codedrm_280742827/codedrm_280742827_tif/jpegs/"
        "%08d.tif.original.jpg")
OBJECT = "Codex Dresdensis, Mscr.Dresd.R.310, SLUB Dresden"
RIGHTS = "Public Domain Mark 1.0 (declared in the object's METS record)"


def corr_milli(a, b):
    """Exact-enough integer correlation for the page-identity check."""
    a = a.astype(np.int64)
    b = b.astype(np.int64)
    a = a - int(np.sort(a, axis=None)[a.size // 2])
    b = b - int(np.sort(b, axis=None)[b.size // 2])
    num = float((a * b).sum())
    den = float(np.sqrt(float((a * a).sum()) * float((b * b).sum())))
    return int(1000 * num / den) if den else 0


def main():
    first = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    last = int(sys.argv[2]) if len(sys.argv) > 2 else 78
    recs = []
    rpath = os.path.join(HI, "RECEIPTS.json")
    if os.path.exists(rpath):
        with open(rpath) as f:
            recs = json.load(f)
    have = {r["page"] for r in recs}
    for k in range(first, last + 1):
        out = os.path.join(HI, "slub_p%02d.jpg" % k)
        if k in have and os.path.exists(out):
            print("p%02d already have" % k, flush=True)
            continue
        url = BASE % k
        with urllib.request.urlopen(url, timeout=300) as r:
            blob = r.read()
        with open(out, "wb") as f:
            f.write(blob)
        im = Image.open(out)
        ref = Image.open(os.path.join(
            DATA, "pages", "wdl11621_scan%02d.jpg" % k)).convert("RGB")
        c = corr_milli(
            dresden.int_luma(np.asarray(im.convert("RGB").resize(
                ref.size, Image.LANCZOS))),
            dresden.int_luma(np.asarray(ref)))
        rec = {"page": k, "url": url, "bytes": len(blob),
               "sha256": hashlib.sha256(blob).hexdigest(),
               "width": im.size[0], "height": im.size[1],
               "corr_vs_pdf_page_milli": c,
               "identity_ok": bool(c >= 950),
               "object": OBJECT, "rights": RIGHTS}
        recs = [r for r in recs if r["page"] != k] + [rec]
        recs.sort(key=lambda r: r["page"])
        with open(rpath, "w") as f:
            json.dump(recs, f, indent=1)
        print("p%02d %dx%d %d bytes corr %d/1000 %s"
              % (k, im.size[0], im.size[1], len(blob), c,
                 "OK" if rec["identity_ok"] else "*** IDENTITY CHECK FAILED"),
              flush=True)
    with open(os.path.join(HI, "SHA256SUMS.txt"), "w") as f:
        for r in recs:
            f.write("%s  slub_p%02d.jpg\n" % (r["sha256"], r["page"]))
    bad = [r["page"] for r in recs if not r["identity_ok"]]
    print("pages: %d  identity failures: %s" % (len(recs), bad or "none"))


if __name__ == "__main__":
    main()
