"""Rational-Grid Exact Unmixing (recto-verso bleed-through).

Classical blind source separation (PCA/ICA) estimates the mixing matrix
statistically in float space and always leaves residual. Here the mixing is
modelled as an exact rational operator and inverted fraction-free:

    Yr = q*Sr + p*flip(Sv)
    Yv = q*Sv + p*flip(Sr)          (flip = horizontal mirror, verso seen
                                     through the leaf; alpha = p/q, p < q)

Fraction-free elimination gives, with D = q^2 - p^2:

    D*Sr = q*Yr - p*flip(Yv)
    D*Sv = q*Yv - p*flip(Yr)

Every division is exact by construction — an A1 pipeline, zero residual.

Blind estimation: the true (p, q) is found on the coprime rational grid by an
integer objective — exact-divisibility violations first (at the true operator
D divides everywhere; elsewhere it generically does not), then negativity,
then the integer cross-energy sum|Sr * flip(Sv)| (source overlap only).
"""

from math import gcd

import numpy as np


def mix(Sr, Sv, p: int, q: int):
    Sr = np.asarray(Sr).astype(np.int64)
    Sv = np.asarray(Sv).astype(np.int64)
    Yr = q * Sr + p * np.fliplr(Sv)
    Yv = q * Sv + p * np.fliplr(Sr)
    return Yr, Yv


def unmix_exact(Yr, Yv, p: int, q: int):
    Yr = np.asarray(Yr).astype(np.int64)
    Yv = np.asarray(Yv).astype(np.int64)
    D = q * q - p * p
    Nr = q * Yr - p * np.fliplr(Yv)
    Nv = q * Yv - p * np.fliplr(Yr)
    viol = int((Nr % D != 0).sum() + (Nv % D != 0).sum())
    return Nr // D, Nv // D, viol


def estimate_pq(Yr, Yv, q_max: int = 12):
    """Blind rational-grid search. Returns ((p, q), score_tuple)."""
    Yr = np.asarray(Yr).astype(np.int64)
    Yv = np.asarray(Yv).astype(np.int64)
    best = None
    for q in range(1, q_max + 1):
        for p in range(0, q):
            if gcd(p, q) != 1:
                continue
            Sr, Sv, viol = unmix_exact(Yr, Yv, p, q)
            neg = int((Sr < 0).sum() + (Sv < 0).sum())
            cross = int(np.abs(Sr * np.fliplr(Sv)).sum())
            score = (viol, neg, cross)
            if best is None or score < best[1]:
                best = ((p, q), score)
    return best
