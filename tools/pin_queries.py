"""NODE-DRE (queries) — pin the researcher-supplied illustration/query images.

The researcher supplied three images with the scan set:
  * two concept illustrations (the claims under test), and
  * one photographed codex column (the localization query).

Full-resolution originals are session uploads, not public objects; per the
data discipline the repo carries exact nearest-neighbour decimations
(every k-th pixel, offset 0 — an exact integer subsample per the
NODE-INF07 geometry-cast rule) with the original bytes pinned by SHA-256
in the receipts. No resampling, no interpolation, no value synthesis.
"""

import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cram_dsp.forensics import Ledger


def pin(src_path: str, out_path: str, k: int, ledger: Ledger, label: str):
    raw = open(src_path, "rb").read()
    src_sha = hashlib.sha256(raw).hexdigest()
    rgb = np.asarray(Image.open(src_path).convert("RGB"))
    dec = rgb[::k, ::k, :]
    Image.fromarray(dec).save(out_path, optimize=True)
    out_sha = hashlib.sha256(open(out_path, "rb").read()).hexdigest()
    ledger.record_acquisition(
        url="researcher-upload:%s" % label,
        byte_range="0-%d" % (len(raw) - 1),
        sha256=src_sha, nbytes=len(raw), out_digest=src_sha)
    ledger.record(
        "decimate_nn",
        {"label": label, "k": k, "offset": 0,
         "src_shape": [int(x) for x in rgb.shape],
         "out_shape": [int(x) for x in dec.shape],
         "out_file": os.path.basename(out_path), "out_sha256": out_sha},
        src_sha, Ledger.digest(dec))
    print(label, "->", os.path.basename(out_path), dec.shape, out_sha[:12])


def main(uploads_dir: str):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "data", "dresden", "queries")
    os.makedirs(base, exist_ok=True)
    ledger = Ledger()
    pin(os.path.join(uploads_dir, "563c5bc6-image.png"),
        os.path.join(base, "query_column_photo_q4.png"), 4, ledger,
        "photographed codex column (localization query)")
    pin(os.path.join(uploads_dir, "b47c3ace-image.png"),
        os.path.join(base, "claim_illustration_1_q2.png"), 2, ledger,
        "concept illustration 1 (luminous path / glyph code claims)")
    pin(os.path.join(uploads_dir, "72162b5b-image.png"),
        os.path.join(base, "claim_illustration_2_q2.png"), 2, ledger,
        "concept illustration 2 (white-gradient sequence claims)")
    with open(os.path.join(base, "receipts.json"), "w") as f:
        f.write(ledger.export())
    print("chain:", ledger.chain)


if __name__ == "__main__":
    main(sys.argv[1])
