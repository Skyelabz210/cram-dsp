"""NODE-ARC04 — integer separation and survivability metrics.

All ratios are exact integer milli-units (x1000, floor). No float anywhere:
a metric that rounds is a metric that can be argued with.
"""

import numpy as np


def milli(num: int, den: int) -> int:
    """floor(1000 * num / den), exact integer."""
    if den == 0:
        return 0
    return (1000 * int(num)) // int(den)


def fmt_milli(v: int) -> str:
    return f"{v // 1000}.{abs(v) % 1000:03d}"


def region_stats(img, mask):
    a = np.asarray(img).astype(np.int64)
    m = np.asarray(mask, dtype=bool)
    sel = a[m]
    if sel.size == 0:
        return {"n": 0, "mean_milli": 0, "min": 0, "max": 0, "spread": 0}
    return {"n": int(sel.size),
            "mean_milli": milli(int(sel.sum()), int(sel.size)),
            "min": int(sel.min()), "max": int(sel.max()),
            "spread": int(sel.max()) - int(sel.min())}


def contrast_milli(img, fg_mask, bg_mask) -> int:
    """Separation of foreground from background, in exact milli-units of the
    background spread. Positive = foreground is darker than background."""
    f = region_stats(img, fg_mask)
    b = region_stats(img, bg_mask)
    if f["n"] == 0 or b["n"] == 0:
        return 0
    gap = b["mean_milli"] - f["mean_milli"]
    denom = max(b["spread"], 1)
    return gap // denom


def distinct_levels(img) -> int:
    return int(np.unique(np.asarray(img).astype(np.int64)).size)


def lattice_intact(img, step: int) -> tuple:
    """(values_on_lattice, total) — how much of the source quantisation
    structure survives an operation."""
    a = np.asarray(img).astype(np.int64)
    return int((a % step == 0).sum()), int(a.size)


def unit_delta_count(img, lanes) -> int:
    """Count of exact +/-1 horizontal steps found residue-natively."""
    from .core import selective_delta
    return int(selective_delta(img, (1, -1), lanes=lanes).sum())
