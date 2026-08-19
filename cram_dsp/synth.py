"""Deterministic synthetic evidence generators (integers only, seeded)."""

import numpy as np


def rng(seed: int = 2026):
    return np.random.default_rng(seed)


# ---------------------------------------------------------------------------
# Faint-ink palimpsest page
# ---------------------------------------------------------------------------

def make_faint_page(seed: int = 2026):
    """Piecewise-flat aged substrate with:
      - posterization plateaus (historical requantization steps of +4),
      - a delta=+1 faint undertext (below display contrast),
      - a delta=+11 decoy stroke (single-lane blind spot for sigma-11),
      - a delta=+12 decoy stroke.
    Returns img, masks dict, and the true edge masks (horizontal axis)."""
    H, W = 96, 128
    img = np.full((H, W), 180, dtype=np.int64)
    for c in (32, 64, 96):
        img[:, c:] += 4                      # plateau steps of +4

    ink = np.zeros((H, W), dtype=bool)       # delta = +1 undertext strokes
    ink[20:24, 10:50] = True
    ink[30:70, 40:44] = True
    ink[50:54, 70:120] = True
    for t in range(30):                      # diagonal stroke
        ink[60 + t // 3, 12 + t] = True
    img[ink] += 1

    d11 = np.zeros((H, W), dtype=bool)
    d11[8:12, 5:60] = True
    img[d11] += 11

    d12 = np.zeros((H, W), dtype=bool)
    d12[84:88, 60:120] = True
    img[d12] += 12

    def h_edges(mask):
        e = np.zeros((H, W - 1), dtype=bool)
        e |= mask[:, 1:] ^ mask[:, :-1]
        return e

    return img, {"ink": ink, "d11": d11, "d12": d12}, {
        "ink": h_edges(ink), "d11": h_edges(d11), "d12": h_edges(d12)
    }


# ---------------------------------------------------------------------------
# Codex strata page (KELD ground truth)
# ---------------------------------------------------------------------------

def make_codex_page(seed: int = 2026):
    """Regions drawn per KELD band k (values sampled inside [36k, 36k+35]):
    0 carbon outline, 2 cinnabar, 3 Maya blue, 5 gesso ground."""
    r = rng(seed)
    H, W = 96, 128
    K_true = np.full((H, W), 5, dtype=np.int64)          # gesso ground
    K_true[10:40, 10:60] = 3                             # blue field
    K_true[15:35, 75:115] = 2                            # red header
    K_true[55:85, 20:100] = 3
    K_true[60:80, 30:90] = 0                             # carbon glyphs
    jitter = r.integers(0, 36, size=(H, W))
    img = 36 * K_true + jitter
    return img.astype(np.int64), K_true


# ---------------------------------------------------------------------------
# Recto-verso bleed pair
# ---------------------------------------------------------------------------

def _text_layer(r, H, W, n_strokes: int, lo: int = 30, hi: int = 60):
    S = np.zeros((H, W), dtype=np.int64)
    for _ in range(n_strokes):
        i = int(r.integers(4, H - 8))
        j = int(r.integers(4, W - 30))
        ln = int(r.integers(12, 26))
        v = int(r.integers(lo, hi))
        S[i:i + 3, j:j + ln] = v
    return S


def make_bleed_pair(seed: int = 2026, p: int = 3, q: int = 8):
    r = rng(seed)
    H, W = 96, 128
    Sr = _text_layer(r, H, W, 14)
    Sv = _text_layer(r, H, W, 14)
    from .unmix import mix
    Yr, Yv = mix(Sr, Sv, p, q)
    return Sr, Sv, Yr, Yv, (p, q)


# ---------------------------------------------------------------------------
# Splice (different requantization histories) and copy-move
# ---------------------------------------------------------------------------

def _plateau_field(r, H, W, step: int, cell: int = 8, amp: int = 12):
    low = r.integers(0, amp, size=(H // cell, W // cell)).astype(np.int64)
    up = np.kron(low, np.ones((cell, cell), dtype=np.int64))
    return 120 + step * up


def make_splice(seed: int = 2026, step_bg: int = 4, step_fg: int = 5):
    r = rng(seed)
    H, W = 96, 128
    bg = _plateau_field(r, H, W, step_bg)
    fg = _plateau_field(rng(seed + 1), H, W, step_fg)
    img = bg.copy()
    mask = np.zeros((H, W), dtype=bool)
    mask[30:78, 50:114] = True          # deliberately off the 16px block grid
    img[mask] = fg[mask]
    return img, mask


def make_copy_move(seed: int = 2026):
    r = rng(seed)
    H, W = 96, 128
    img = r.integers(60, 200, size=(H, W)).astype(np.int64)
    src = (np.s_[10:34, 12:36])
    dst = (np.s_[60:84, 80:104])
    img[dst] = img[src]
    truth = np.zeros((H, W), dtype=bool)
    truth[src] = True
    truth[dst] = True
    return img, truth
