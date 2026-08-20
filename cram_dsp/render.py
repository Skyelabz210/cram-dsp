"""NODE-ARC06 — exact renderers. Every emitted value is an exact function of
measured input; nothing is generated, smoothed, or invented. Where a display
step needs a division it happens once, at the emission seam, and is receipted.
"""

import numpy as np

from .core import keld_map, selective_delta, sigma, STAR16
from .transforms import emit_round_div


def band_difference_exact(band_a, band_b):
    """Exact integer band difference — the incumbent 'Sharpie' idea without
    the float. Returns (numerator, denominator=1): no information discarded,
    fully reversible given either input band."""
    a = np.asarray(band_a).astype(np.int64)
    b = np.asarray(band_b).astype(np.int64)
    return a - b, 1


def keld_composite(band, track=STAR16):
    """Exact stratification: band index floor(L/M) read from a residue pair."""
    return keld_map(np.asarray(band).astype(np.int64), track)


def lane_class_map(band, p: int):
    """Residue class of every pixel on lane p — an exact partition of the
    image into p classes. Not a threshold, not a gradient: a class label."""
    return sigma(np.asarray(band).astype(np.int64), p)


def undertext_probe(band, lanes):
    """Residue-native unit-step probe. The difference is never materialised;
    detection happens as simultaneous equality tests inside the lanes."""
    return selective_delta(np.asarray(band).astype(np.int64), (1, -1), lanes=lanes)


def emit_display(num, den: int = 1):
    """The single sanctioned rounding division, at the display seam only."""
    return emit_round_div(num, den) if den != 1 else np.asarray(num)
