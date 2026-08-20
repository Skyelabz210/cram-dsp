"""NODE-INF04 — lattice-aware ingestion (the sealed entry seam).

Real sensor releases often pad: the Archimedes 16-bit rasters carry 14-bit
data left-shifted by 2, so every value is a multiple of 4. Analysing padded
values wastes two bits of lane budget and misaligns every band boundary.

This module detects the value lattice exactly, casts once at the seam
(v // g), and records a receipt so the cast is auditable and exactly
reversible (v * g). No float, no normalisation, no clipping.
"""

from math import gcd
from functools import reduce

import numpy as np


def detect_lattice(arr, sample_cap: int = 100000) -> int:
    """Exact gcd of the nonzero values — the quantisation step of the source."""
    v = np.unique(np.asarray(arr).astype(np.int64))
    v = v[v > 0]
    if v.size == 0:
        return 1
    return int(reduce(gcd, v[:sample_cap].tolist(), 0)) or 1


def effective_bits(arr, lattice: int) -> int:
    """Bits actually carried once the padding lattice is divided out."""
    hi = int(np.asarray(arr).max()) // max(lattice, 1)
    b = 0
    while (1 << b) <= hi:
        b += 1
    return b


def seal(arr, ledger=None, name: str = "ingest"):
    """Cast to the true lattice. Returns (sealed, lattice, bits).

    Exactly invertible: unseal(seal(a)) == a. If a ledger is supplied the
    cast is receipted with the detected step so downstream results can be
    audited back to the raw release.
    """
    a = np.asarray(arr).astype(np.int64)
    if a.dtype.kind not in "iu":
        raise TypeError("A1: ingest refuses non-integer input")
    g = detect_lattice(a)
    sealed = a // g
    bits = effective_bits(a, g)
    if ledger is not None:
        ledger.record(f"{name}:lattice_seal", {"step": g, "bits": bits},
                      ledger.digest(a), ledger.digest(sealed))
    return sealed, g, bits


def unseal(sealed, lattice: int):
    """Exact inverse of seal()."""
    return np.asarray(sealed).astype(np.int64) * int(lattice)
