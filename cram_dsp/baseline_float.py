"""QUARANTINED classical baselines. Floating point BY DESIGN.

These are the comparison foils (the classical methods CRAM-DF is measured
against): float PCA blind separation, Sobel gradient magnitude, and a float
Gaussian blur. Nothing here is on a CRAM-DF production path, and this file is
excluded from the A1 lint by name — the same quarantine discipline as the
reconstruction-RNS foil in cramlab.
"""

import numpy as np


def pca_separate_2ch(Yr, Yv_flipped):
    """Classical 2-channel PCA blind separation (float)."""
    X = np.stack([np.asarray(Yr, dtype=np.float64).ravel(),
                  np.asarray(Yv_flipped, dtype=np.float64).ravel()])
    Xc = X - X.mean(axis=1, keepdims=True)
    C = Xc @ Xc.T / Xc.shape[1]
    _, vecs = np.linalg.eigh(C)
    comps = vecs.T @ Xc
    return comps.reshape(2, *np.asarray(Yr).shape)


def best_fit_mae(comp, truth):
    """Best affine fit of a float component to integer ground truth, MAE."""
    c = comp.astype(np.float64).ravel()
    t = np.asarray(truth, dtype=np.float64).ravel()
    A = np.stack([c, np.ones_like(c)]).T
    coef, *_ = np.linalg.lstsq(A, t, rcond=None)
    fit = A @ coef
    return float(np.abs(fit - t).mean())


def pca_best_mae(Yr, Yv, Sr, Sv):
    comps = pca_separate_2ch(Yr, np.fliplr(np.asarray(Yv)))
    maes = []
    for truth in (Sr, Sv):
        maes.append(min(best_fit_mae(comps[0], truth),
                        best_fit_mae(comps[1], truth)))
    return maes


def pca_best_mae_milli(Yr, Yv, Sr, Sv):
    """Same, returned as exact integer milli-MAE (the float lives here only)."""
    return [int(round(m * 1000)) for m in pca_best_mae(Yr, Yv, Sr, Sv)]


def sobel_mag(img):
    a = np.asarray(img, dtype=np.float64)
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    ky = kx.T
    def conv(a, k):
        H, W = a.shape
        pad = np.pad(a, 1, mode="edge")
        out = np.zeros_like(a)
        for i in range(3):
            for j in range(3):
                out += k[i, j] * pad[i:i + H, j:j + W]
        return out
    gx, gy = conv(a, kx), conv(a, ky)
    return np.hypot(gx, gy)


def blur_round_int(img, sigma_px: float = 1.0):
    """The classical pipeline in one call: float Gaussian blur, then round back
    to integers. This is the operation that irreversibly erases exact forensic
    structure (quantization fingerprints, unit-delta strokes)."""
    return np.rint(gaussian_blur_float(img, sigma_px)).astype(np.int64)


def gaussian_blur_float(img, sigma_px: float = 1.0):
    """Separable float Gaussian — used to demonstrate fingerprint erasure."""
    a = np.asarray(img, dtype=np.float64)
    radius = max(1, int(3 * sigma_px))
    xs = np.arange(-radius, radius + 1, dtype=np.float64)
    k = np.exp(-(xs ** 2) / (2 * sigma_px ** 2))
    k /= k.sum()
    pad = np.pad(a, ((0, 0), (radius, radius)), mode="edge")
    h = np.zeros_like(a)
    for i, w in enumerate(k):
        h += w * pad[:, i:i + a.shape[1]]
    pad = np.pad(h, ((radius, radius), (0, 0)), mode="edge")
    out = np.zeros_like(a)
    for i, w in enumerate(k):
        out += w * pad[i:i + a.shape[0], :]
    return out


# ---------------------------------------------------------------------------
# NODE-ARC05 — the incumbent manuscript renderers, implemented faithfully from
# their published recipes (Easton / Knox / Christens-Barry). FLOAT BY DESIGN.
# These are the comparison foils; they are quarantined from the A1 lint and
# are run at their best plausible settings, never strawmanned.
# ---------------------------------------------------------------------------

def knox_pseudocolor(red_band, uv_band):
    """Knox pseudocolor: tungsten/red image -> R; UV-blue -> G and B."""
    r = _stretch8(red_band)
    u = _stretch8(uv_band)
    return np.dstack([r, u, u])


def sharpie_subtract(band_a, band_b, gain: float = 1.0):
    """The 'Sharpie' path: band subtraction. Sharper undertext -- and, as the
    authors concede, it also amplifies whatever noise is present."""
    a = np.asarray(band_a).astype(np.float64)
    b = np.asarray(band_b).astype(np.float64)
    return np.rint(np.clip(gain * (a - b), -32768, 32767)).astype(np.int64)


def pca_render(bands):
    """PCA on the band cube; first component returned as an 8-bit render."""
    X = np.stack([np.asarray(b).astype(np.float64).ravel() for b in bands])
    X = X - X.mean(axis=1, keepdims=True)
    cov = np.cov(X)
    w, v = np.linalg.eigh(cov)
    pc = v[:, np.argmax(w)]
    proj = pc @ X
    return _stretch8(proj.reshape(np.asarray(bands[0]).shape))


def _stretch8(a):
    a = np.asarray(a).astype(np.float64)
    lo, hi = np.percentile(a, 1), np.percentile(a, 99)
    if hi - lo < 1e-9:
        hi = lo + 1.0
    return np.clip((a - lo) * 255.0 / (hi - lo), 0, 255).astype(np.uint8)
