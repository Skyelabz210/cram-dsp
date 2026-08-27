"""NODE-DRE01 — Dresden Codex scan ingestion (receipted, byte-exact).

Source object: World Digital Library item 11621 ("Codex Dresdensis",
SLUB Mscr.Dresd.R.310), provided by the researcher as a single PDF whose
78 pages each embed one baseline-JPEG scan (DCTDecode stream).

This tool:
  1. pins the source PDF by SHA-256 (acquisition receipt),
  2. extracts each page's embedded JPEG *byte-exact* — the raw DCTDecode
     stream is written to disk untouched; no decode/re-encode, no
     resampling: the bytes on disk are the bytes inside the PDF,
  3. decodes each JPEG once (libjpeg via Pillow, version recorded) to an
     RGB uint8 array and characterizes it with exact integer statistics
     (dimensions, integer-luma extrema/median, integer-Otsu ink threshold,
     dark-pixel coverage in milli-units),
  4. emits data/dresden/receipts.json (hash-chained forensics.Ledger),
     data/dresden/characterization.json and data/dresden/SHA256SUMS.txt.

A1 note: every statistic here is computed with integer ops only
(//, %, >>, integer numpy dtypes). The JPEG decode itself happens inside
libjpeg; its output integers are digested and recorded, so any future
decoder change is detectable against the receipts.
"""

import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image
import PIL

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cram_dsp.forensics import Ledger
from cram_dsp.dresden import int_luma, exact_median, otsu_threshold as otsu_int

WDL_URL = "http://hdl.loc.gov/loc.wdl/wdl.11621"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def characterize(rgb):
    y = int_luma(rgb)
    h, w = y.shape
    thr = otsu_int(y)
    dark = int((y < thr).sum())
    total = h * w
    return {
        "width": int(w),
        "height": int(h),
        "luma_min": int(y.min()),
        "luma_max": int(y.max()),
        "luma_median": exact_median(y),
        "otsu_threshold": int(thr),
        "dark_px": dark,
        "total_px": total,
        "ink_coverage_milli": (1000 * dark) // total,
    }


def main(pdf_path: str, out_dir: str):
    import pymupdf

    pages_dir = os.path.join(out_dir, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    pdf_sha = sha256_bytes(pdf_bytes)

    ledger = Ledger()
    ledger.record_acquisition(
        url=WDL_URL,
        byte_range="0-%d" % (len(pdf_bytes) - 1),
        sha256=pdf_sha,
        nbytes=len(pdf_bytes),
        out_digest=pdf_sha,
    )

    doc = pymupdf.open(pdf_path)
    sums, chars = [], {}
    for i in range(doc.page_count):
        page = doc[i]
        imgs = page.get_images(full=True)
        if len(imgs) != 1:
            raise SystemExit(
                "page %d carries %d images; expected exactly 1" % (i + 1, len(imgs))
            )
        xref = imgs[0][0]
        info = doc.extract_image(xref)
        if info["ext"] != "jpeg":
            raise SystemExit("page %d stream is %s, not jpeg" % (i + 1, info["ext"]))
        raw = info["image"]
        name = "wdl11621_scan%02d.jpg" % (i + 1)
        with open(os.path.join(pages_dir, name), "wb") as f:
            f.write(raw)
        jsha = sha256_bytes(raw)
        sums.append((jsha, "pages/" + name))

        rgb = np.asarray(Image.open(os.path.join(pages_dir, name)).convert("RGB"))
        c = characterize(rgb)
        c["jpeg_sha256"] = jsha
        c["jpeg_bytes"] = len(raw)
        c["decoded_digest"] = Ledger.digest(rgb)
        chars["scan%02d" % (i + 1)] = c

        ledger.record(
            "extract_jpeg",
            {"pdf_page": i + 1, "xref": xref, "file": "pages/" + name,
             "bytes": len(raw), "mode": "byte-exact DCTDecode stream copy"},
            pdf_sha, jsha,
        )
        ledger.record(
            "decode_jpeg",
            {"file": "pages/" + name,
             "decoder": "Pillow %s" % PIL.__version__,
             "luma": "(77R+150G+29B)>>8"},
            jsha, c["decoded_digest"],
        )

    with open(os.path.join(out_dir, "SHA256SUMS.txt"), "w") as f:
        f.write("%s  %s\n" % (pdf_sha, os.path.basename(pdf_path)))
        for jsha, rel in sums:
            f.write("%s  %s\n" % (jsha, rel))
    with open(os.path.join(out_dir, "receipts.json"), "w") as f:
        f.write(ledger.export())
    with open(os.path.join(out_dir, "characterization.json"), "w") as f:
        json.dump(chars, f, indent=1, sort_keys=True)

    print("pdf sha256:", pdf_sha)
    print("pages extracted:", len(sums))
    print("chain:", ledger.chain)


if __name__ == "__main__":
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "data", "dresden")
    pdf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        base, "source", "wdl11621_codex_dresdensis.pdf")
    main(pdf, base)
