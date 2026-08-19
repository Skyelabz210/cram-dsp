"""CRAM-DF forensic probes + provenance layer.

Provenance = the Kiosk verification-receipt idea applied to evidence handling:
every operation on evidence appends a SHA-256 receipt to a hash chain. Because
the whole pipeline is integer-exact (A1) it is bit-identical across platforms
and runs, so the chain hash IS the reproducibility certificate — a chain of
custody for computation. Reversible ops additionally carry a round-trip
receipt (T-X-REV witnessed on the actual evidence bytes).
"""

import hashlib
import json
from math import gcd

import numpy as np


# ---------------------------------------------------------------------------
# Provenance ledger (hash-chained receipts)
# ---------------------------------------------------------------------------

class Ledger:
    GENESIS = b"CRAM-DF-GENESIS"

    def __init__(self):
        self.chain = hashlib.sha256(self.GENESIS).hexdigest()
        self.entries = []

    @staticmethod
    def digest(arr) -> str:
        a = np.ascontiguousarray(np.asarray(arr).astype(np.int64))
        h = hashlib.sha256()
        h.update(str(a.shape).encode())
        h.update(a.tobytes())
        return h.hexdigest()

    def record(self, op: str, params, in_digest: str, out_digest: str):
        entry = {"op": op, "params": params, "in": in_digest, "out": out_digest}
        h = hashlib.sha256()
        h.update(self.chain.encode())
        h.update(json.dumps(entry, sort_keys=True).encode())
        self.chain = h.hexdigest()
        entry["chain"] = self.chain
        self.entries.append(entry)
        return entry

    def roundtrip_receipt(self, name: str, original, recovered):
        d0, d1 = self.digest(original), self.digest(recovered)
        ok = d0 == d1
        self.record("roundtrip:" + name, {"exact": ok}, d0, d1)
        return ok

    def export(self) -> str:
        return json.dumps(
            {"chain": self.chain, "entries": self.entries}, indent=1, sort_keys=True
        )


# ---------------------------------------------------------------------------
# Exact copy-move clone detection
# ---------------------------------------------------------------------------

def copy_move_exact(img, block: int = 12, stride: int = 1, min_offset: int = 16):
    """Detect exact cloned regions by content-addressed block hashing.

    Exactness matters: a float pipeline perturbs clones apart; an A1 pipeline
    keeps clone pairs bit-identical, so detection is a dictionary lookup.
    Returns a boolean involvement mask and the list of (src, dst) block pairs.
    """
    a = np.asarray(img).astype(np.int64)
    H, W = a.shape
    seen = {}
    pairs = []
    mask = np.zeros((H, W), dtype=bool)
    for i in range(0, H - block + 1, stride):
        for j in range(0, W - block + 1, stride):
            key = hashlib.sha256(
                np.ascontiguousarray(a[i:i + block, j:j + block]).tobytes()
            ).digest()
            if key in seen:
                pi, pj = seen[key]
                if abs(pi - i) + abs(pj - j) >= min_offset:
                    pairs.append(((pi, pj), (i, j)))
                    mask[pi:pi + block, pj:pj + block] = True
                    mask[i:i + block, j:j + block] = True
            else:
                seen[key] = (i, j)
    return mask, pairs


# ---------------------------------------------------------------------------
# Quantization-fingerprint splice localization (exact gcd statistic)
# ---------------------------------------------------------------------------

def _block_gcd_of_steps(a):
    """gcd of all nonzero local steps inside a block (0 if the block is flat)."""
    g = 0
    dh = np.diff(a, axis=1).ravel()
    dv = np.diff(a, axis=0).ravel()
    for d in (dh, dv):
        for v in d:
            if v:
                g = gcd(g, int(abs(v)))
                if g == 1:
                    return 1
    return g


def quant_fingerprint_map(img, block: int = 16):
    """Per-block gcd of local steps — the requantization fingerprint.

    A region whose values were quantized to multiples of step s has all local
    steps divisible by s; its fingerprint is a multiple of s. A pasted region
    with a different processing history carries a different fingerprint; seam
    blocks mixing two histories collapse to gcd 1.
    """
    a = np.asarray(img).astype(np.int64)
    H, W = a.shape
    gh, gw = H // block, W // block
    fp = np.zeros((gh, gw), dtype=np.int64)
    for bi in range(gh):
        for bj in range(gw):
            fp[bi, bj] = _block_gcd_of_steps(
                a[bi * block:(bi + 1) * block, bj * block:(bj + 1) * block]
            )
    return fp


def estimate_background_step(fp) -> int:
    """Largest step s >= 2 dividing the fingerprint of at least half the
    non-flat blocks. Robust to blocks whose gcd is a multiple of the true
    step (e.g. 8 or 12 where the history step is 4)."""
    nz = fp[fp != 0]
    if nz.size == 0:
        return 1
    best = 1
    for s in range(2, int(nz.max()) + 1):
        if int((nz % s == 0).sum()) * 2 >= int(nz.size):
            best = s
    return best


def splice_flag_map(fp):
    """Unsupervised: estimate the background requantization step, then flag
    every non-flat block whose fingerprint is incompatible with it (seam
    blocks collapse to gcd 1 and are flagged too). Flat blocks (fp = 0) carry
    no step evidence and are never flagged."""
    step = estimate_background_step(fp)
    return (fp != 0) & (fp % step != 0), step


def sigma_diff_histograms(img, block: int = 16, lane: int = 11):
    """Secondary probe: per-block histogram of nonzero local steps mod `lane`
    (residue-native — computed from lane residues, never from magnitudes)."""
    r = np.asarray(img).astype(np.int64) % lane
    H, W = r.shape
    gh, gw = H // block, W // block
    hist = np.zeros((gh, gw, lane), dtype=np.int64)
    dh = np.diff(r, axis=1) % lane
    dv = np.diff(r, axis=0) % lane
    for bi in range(gh):
        for bj in range(gw):
            for d in (
                dh[bi * block:(bi + 1) * block, bj * block:(bj + 1) * block - 1],
                dv[bi * block:(bi + 1) * block - 1, bj * block:(bj + 1) * block],
            ):
                cls, cnt = np.unique(d[d != 0], return_counts=True)
                for c, n in zip(cls, cnt):
                    hist[bi, bj, int(c)] += int(n)
    return hist


def iou(mask_a, mask_b) -> "tuple[int, int]":
    """Exact integer IoU as a (intersection, union) pair — no float ratio."""
    inter = int((mask_a & mask_b).sum())
    union = int((mask_a | mask_b).sum())
    return inter, union
